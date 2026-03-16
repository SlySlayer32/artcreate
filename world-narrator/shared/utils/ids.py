import uuid


def new_id(prefix: str) -> str:
    """Generate a stable id with a prefix."""

    return f"{prefix}_{uuid.uuid4().hex}"
