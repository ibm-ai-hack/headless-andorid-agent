import os
import logging

from twilio.rest import Client

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_twilio_client() -> Client:
    global _client
    if _client is None:
        _client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ.get("TWILIO_AUTH_TOKEN", ""),
        )
    return _client


def send_sms(to: str, body: str) -> str:
    client = get_twilio_client()
    from_number = os.environ["TWILIO_PHONE_NUMBER"]

    # Split long messages
    chunks = _split(body, 1500)
    sids = []
    for chunk in chunks:
        msg = client.messages.create(body=chunk, from_=from_number, to=to)
        sids.append(msg.sid)
        logger.info("Sent SMS %s to %s (%d chars)", msg.sid, to, len(chunk))

    return sids[0] if sids else ""


def _split(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        idx = text.rfind("\n", 0, max_len)
        if idx == -1:
            idx = text.rfind(" ", 0, max_len)
        if idx == -1:
            idx = max_len
        chunks.append(text[:idx])
        text = text[idx:].lstrip()
    return chunks
