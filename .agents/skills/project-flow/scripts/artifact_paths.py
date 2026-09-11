"""Resolve organized and legacy Project Flow artifacts without following links."""

from pathlib import Path
from uuid import UUID


def checked_path(path: Path, *, root: Path | None = None) -> Path:
    absolute = path.absolute()
    boundary = root.absolute() if root is not None else absolute.parent
    for component in (absolute, *absolute.parents):
        if component.is_symlink() or (hasattr(component, "is_junction") and component.is_junction()):
            raise ValueError("artifact paths must not traverse symlinks or junctions")
        if component == boundary:
            break
    else:
        raise ValueError("artifact path is outside the checked root")
    return absolute.resolve()


def artifact_root(path: Path) -> Path:
    """Paths in state remain relative to the item/scope, including candidates."""
    parent = path.absolute().parent
    root = parent
    parts = path.absolute().parts
    anchors = [index for index in range(len(parts) - 4) if parts[index:index + 2] == ("docs", "harness") and parts[index + 2] in {"features", "bugs", "scopes", ".runs"}]
    if anchors:
        root = Path(*parts[:anchors[-1] + 4])
    elif parent.name in {".flow", ".work"}:
        root = parent.parent
    elif parent.parent.name == "publications" and parent.parent.parent.name in {".flow", ".work"}:
        UUID(parent.name)
        root = parent.parent.parent.parent
    checked_path(path, root=root)
    return root.resolve()


def contained_path(root: Path, value: str) -> Path:
    relative = Path(value)
    if relative.anchor or ".." in relative.parts or "\\" in value or ":" in value:
        raise ValueError("artifact reference must be a contained relative path")
    root = checked_path(root)
    target = checked_path(root / relative, root=root)
    if target != root and root not in target.parents:
        raise ValueError("artifact reference escapes its root")
    return target


def relocated_path(path: Path) -> Path:
    """Resolve explicitly recorded historical paths after a local migration."""
    from artifact_layout import resolve_path

    return resolve_path(path)
