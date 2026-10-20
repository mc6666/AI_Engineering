"""Command-line entry point: ``python -m matplotlib_designer.main``."""
from __future__ import annotations

import sys

from .app import run


def main() -> None:
    """Launch the application and exit the process with its return code."""
    sys.exit(run())


if __name__ == "__main__":
    main()
