"""Failures exposed to SDK consumers, independent of the HTTP server."""


class TransfermarktError(Exception):
    """Base class for failures fetching or assembling Transfermarkt data."""

    def __init__(self, message: str, *, url: str | None = None, status_code: int | None = None) -> None:
        """Attach upstream request metadata when available."""
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class NotFound(TransfermarktError):
    """The requested entity does not exist upstream."""


class UpstreamBlocked(TransfermarktError):
    """Upstream challenged or refused the request."""


class UpstreamTimeout(TransfermarktError):
    """An upstream request timed out."""


class UpstreamError(TransfermarktError):
    """An upstream connection, response or assembled model was invalid."""


class EndpointUnavailable(TransfermarktError):
    """There is no upstream data source for this endpoint."""
