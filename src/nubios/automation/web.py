from __future__ import annotations

from urllib.parse import urlparse
import webbrowser

from ..core.permissions import Permission
from ..core.permissions import PermissionManager


class WebService:
    """Network boundary: opening a URL is local; searching requires explicit web permission."""

    def __init__(self, permissions: PermissionManager) -> None:
        self.permissions = permissions

    def open_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Only valid HTTP(S) URLs are allowed")
        webbrowser.open(url)

    def search(self, query: str) -> str:
        if not self.permissions.check(Permission.WEB_ACCESS):
            raise PermissionError("Permission denied: web.access")
        self.open_url("https://www.google.com/search?q=" + query.replace(" ", "+"))
        return "Opened a web search in your browser."
