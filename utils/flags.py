"""Country flag emoji → language name mapping for on-demand translation."""

from __future__ import annotations

# Regional indicator symbols map to ISO-like codes; we resolve to human language names.
FLAG_TO_LANGUAGE: dict[str, str] = {
    "🇺🇸": "English",
    "🇬🇧": "English",
    "🇦🇺": "English",
    "🇨🇦": "English (Canadian)",
    "🇪🇸": "Spanish",
    "🇲🇽": "Spanish",
    "🇦🇷": "Spanish",
    "🇫🇷": "French",
    "🇩🇪": "German",
    "🇮🇹": "Italian",
    "🇵🇹": "Portuguese",
    "🇧🇷": "Portuguese",
    "🇯🇵": "Japanese",
    "🇰🇷": "Korean",
    "🇨🇳": "Chinese (Simplified)",
    "🇹🇼": "Chinese (Traditional)",
    "🇷🇺": "Russian",
    "🇳🇱": "Dutch",
    "🇸🇪": "Swedish",
    "🇳🇴": "Norwegian",
    "🇩🇰": "Danish",
    "🇫🇮": "Finnish",
    "🇵🇱": "Polish",
    "🇹🇷": "Turkish",
    "🇬🇷": "Greek",
    "🇮🇳": "Hindi",
    "🇹🇭": "Thai",
    "🇻🇳": "Vietnamese",
    "🇮🇩": "Indonesian",
    "🇲🇾": "Malay",
    "🇵🇭": "Filipino",
    "🇺🇦": "Ukrainian",
    "🇨🇿": "Czech",
    "🇷🇴": "Romanian",
    "🇭🇺": "Hungarian",
    "🇸🇦": "Arabic",
    "🇮🇱": "Hebrew",
    "🇿🇦": "Afrikaans",
    "🇳🇬": "English",
    "🇵🇰": "Urdu",
    "🇧🇩": "Bengali",
}

# Language role name → target language (for onboarding & context menu defaults)
ROLE_TO_LANGUAGE: dict[str, str] = {
    "english": "English",
    "español": "Spanish",
    "spanish": "Spanish",
    "français": "French",
    "french": "French",
    "deutsch": "German",
    "german": "German",
    "italiano": "Italian",
    "italian": "Italian",
    "português": "Portuguese",
    "portuguese": "Portuguese",
    "日本語": "Japanese",
    "japanese": "Japanese",
    "한국어": "Korean",
    "korean": "Korean",
    "中文": "Chinese (Simplified)",
    "chinese": "Chinese (Simplified)",
    "русский": "Russian",
    "russian": "Russian",
    "nederlands": "Dutch",
    "dutch": "Dutch",
    "türkçe": "Turkish",
    "turkish": "Turkish",
    "العربية": "Arabic",
    "arabic": "Arabic",
    "हिन्दी": "Hindi",
    "hindi": "Hindi",
    "ไทย": "Thai",
    "thai": "Thai",
    "tiếng việt": "Vietnamese",
    "vietnamese": "Vietnamese",
}

# Onboarding button labels
ONBOARDING_LANGUAGES: list[tuple[str, str, str]] = [
    ("English", "🇺🇸", "english"),
    ("Español", "🇪🇸", "español"),
    ("Français", "🇫🇷", "français"),
    ("Deutsch", "🇩🇪", "deutsch"),
    ("Italiano", "🇮🇹", "italiano"),
    ("Português", "🇧🇷", "português"),
    ("日本語", "🇯🇵", "日本語"),
    ("한국어", "🇰🇷", "한국어"),
    ("中文", "🇨🇳", "中文"),
    ("Русский", "🇷🇺", "русский"),
    ("العربية", "🇸🇦", "العربية"),
    ("हिन्दी", "🇮🇳", "हिन्दी"),
]


def flag_to_language(emoji: str) -> str | None:
    """Return target language for a flag emoji, or None."""
    return FLAG_TO_LANGUAGE.get(emoji)


def resolve_language_name(name: str) -> str | None:
    """Resolve user-provided language string to canonical name."""
    if not name:
        return None
    key = name.strip().lower()
    if key in ROLE_TO_LANGUAGE:
        return ROLE_TO_LANGUAGE[key]
    for lang in set(FLAG_TO_LANGUAGE.values()) | set(ROLE_TO_LANGUAGE.values()):
        if lang.lower() == key or lang.lower().startswith(key):
            return lang
    return name.strip()  # pass through for Grok to interpret
