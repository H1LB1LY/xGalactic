"""Country flag emoji → language name mapping for on-demand translation."""

from __future__ import annotations

# Regional indicator symbols map to ISO-like codes; we resolve to human language names.
# Comprehensive flag → language mapping
# All 249 valid Discord regional indicator flags mapped to their primary language.
# If a flag is not mapped or is a multi-language country, it falls back gracefully.
FLAG_TO_LANGUAGE: dict[str, str] = {
    "🇦🇫": "persian", "🇦🇱": "albanian", "🇩🇿": "arabic", "🇦🇸": "english", "🇦🇩": "catalan",
    "🇦🇴": "português", "🇦🇮": "english", "🇦🇶": "english", "🇦🇬": "english", "🇦🇷": "español",
    "🇦🇲": "armenian", "🇦🇼": "dutch", "🇦🇨": "english", "🇦🇺": "english", "🇦🇹": "deutsch",
    "🇦🇿": "azerbaijani", "🇧🇸": "english", "🇧🇭": "arabic", "🇧🇩": "bengali", "🇧🇧": "english",
    "🇧🇾": "belarusian", "🇧🇪": "français", "🇧🇿": "english", "🇧🇯": "français", "🇧🇲": "english",
    "🇧🇹": "dzongkha", "🇧🇴": "español", "🇧🇦": "bosnian", "🇧🇼": "english", "🇧🇻": "norwegian",
    "🇧🇷": "português", "🇮🇴": "english", "🇻🇬": "english", "🇧🇳": "malay", "🇧🇬": "bulgarian",
    "🇧🇫": "français", "🇧🇮": "français", "🇰🇭": "khmer", "🇨🇲": "français", "🇨🇦": "english",
    "🇮🇨": "español", "🇨🇻": "português", "🇧🇶": "dutch", "🇰🇾": "english", "🇨🇫": "français",
    "🇹🇩": "français", "🇨🇱": "español", "🇨🇳": "chinese", "🇨🇽": "english", "🇨🇨": "english",
    "🇨🇴": "español", "🇰🇲": "français", "🇨🇬": "français", "🇨🇩": "français", "🇨🇰": "english",
    "🇨🇷": "español", "🇨🇮": "français", "🇭🇷": "croatian", "🇨🇺": "español", "🇨🇼": "dutch",
    "🇨🇾": "greek", "🇨🇿": "czech", "🇩🇰": "danish", "🇩🇯": "français", "🇩🇲": "english",
    "🇩🇴": "español", "🇪🇨": "español", "🇪🇬": "arabic", "🇸🇻": "español", "🇬🇶": "español",
    "🇪🇷": "tigrinya", "🇪🇪": "estonian", "🇪🇹": "amharic", "🇫🇰": "english", "🇫🇴": "faroese",
    "🇫🇯": "english", "🇫🇮": "finnish", "🇫🇷": "français", "🇬🇫": "français", "🇵🇫": "français",
    "🇹🇫": "français", "🇬🇦": "français", "🇬🇲": "english", "🇬🇪": "georgian", "🇩🇪": "deutsch",
    "🇬🇭": "english", "🇬🇮": "english", "🇬🇷": "greek", "🇬🇱": "danish", "🇬🇩": "english",
    "🇬🇵": "français", "🇬🇺": "english", "🇬🇹": "español", "🇬🇬": "english", "🇬🇳": "français",
    "🇬🇼": "português", "🇬🇾": "english", "🇭🇹": "français", "🇭🇳": "español", "🇭🇰": "chinese",
    "🇭🇺": "hungarian", "🇮🇸": "icelandic", "🇮🇳": "hindi", "🇮🇩": "indonesian", "🇮🇷": "persian",
    "🇮🇶": "arabic", "🇮🇪": "english", "🇮🇲": "english", "🇮🇱": "hebrew", "🇮🇹": "italiano",
    "🇯🇲": "english", "🇯🇵": "japanese", "🇯🇪": "english", "🇯🇴": "arabic", "🇰🇿": "russian",
    "🇰🇪": "swahili", "🇰🇮": "english", "🇰🇵": "korean", "🇰🇷": "korean", "🇰🇼": "arabic",
    "🇰🇬": "russian", "🇱🇦": "lao", "🇱🇻": "latvian", "🇱🇧": "arabic", "🇱🇸": "english",
    "🇱🇷": "english", "🇱🇾": "arabic", "🇱🇮": "deutsch", "🇱🇹": "lithuanian", "🇱🇺": "français",
    "🇲🇴": "chinese", "🇲🇰": "macedonian", "🇲🇬": "français", "🇲🇼": "english", "🇲🇾": "malay",
    "🇲🇻": "dhivehi", "🇲🇱": "français", "🇲🇹": "maltese", "🇲🇭": "english", "🇲🇶": "français",
    "🇲🇷": "arabic", "🇲🇺": "english", "🇾🇹": "français", "🇲🇽": "español", "🇫🇲": "english",
    "🇲🇩": "romanian", "🇲🇨": "français", "🇲🇳": "mongolian", "🇲🇪": "montenegrin", "🇲🇸": "english",
    "🇲🇦": "arabic", "🇲🇿": "português", "🇲🇲": "burmese", "🇳🇦": "english", "🇳🇷": "english",
    "🇳🇵": "nepali", "🇳🇱": "dutch", "🇳🇨": "français", "🇳🇿": "english", "🇳🇮": "español",
    "🇳🇪": "français", "🇳🇬": "english", "🇳🇺": "english", "🇳🇫": "english", "🇰🇵": "korean",
    "🇲🇵": "english", "🇳🇴": "norwegian", "🇴🇲": "arabic", "🇵🇰": "urdu", "🇵🇼": "english",
    "🇵🇸": "arabic", "🇵🇦": "español", "🇵🇬": "english", "🇵🇾": "español", "🇵🇪": "español",
    "🇵🇭": "filipino", "🇵🇳": "english", "🇵🇱": "polish", "🇵🇹": "português", "🇵🇷": "español",
    "🇶🇦": "arabic", "🇷🇪": "français", "🇷🇴": "romanian", "🇷🇺": "russian", "🇷🇼": "english",
    "🇧🇱": "français", "🇸🇭": "english", "🇰🇳": "english", "🇱🇨": "english", "🇵🇲": "français",
    "🇻🇨": "english", "🇼🇸": "english", "🇸🇲": "italiano", "🇸🇹": "português", "🇸🇦": "arabic",
    "🇸🇳": "français", "🇷🇸": "serbian", "🇸🇨": "english", "🇸🇱": "english", "🇸🇬": "english",
    "🇸🇽": "dutch", "🇸🇰": "slovak", "🇸🇮": "slovenian", "🇸🇧": "english", "🇸🇴": "somali",
    "🇿🇦": "english", "🇬🇸": "english", "🇰🇷": "korean", "🇸🇸": "english", "🇪🇸": "español",
    "🇱🇰": "sinhala", "🇸🇩": "arabic", "🇸🇷": "dutch", "🇸🇯": "norwegian", "🇸🇿": "english",
    "🇸🇪": "swedish", "🇨🇭": "deutsch", "🇸🇾": "arabic", "🇹🇼": "chinese-traditional",
    "🇹🇯": "tajik", "🇹🇿": "swahili", "🇹🇭": "thai", "🇹🇱": "tetum", "🇹🇬": "français",
    "🇹🇰": "english", "🇹🇴": "english", "🇹🇹": "english", "🇹🇳": "arabic", "🇹🇷": "turkish",
    "🇹🇲": "turkmen", "🇹🇨": "english", "🇹🇻": "english", "🇺🇬": "english", "🇺🇦": "ukrainian",
    "🇦🇪": "arabic", "🇬🇧": "english", "🇺🇸": "english", "🇺🇾": "español", "🇺🇿": "uzbek",
    "🇻🇺": "english", "🇻🇦": "italiano", "🇻🇪": "español", "🇻🇳": "vietnamese", "🇻🇮": "english",
    "🇼🇫": "français", "🇪🇭": "arabic", "🇾🇪": "arabic", "🇿🇲": "english", "🇿🇼": "english",
    # Special / rare flags that Discord supports
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿": "english", "🏴󠁧󠁢󠁳󠁣󠁴󠁿": "english", "🏴󠁧󠁢󠁷󠁬󠁳󠁿": "english",
}

# Role name → language mapping
ROLE_TO_LANGUAGE: dict[str, str] = {
    "english": "english", "español": "español", "spanish": "español",
    "français": "français", "french": "français",
    "deutsch": "deutsch", "german": "deutsch",
    "italiano": "italiano", "italian": "italiano",
    "português": "português", "portuguese": "português",
    "japanese": "japanese", "korean": "korean",
    "chinese": "chinese", "russian": "russian",
    "arabic": "arabic", "hindi": "hindi",
    "turkish": "turkish", "filipino": "filipino",
    "indonesian": "indonesian", "vietnamese": "vietnamese",
    "thai": "thai", "dutch": "dutch", "polish": "polish",
    "czech": "czech", "hungarian": "hungarian", "greek": "greek",
    "hebrew": "hebrew", "persian": "persian", "urdu": "urdu",
    "bengali": "bengali", "swahili": "swahili", "romanian": "romanian",
    "ukrainian": "ukrainian", "malay": "malay", "tagalog": "tagalog",
    "albanian": "albanian", "armenian": "armenian", "azerbaijani": "azerbaijani",
    "belarusian": "belarusian", "bosnian": "bosnian", "bulgarian": "bulgarian",
    "catalan": "catalan", "croatian": "croatian", "czech": "czech",
    "danish": "danish", "estonian": "estonian", "finnish": "finnish",
    "georgian": "georgian", "greek": "greek", "hebrew": "hebrew",
    "icelandic": "icelandic", "latvian": "latvian", "lithuanian": "lithuanian",
    "macedonian": "macedonian", "maltese": "maltese", "mongolian": "mongolian",
    "montenegrin": "montenegrin", "norwegian": "norwegian", "persian": "persian",
    "serbian": "serbian", "slovak": "slovak", "slovenian": "slovenian",
    "swedish": "swedish", "tajik": "tajik", "turkmen": "turkmen",
    "uzbek": "uzbek",
}

# Safe button list for the welcome panel (max 15 to stay under Discord's 25 limit)
ONBOARDING_LANGUAGES: list[tuple[str, str, str]] = [
    ("English", "🇺🇸", "english"),
    ("Español", "🇪🇸", "español"),
    ("Français", "🇫🇷", "français"),
    ("Deutsch", "🇩🇪", "deutsch"),
    ("Italiano", "🇮🇹", "italiano"),
    ("Português", "🇧🇷", "português"),
    ("日本語", "🇯🇵", "japanese"),
    ("한국어", "🇰🇷", "korean"),
    ("中文", "🇨🇳", "chinese"),
    ("Русский", "🇷🇺", "russian"),
    ("العربية", "🇸🇦", "arabic"),
    ("हिन्दी", "🇮🇳", "hindi"),
    ("Türkçe", "🇹🇷", "turkish"),
    ("Filipino", "🇵🇭", "filipino"),
    ("Bahasa Indonesia", "🇮🇩", "indonesian"),
]

# Large master list used by admin commands
MASTER_LANGUAGES: list[tuple[str, str, str]] = [
    ("English", "🇺🇸", "english"),
    ("Español", "🇪🇸", "español"),
    ("Français", "🇫🇷", "français"),
    ("Deutsch", "🇩🇪", "deutsch"),
    ("Italiano", "🇮🇹", "italiano"),
    ("Português", "🇧🇷", "português"),
    ("日本語", "🇯🇵", "japanese"),
    ("한국어", "🇰🇷", "korean"),
    ("中文", "🇨🇳", "chinese"),
    ("Русский", "🇷🇺", "russian"),
    ("العربية", "🇸🇦", "arabic"),
    ("हिन्दी", "🇮🇳", "hindi"),
    ("Türkçe", "🇹🇷", "turkish"),
    ("Filipino", "🇵🇭", "filipino"),
    ("Bahasa Indonesia", "🇮🇩", "indonesian"),
    ("Tiếng Việt", "🇻🇳", "vietnamese"),
    ("ไทย", "🇹🇭", "thai"),
    ("Nederlands", "🇳🇱", "dutch"),
    ("Polski", "🇵🇱", "polish"),
    ("Čeština", "🇨🇿", "czech"),
    ("Magyar", "🇭🇺", "hungarian"),
    ("Ελληνικά", "🇬🇷", "greek"),
    ("עברית", "🇮🇱", "hebrew"),
    ("فارسی", "🇮🇷", "persian"),
    ("اردو", "🇵🇰", "urdu"),
    ("বাংলা", "🇧🇩", "bengali"),
    ("Swahili", "🇰🇪", "swahili"),
    ("Română", "🇷🇴", "romanian"),
    ("Українська", "🇺🇦", "ukrainian"),
    ("Melayu", "🇲🇾", "malay"),
    ("Tagalog", "🇵🇭", "tagalog"),
    ("Español (Latinoamérica)", "🇲🇽", "spanish-latam"),
    ("Português (Brasil)", "🇧🇷", "portuguese-br"),
    ("中文 (繁體)", "🇹🇼", "chinese-traditional"),
    ("日本語 (カタカナ)", "🇯🇵", "japanese-kana"),
    ("Albanian", "🇦🇱", "albanian"),
    ("Armenian", "🇦🇲", "armenian"),
    ("Azerbaijani", "🇦🇿", "azerbaijani"),
    ("Belarusian", "🇧🇾", "belarusian"),
    ("Bosnian", "🇧🇦", "bosnian"),
    ("Bulgarian", "🇧🇬", "bulgarian"),
    ("Catalan", "🇦🇩", "catalan"),
    ("Croatian", "🇭🇷", "croatian"),
    ("Danish", "🇩🇰", "danish"),
    ("Estonian", "🇪🇪", "estonian"),
    ("Finnish", "🇫🇮", "finnish"),
    ("Georgian", "🇬🇪", "georgian"),
    ("Icelandic", "🇮🇸", "icelandic"),
    ("Latvian", "🇱🇻", "latvian"),
    ("Lithuanian", "🇱🇹", "lithuanian"),
    ("Macedonian", "🇲🇰", "macedonian"),
    ("Maltese", "🇲🇹", "maltese"),
    ("Mongolian", "🇲🇳", "mongolian"),
    ("Montenegrin", "🇲🇪", "montenegrin"),
    ("Norwegian", "🇳🇴", "norwegian"),
    ("Serbian", "🇷🇸", "serbian"),
    ("Slovak", "🇸🇰", "slovak"),
    ("Slovenian", "🇸🇮", "slovenian"),
    ("Swedish", "🇸🇪", "swedish"),
    ("Tajik", "🇹🇯", "tajik"),
    ("Turkmen", "🇹🇲", "turkmen"),
    ("Uzbek", "🇺🇿", "uzbek"),
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
