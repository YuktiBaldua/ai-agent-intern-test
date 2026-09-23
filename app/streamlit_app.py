import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from app.agent import SupportAgent

st.set_page_config(
    page_title="Aster & Row Support",
    page_icon="💬",
    layout="centered",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #f7f7f5;
    }

    .title {
        font-size: 30px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #6b7280;
        margin-bottom: 25px;
    }

    .source-box {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 10px;
    }

    .handoff {
        background: #fff7ed;
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">Aster & Row Support</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered customer support assistant</div>',
    unsafe_allow_html=True,
)

if "agent" not in st.session_state:
    st.session_state.agent = SupportAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(
                        f"**{source['heading']}**  \n"
                        f"`{source['filename']}`"
                    )

        if message.get("handoff"):
            st.warning("Human handoff recommended.")

user_message = st.chat_input("Ask about orders, returns, or product support...")

if user_message:
    st.session_state.messages.append(
        {"role": "user", "content": user_message}
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.agent.answer(user_message)

        st.markdown(result["answer"])

        if result.get("sources"):
            with st.expander("📚 Sources"):
                for source in result["sources"]:
                    st.write(
                        f"**{source['heading']}**  \n"
                        f"`{source['filename']}`"
                    )

        if result.get("handoff"):
            st.warning("Human handoff recommended.")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "handoff": result.get("handoff", False),
        }
    )
