"""Optional dependency guards for benchmark module."""

from __future__ import annotations


def cogames_available() -> bool:
    """Check if cogames package is installed."""
    try:
        import cogames  # noqa: F401
        return True
    except ImportError:
        return False


def mettagrid_available() -> bool:
    """Check if mettagrid package is installed."""
    try:
        import mettagrid  # noqa: F401
        return True
    except ImportError:
        return False


def require_cogames():
    """Raise ImportError with install instructions if cogames is missing."""
    if not cogames_available():
        raise ImportError(
            "cogames is required for benchmark mode. "
            "Install with: pip install cogames"
        )


def require_mettagrid():
    """Raise ImportError with install instructions if mettagrid is missing."""
    if not mettagrid_available():
        raise ImportError(
            "mettagrid is required for benchmark mode. "
            "Install with: pip install mettagrid"
        )
