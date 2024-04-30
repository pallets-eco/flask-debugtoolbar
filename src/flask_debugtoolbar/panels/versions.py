from __future__ import annotations

import importlib.metadata
import os
from sysconfig import get_path

from . import DebugPanel

flask_version: str = importlib.metadata.version("flask")


class VersionDebugPanel(DebugPanel):
    """Panel that displays the Flask version."""

    name = "Version"
    has_content = True

    def nav_title(self) -> str:
        return "Versions"

    def nav_subtitle(self) -> str:
        return f"Flask {flask_version}"

    def url(self) -> str:
        return ""

    def title(self) -> str:
        return "Versions"

    def content(self) -> str:
        packages_metadata = [p.metadata for p in importlib.metadata.distributions()]
        packages = sorted(packages_metadata, key=lambda p: p["Name"].lower())
        return self.render(
            "panels/versions.html",
            {
                "packages": packages,
                "python_lib_dir": os.path.normpath(get_path("platlib")),
            },
        )
