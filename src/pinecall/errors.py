"""Every error this package raises, under one root."""


class PinecallError(Exception):
    """The root of every error this package raises: `except PinecallError` catches them all."""


class WireError(PinecallError):
    """A frame, an entry or a body that does not fit its shape: an unknown type, an undeclared key.

    The wire is closed, so a key nobody declared means the gateway speaks a newer wire than this
    package: update it.
    """


class DeclarationRefused(PinecallError):
    """A class declares something the gateway would refuse; raised when the class is created."""


class UnauthoredWrite(PinecallError):
    """A state field was assigned outside a tool and outside a hook."""

    def __init__(self, field: str) -> None:
        """Name the field that was written."""
        super().__init__(
            f"state field {field} was assigned outside a tool and outside a lifecycle hook; "
            "tools are the only writers of state"
        )


class NotAStage(PinecallError):
    """The stage was set to a value the class's `stage` Literal does not hold."""


class ToolFailed(PinecallError):
    """A tool could not run; the message goes back to the model as the tool's error."""
