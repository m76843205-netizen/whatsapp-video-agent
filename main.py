from dotenv import load_dotenv
from agent.core import AgentCore


def main():
    load_dotenv()

    print("NEXUS AI starting...")

    try:
        agent = AgentCore()
        print("Groq Brain: ONLINE")
    except Exception as error:
        print(f"Startup Error: {error}")
        return

    while True:
        try:
            message = input("\nYou: ").strip()

            if message.lower() in ("exit", "quit"):
                print("NEXUS offline.")
                break

            if not message:
                continue

            print("\nNEXUS:", agent.ask(message))

        except KeyboardInterrupt:
            print("\nNEXUS offline.")
            break
        except Exception as error:
            print(f"\nAgent Error: {error}")


if __name__ == "__main__":
    main()
