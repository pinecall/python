"""Every error this package raises, under one root."""


class PinecallError(Exception):
    """The root of every error this package raises: `except PinecallError` catches them all."""


class WireError(PinecallError):
    """A frame, an entry or a body that does not fit its shape: an unknown type, an undeclared key.

    The wire is closed, so a key nobody declared means the gateway speaks a newer wire than this
    package: update it.
    """
