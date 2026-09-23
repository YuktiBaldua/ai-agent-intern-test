from app.agent import SupportAgent


RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"


def print_header() -> None:
    print("\033[2J\033[H", end="")
    print(f"{BOLD}{CYAN}")
    print("╔══════════════════════════════════════════════════════╗")
    print("║              ASTER & ROW SUPPORT AGENT              ║")
    print("║          AI-Powered Customer Support Assistant       ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"{DIM}Ask about returns, orders, policies, or product support.")
    print("Type 'exit' to end the session.{RESET}\n")


def main() -> None:
    agent = SupportAgent()
    print_header()

    while True:
        try:
            user_message = input(f"{BOLD}{CYAN}You › {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break

        if user_message.lower() in {"exit", "quit"}:
            print(f"\n{DIM}Session ended. Goodbye!{RESET}")
            break

        if not user_message:
            continue

        print(f"{DIM}Agent is thinking...{RESET}")

        result = agent.answer(user_message)

        print(f"\n{BOLD}{GREEN}Agent ›{RESET}")
        print(result["answer"])

        if result.get("sources"):
            print(f"\n{BOLD}{CYAN}Sources{RESET}")
            print(f"{DIM}{'─' * 55}{RESET}")
            for source in result["sources"]:
                heading = source.get("heading", "")
                filename = source.get("filename", "")
                print(f"  • {heading}")
                print(f"    {DIM}{filename}{RESET}")

        if result.get("tool_calls"):
            print(f"\n{BOLD}{CYAN}Tool Calls{RESET}")
            print(f"{DIM}{'─' * 55}{RESET}")
            for call in result["tool_calls"]:
                tool = call.get("tool", "unknown")
                order_id = call.get("order_id")
                if order_id:
                    print(f"  • {tool} → {order_id}")
                else:
                    print(f"  • {tool}")

        if result.get("handoff"):
            print(
                f"\n{BOLD}{YELLOW}⚠ Human handoff recommended{RESET}"
            )

        print(f"\n{DIM}{'═' * 55}{RESET}\n")


if __name__ == "__main__":
    main()
