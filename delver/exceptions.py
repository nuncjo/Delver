# -*- coding:utf-8 -*-


class GeneralError(Exception):
    """General error"""


class SessionError(GeneralError):
    """Raised on errors related to session usage."""


class HistoryError(GeneralError):
    """Raised when functionality needs history=True."""


class FlowError(GeneralError):
    """Raised on errors related to flow usage."""


class CrawlerError(GeneralError):
    """Raised on errors related to crawler usage."""
