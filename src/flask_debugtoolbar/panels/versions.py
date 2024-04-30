import importlib.metadata
import os
from sysconfig import get_path

from . import DebugPanel

flask_version = importlib.metadata.version("flask")


class VersionDebugPanel(DebugPanel):
    """Panel that displays the Flask version."""

    name = "Version"
    has_content = True

    def nav_title(self):
        return "Versions"

    def nav_subtitle(self):
        return f"Flask {flask_version}"

    def url(self):
        return ""

    def title(self):
        return "Versions"

    def content(self):
        packages_metadata = [p.metadata for p in importlib.metadata.distributions()]
        packages = sorted(packages_metadata, key=lambda p: p["Name"].lower())
        return self.render(
            "panels/versions.html",
            {
                "packages": packages,
                "python_lib_dir": os.path.normpath(get_path("platlib")),
            },
        )
