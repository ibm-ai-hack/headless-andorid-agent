import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("buckeyebot")


def main():
    from agent import create_agent
    from sms.webhook import app, set_agent_handler

    agent = create_agent()
    logger.info("BuckeyeBot agent initialized")

    # Per-user conversation memory (phone number -> list of messages)
    conversations: dict[str, list] = {}

    async def handle_message(text: str, from_number: str) -> str:
        try:
            response = await agent.run(text)
            return response.last_message.text
        except Exception as e:
            logger.exception("Agent error")
            return f"Sorry, I ran into an error: {type(e).__name__}. Please try again."

    set_agent_handler(handle_message)

    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting BuckeyeBot on port %d", port)
    logger.info("Configure your Twilio webhook to POST to: http://<your-host>:%d/sms", port)

    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
