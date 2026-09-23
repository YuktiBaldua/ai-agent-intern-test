from pathlib import Path
import re
from typing import List

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import DocumentChunk


class KnowledgeBase:
    def __init__(self, knowledge_base_dir: str = "knowledge-base"):
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.chunks: List[DocumentChunk] = []

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )

        self.matrix = None

    def load(self) -> None:
        self.chunks.clear()

        for path in sorted(self.knowledge_base_dir.glob("*.md")):
            self._load_document(path)

        if not self.chunks:
            raise RuntimeError("No knowledge-base documents were found.")

        indexed_text = [
            f"{chunk.heading}. {chunk.content}"
            for chunk in self.chunks
        ]

        self.matrix = self.vectorizer.fit_transform(indexed_text)

    def _load_document(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        metadata, body = self._parse_front_matter(text)

        sections = self._split_into_sections(body)

        for heading, content in sections:
            if not content.strip():
                continue

            self.chunks.append(
                DocumentChunk(
                    filename=path.name,
                    document_id=str(metadata.get("document_id", "")),
                    title=str(metadata.get("title", "")),
                    status=str(metadata.get("status", "")),
                    effective_date=str(metadata.get("effective_date", "")),
                    audience=str(metadata.get("audience", "")),
                    policy_authority=str(
                        metadata.get("policy_authority", "")
                    ),
                    heading=heading,
                    content=content.strip(),
                    metadata=metadata,
                )
            )

    @staticmethod
    def _parse_front_matter(text: str) -> tuple[dict, str]:
        text = text.lstrip()

        if not text.startswith("---"):
            return {}, text

        parts = text.split("---", 2)

        if len(parts) != 3:
            return {}, text

        metadata = yaml.safe_load(parts[1]) or {}
        body = parts[2]

        if not isinstance(metadata, dict):
            metadata = {}

        return metadata, body

    @staticmethod
    def _split_into_sections(body: str) -> list[tuple[str, str]]:
        lines = body.splitlines()

        sections: list[tuple[str, list[str]]] = []
        current_heading = "Document overview"
        current_content: list[str] = []

        for line in lines:
            heading_match = re.match(
                r"^(#{1,6})\s+(.+?)\s*$",
                line,
            )

            if heading_match:
                if current_content:
                    sections.append(
                        (current_heading, current_content)
                    )

                current_heading = heading_match.group(2)
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections.append(
                (current_heading, current_content)
            )

        return [
            (heading, "\n".join(content).strip())
            for heading, content in sections
            if "\n".join(content).strip()
        ]

    @staticmethod
    def _authority_score(chunk: DocumentChunk) -> float:
        """
        Higher score = more authoritative for customer answers.

        Active official customer documents are preferred.
        Superseded, draft, internal, and non-authoritative documents
        are strongly penalized.
        """
        score = 0.0

        if chunk.status == "active":
            score += 5.0
        elif chunk.status == "superseded":
            score -= 8.0
        elif chunk.status == "draft":
            score -= 10.0

        if chunk.audience == "customer":
            score += 3.0
        elif chunk.audience == "internal":
            score -= 6.0

        if chunk.policy_authority == "official":
            score += 4.0
        elif chunk.policy_authority == "none":
            score -= 5.0

        return score

    @staticmethod
    def _keyword_boost(query: str, chunk: DocumentChunk) -> float:
        """
        Small deterministic boosts for important domain concepts.

        TF-IDF handles general relevance. These boosts help distinguish
        closely related policies such as:
        - standard returns vs TrailPlus returns
        - international shipping vs returns
        - product-care conflicts

        The boost is intentionally small so keyword matching cannot
        completely override semantic relevance.
        """
        query_lower = query.lower()
        text = f"{chunk.heading} {chunk.content}".lower()

        boost = 0.0

        # ---------------------------------------------------------
        # Return-policy intent
        # ---------------------------------------------------------
        return_terms = [
            "return",
            "returns",
            "return window",
            "days of delivery",
        ]

        if any(term in query_lower for term in return_terms):
            if "return" in chunk.heading.lower():
                boost += 0.08

        # ---------------------------------------------------------
        # Standard return intent
        # ---------------------------------------------------------
        standard_terms = [
            "regular customer",
            "standard customer",
            "standard plan",
            "normal customer",
            "unused backpack",
            "unused item",
        ]

        if any(term in query_lower for term in standard_terms):
            if (
                "standard" in chunk.heading.lower()
                or "standard plan" in text
            ):
                boost += 0.20

        # ---------------------------------------------------------
        # TrailPlus intent
        # ---------------------------------------------------------
        trailplus_terms = [
            "trailplus",
            "trail plus",
            "membership",
            "member return",
        ]

        if any(term in query_lower for term in trailplus_terms):
            if (
                "trailplus" in chunk.filename.lower()
                or "trailplus" in chunk.title.lower()
                or "trailplus" in chunk.heading.lower()
                or "trail plus" in chunk.title.lower()
                or "trail plus" in chunk.heading.lower()
            ):
                boost += 0.20
        # ---------------------------------------------------------
        # International shipping intent
        # ---------------------------------------------------------
        international_terms = [
            "international",
            "ship internationally",
            "shipping to",
            "shipping country",
            "canada",
            "germany",
            "delivery country",
            "duties",
            "taxes",
        ]

        if any(term in query_lower for term in international_terms):
            if (
                "shipping" in chunk.heading.lower()
                or "international" in text
                or "supported destinations" in chunk.heading.lower()

            ):
                boost += 0.15

        # ---------------------------------------------------------
        # Warranty intent
        # ---------------------------------------------------------
        warranty_terms = [
            "warranty",
            "warranties",
            "covered for",
            "coverage period",
        ]

        if any(term in query_lower for term in warranty_terms):
            if "warranty" in chunk.heading.lower() or "warranty" in text:
                boost += 0.15

        # ---------------------------------------------------------
        # Damaged / wrong item intent
        # ---------------------------------------------------------
        damage_terms = [
            "damaged",
            "damage",
            "wrong item",
            "wrong product",
            "defective",
            "broken",
        ]

        if any(term in query_lower for term in damage_terms):
            if any(term in text for term in damage_terms):
                boost += 0.15

        # ---------------------------------------------------------
        # Product-care intent
        # ---------------------------------------------------------
        care_terms = [
            "dishwasher",
            "dishwasher safe",
            "wash",
            "washing",
            "care instructions",
            "clean",
            "cleaning",
        ]

        if any(term in query_lower for term in care_terms):
            if (
                "care" in chunk.heading.lower()
                or "dishwasher" in text
                or "care" in text
            ):
                boost += 0.15

        return boost

    @staticmethod
    def _is_active_authoritative(chunk: DocumentChunk) -> bool:
        return (
            chunk.status == "active"
            and chunk.audience == "customer"
            and chunk.policy_authority == "official"
        )

    def search(
        self,
        query: str,
        top_k: int = 6,
        customer_only: bool = True,
    ) -> list[dict]:
        """
        Retrieve relevant knowledge-base chunks.

        For normal customer questions:
        - prioritize relevance
        - prefer active official customer documents
        - exclude internal/draft/superseded material by default

        For conflict detection:
        - callers can use customer_only=True and inspect multiple
          active authoritative chunks returned for the same topic.
        """

        if self.matrix is None:
            self.load()

        if not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.matrix,
        ).flatten()

        candidates = []

        for index, similarity in enumerate(similarities):
            chunk = self.chunks[index]

            if customer_only and not self._is_active_authoritative(chunk):
                continue

            if similarity <= 0:
                is_destination_query = any(term in query.lower() for term in ["ship to", "shipping to", "ship orders to", "international shipping", "canada"]) and chunk.heading.lower() == "supported destinations"
                if not is_destination_query:
                    continue

            authority = self._authority_score(chunk)
            keyword_boost = self._keyword_boost(query, chunk)

            # Relevance remains the main signal.
            #
            # Authority prevents stale/unapproved material from
            # outranking current official policy.
            #
            # Keyword boost helps with known domain distinctions.
            final_score = (
                float(similarity)
                + (authority * 0.02)
                + keyword_boost
            )

            candidates.append(
                {
                    "chunk": chunk,
                    "similarity": float(similarity),
                    "authority_score": authority,
                    "keyword_boost": keyword_boost,
                    "score": final_score,
                }
            )

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return candidates[:top_k]

    def search_active_authoritative(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:
        """
        Retrieve multiple relevant active official customer sources.

        This is intentionally separate from normal search because
        genuine conflicts must be detected instead of silently choosing
        one source.

        Example:
        Breeze Tumbler may have relevant information in both:
        - 11-product-care.md
        - 12-breeze-tumbler-product-card.md

        Both should remain available for conflict inspection.
        """
        return self.search(
            query=query,
            top_k=top_k,
            customer_only=True,
        )
