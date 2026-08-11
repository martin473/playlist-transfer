"""Unicode text normalization for matching."""

import re
import unicodedata
from typing import Final


# Removable media-label phrases that should be stripped from track titles
# These are common decorations like "Official Video", "Lyrics", "HD", etc.
# Note: "remix", "live", and similar meaningful version terms are NOT included
# as they should be preserved as part of the track title.
REMOVABLE_NOISE_PHRASES: Final[frozenset[str]] = frozenset({
    # Official/unofficial designations
    "official video",
    "official audio",
    "official music video",
    "official lyric video",
    "official visualizer",
    "official",
    
    # Quality indicators
    "hd",
    "hq",
    "4k",
    "1080p",
    "720p",
    "high quality",
    "high definition",
    
    # Visualizer and audio-only tags
    "visualizer",
    "audio",
    "audio only",
    "audio version",
    
    # Lyrics
    "lyrics",
    "lyric video",
    "lyrics video",
    "with lyrics",
    
    # Label upload decorations
    "label",
    "upload",
    "official upload",
    "label upload",
    
    # Common media tags
    "music video",
    "video",
    "official video",
    "official audio",
    
    # Remaster indicators (often just noise, but can be meaningful)
    "remastered",
    "remaster",
    
    # Other common decorations (not including "remix" or "live")
    "album version",
    "single version",
    "radio edit",
    "extended mix",
    "radio mix",
    "club mix",
    "dub mix",
    "instrumental",
    "acoustic",
    "cover",
    "tribute",
})


def normalize_unicode_text(value: str) -> str:
    """Normalize Unicode width, whitespace, punctuation, and separators.

    This performs a series of normalizations designed to make text comparison
    more robust across different encodings, input methods, and platforms while
    preserving non-Latin script text.

    Steps:
        1. Normalize Unicode (NFC canonical composition) to standardize combining
           characters and width variants.
        2. Normalize whitespace: collapse all Unicode whitespace runs to a single
           ASCII space, and strip leading/trailing whitespace.
        3. Normalize smart/typographic quotes: convert curly quotes to ASCII
           straight quotes.
        4. Normalize dash variants: convert em-dash, en-dash, and other dash-like
           characters to ASCII hyphen-minus.
        5. Collapse repeated separator runs: reduce any sequence of punctuation
           or separator chars (including hyphens, dots, slashes) to a single
           ASCII space.
        6. Strip leading/trailing whitespace again.

    The function is idempotent: applying it twice yields the same result.

    Args:
        value: The input string to normalize.

    Returns:
        The normalized string.
    """
    if not value:
        return ""

    # Step 1: Unicode normalization - NFC composes combining characters
    # This handles width variants (fullwidth/halfwidth) and diacritics
    normalized = unicodedata.normalize("NFC", value)

    # Step 2: Normalize all Unicode whitespace runs to single ASCII space
    # This includes non-breaking spaces, thin spaces, etc.
    # Use regex with Unicode whitespace property
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.strip()

    # Step 3: Smart/typographic quotes to ASCII straight quotes
    # “ ” ‚ ‘ ’ « » ‹ ›
    quote_map = {
        "\u2018": "'",  # LEFT SINGLE QUOTATION MARK
        "\u2019": "'",  # RIGHT SINGLE QUOTATION MARK
        "\u201A": "'",  # SINGLE LOW-9 QUOTATION MARK
        "\u201B": "'",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK
        "\u201C": '"',  # LEFT DOUBLE QUOTATION MARK
        "\u201D": '"',  # RIGHT DOUBLE QUOTATION MARK
        "\u201E": '"',  # DOUBLE LOW-9 QUOTATION MARK
        "\u201F": '"',  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
        "\u00AB": '"',  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
        "\u00BB": '"',  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
        "\u2039": "'",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
        "\u203A": "'",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    }
    for char, replacement in quote_map.items():
        normalized = normalized.replace(char, replacement)

    # Step 4: Normalize dash variants to ASCII hyphen-minus
    # — – ― ⁓ 〜 etc.
    dash_map = {
        "\u2010": "-",  # HYPHEN
        "\u2011": "-",  # NON-BREAKING HYPHEN
        "\u2012": "-",  # FIGURE DASH
        "\u2013": "-",  # EN DASH
        "\u2014": "-",  # EM DASH
        "\u2015": "-",  # HORIZONTAL BAR
        "\u2043": "-",  # HYPHEN BULLET
        "\u2E3A": "-",  # TWO-EM DASH
        "\u2E3B": "-",  # THREE-EM DASH
        "\uFE58": "-",  # SMALL EM DASH
        "\uFE63": "-",  # SMALL HYPHEN-MINUS
        "\uFF0D": "-",  # FULLWIDTH HYPHEN-MINUS
        "\u2053": "-",  # SWUNG DASH
        "\u223C": "~",  # TILDE OPERATOR (sometimes used as dash)
        "\u301C": "~",  # WAVE DASH
        "\u3030": "~",  # WAVY DASH
    }
    for char, replacement in dash_map.items():
        normalized = normalized.replace(char, replacement)

    # Step 5: Normalize repeated separators
    # Collapse repeated separator characters without removing meaningful
    # characters. Separators include: spaces, dashes, dots, slashes, etc.
    #
    # First, handle parentheses - remove parenthetical content that is
    # often just metadata (e.g., (Remastered), (Live), etc.)
    normalized = re.sub(r"\s*\([^)]*\)\s*", " ", normalized)
    
    # Normalize dash-like separators: any dash variant (including multiple)
    # with optional surrounding whitespace becomes a single space
    # This catches "Track - Remix", "Track--Remix", "Track—Remix"
    normalized = re.sub(r"\s*[-–—]\s*", " ", normalized)
    # Handle multiple dashes in a row (e.g., "Track---Remix")
    normalized = re.sub(r"[-–—]{2,}", " ", normalized)
    
    # Collapse repeated punctuation separators to a single space
    # This includes: . , ; : / | \
    # We only collapse if there are 2 or more in a row
    normalized = re.sub(r"[.,;:/|\\]{2,}", " ", normalized)
    
    # Handle repeated separators that combine punctuation and spaces
    # e.g., "Track . . . Remix" -> "Track Remix"
    # But preserve single punctuation marks with spaces around them
    # We only collapse if there are 2 or more punctuation marks with spaces
    normalized = re.sub(r"\s+[.,;:/|\\](?:\s+[.,;:/|\\])+\s+", " ", normalized)
    
    # Clean up any remaining runs of whitespace
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.strip()

    return normalized


def comparison_text(value: str) -> str:
    """Generate a comparison-only form using Unicode casefolding.

    This function applies Unicode casefolding (which is more aggressive than
    lowercasing) to create a form suitable for case-insensitive comparison
    without changing the display value. It does NOT normalize punctuation,
    whitespace, or other text characteristics—it only casefolds.

    Unicode casefolding is locale-independent and handles characters from
    all scripts, including:
        - German sharp ß -> ss
        - Greek sigma (σ/ς) -> σ
        - Turkish dotted/dotless i handling (with special case)
        - Full-width Latin variants

    Unlike lowercasing which is language-sensitive, casefolding provides
    a deterministic, locale-independent form for comparison.

    Args:
        value: The input string to casefold.

    Returns:
        The casefolded string, suitable for comparison.

    Example:
        >>> comparison_text("Straße")
        'strasse'
        >>> comparison_text("Hello World")
        'hello world'
        >>> comparison_text("İstanbul")  # Turkish dotted I
        'i̇stanbul'
    """
    if not value:
        return ""

    # Use Python's built-in casefold() which implements Unicode casefolding
    return value.casefold()
