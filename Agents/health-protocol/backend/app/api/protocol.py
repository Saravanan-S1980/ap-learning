"""GET /api/protocol/{id} — retrieve a generated protocol by ID."""
from fastapi import APIRouter, HTTPException

from app.models.protocol import Protocol

router = APIRouter()

# In-memory store for MVP — keyed by protocol_id (UUID hex string).
# Production: replace with SQLite/PostgreSQL via ProtocolRecord ORM model.
_protocol_store: dict[str, Protocol] = {}


def save_protocol(protocol_id: str, protocol: Protocol) -> None:
    """Persist a protocol in the in-memory store."""
    _protocol_store[protocol_id] = protocol


def load_protocol(protocol_id: str) -> Protocol | None:
    """Retrieve a protocol by ID, or None if not found."""
    return _protocol_store.get(protocol_id)


@router.get("/protocol/{protocol_id}")
async def get_protocol(protocol_id: str) -> Protocol:
    protocol = load_protocol(protocol_id)
    if protocol is None:
        raise HTTPException(
            status_code=404,
            detail=f"Protocol '{protocol_id}' not found. "
                   "It may have expired (server restart clears in-memory store).",
        )
    return protocol
