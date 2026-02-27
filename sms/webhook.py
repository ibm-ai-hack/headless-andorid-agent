import asyncio
import logging

from flask import Flask, request, Response

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Set by main.py before starting the server
_agent_handler = None


def set_agent_handler(handler):
    """Register the async function that processes an SMS message and returns a reply."""
    global _agent_handler
    _agent_handler = handler


@app.route("/sms", methods=["POST"])
def incoming_sms():
    body = request.form.get("Body", "").strip()
    from_number = request.form.get("From", "")

    if not body:
        return _twiml_response("Please send a message and I'll help you out!")

    logger.info("SMS from %s: %s", from_number, body[:100])

    if _agent_handler is None:
        return _twiml_response("BuckeyeBot is starting up, please try again in a moment.")

    try:
        loop = asyncio.new_event_loop()
        reply = loop.run_until_complete(_agent_handler(body, from_number))
        loop.close()
    except Exception:
        logger.exception("Agent error processing message")
        reply = "Sorry, something went wrong. Please try again."

    return _twiml_response(reply)


def _twiml_response(message: str) -> Response:
    # Split long messages into multiple <Message> tags (SMS limit ~1600 chars)
    chunks = _split_message(message, max_len=1500)
    body = "<Response>"
    for chunk in chunks:
        escaped = chunk.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body += f"<Message>{escaped}</Message>"
    body += "</Response>"
    return Response(body, content_type="application/xml")


def _split_message(text: str, max_len: int = 1500) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Try to split on newline
        idx = text.rfind("\n", 0, max_len)
        if idx == -1:
            idx = text.rfind(" ", 0, max_len)
        if idx == -1:
            idx = max_len
        chunks.append(text[:idx])
        text = text[idx:].lstrip()
    return chunks
