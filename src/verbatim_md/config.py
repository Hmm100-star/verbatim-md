"""Small, strictly validated offline formatting profiles."""
from dataclasses import asdict, dataclass, fields
from pathlib import Path
import math


@dataclass(frozen=True)
class Profile:
    font_name: str = "Arial"
    font_size: float = 11
    small_size: float = 8
    highlight_color: str = "yellow"
    shrink_unread: bool = False
    margin_inches: float = 1


BUILTINS = {"default": Profile(), "ld": Profile(font_size=12, small_size=8)}


def load_profile(name_or_path: str | Path | Profile | None = None) -> Profile:
    if isinstance(name_or_path, Profile):
        data = asdict(name_or_path)
    elif name_or_path is None or str(name_or_path) in BUILTINS:
        return BUILTINS[str(name_or_path or "default")]
    else:
        from .parser import load_yaml
        path = Path(name_or_path)
        if path.stat().st_size > 65536:
            raise ValueError("profile exceeds 64 KiB")
        data = load_yaml(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("profile must be a YAML mapping")
    allowed = {f.name for f in fields(Profile)}
    if set(data) - allowed:
        raise ValueError(f"unknown profile fields: {sorted(set(data) - allowed)}")
    profile = Profile(**data)
    if (not isinstance(profile.font_name, str) or not profile.font_name.strip()
            or any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF or ord(c) in (0xFFFE, 0xFFFF)
                   for c in profile.font_name)):
        raise ValueError("font_name must be nonempty text")
    if type(profile.shrink_unread) is not bool:
        raise ValueError("shrink_unread must be true or false")
    for name, low, high in (("font_size", 1, 72), ("small_size", 1, 72),
                            ("margin_inches", .1, 3)):
        value = getattr(profile, name)
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"{name} must be between {low} and {high}")
    for name in ('font_size', 'small_size'):
        if getattr(profile, name) * 2 != int(getattr(profile, name) * 2):
            raise ValueError(f'{name} must use Word half-point increments (for example 11 or 11.5)')
    if profile.small_size > profile.font_size:
        raise ValueError("small_size cannot exceed font_size")
    if not isinstance(profile.highlight_color, str) or profile.highlight_color not in {"yellow", "green", "cyan", "magenta", "blue", "red", "darkYellow", "lightGray"}:
        raise ValueError("unsupported highlight_color")
    return profile
