from __future__ import annotations

from pathlib import Path


class SafeFileSystem:
    def __init__(self, allowed_directories: tuple[Path, ...]) -> None:
        self.allowed = tuple(p.resolve() for p in allowed_directories)

    def _validate(self, path: Path) -> Path:
        candidate = path.expanduser().resolve()
        if not any(candidate == root or root in candidate.parents for root in self.allowed):
            raise PermissionError("Path is outside configured allowed directories")
        return candidate

    def search(self, query: str, extension: str | None = None, limit: int = 50) -> list[Path]:
        query = query.casefold()
        ext = extension.casefold().lstrip(".") if extension else None
        results: list[Path] = []
        for root in self.allowed:
            if not root.is_dir():
                continue
            for path in root.rglob("*"):
                if not path.is_file() or query not in path.name.casefold():
                    continue
                if ext and path.suffix.casefold().lstrip(".") != ext:
                    continue
                results.append(path)
                if len(results) >= limit:
                    return results
        return results

    def open_file(self, path: Path) -> Path:
        return self._validate(path)

    def open_folder(self, path: Path) -> Path:
        candidate = self._validate(path)
        if not candidate.is_dir():
            raise NotADirectoryError(candidate)
        return candidate
