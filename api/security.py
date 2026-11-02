import hmac
import os

from fastapi import Header, HTTPException, status


def verify_agent_token(
    authorization: str | None = Header(default=None),
) -> None:
    expected_token = os.getenv("SYSADMIN_AGENT_TOKEN", "")

    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent authentication is not configured",
        )

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    scheme, separator, supplied_token = authorization.partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
        or not supplied_token
        or not hmac.compare_digest(
            supplied_token,
            expected_token,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent token",
        )