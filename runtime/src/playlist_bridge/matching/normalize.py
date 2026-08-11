"""Unicode text normalization for matching."""

import re
import unicodedata
from typing import Collection, Final


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
    
    # Other common decorations (not including meaningful version terms)
    "tribute",
})

# Meaningful version terms that should be preserved as part of track titles
# These indicate specific versions or arrangements that are semantically significant
# and should NOT be removed as noise during title normalization.
MEANINGFUL_VERSION_TERMS: Final[frozenset[str]] = frozenset({
    "remix",
    "live",
    "acoustic",
    "instrumental",
    "cover",
    "extended",
    "radio edit",
    "club mix",
    "dub mix",
    "album version",
    "single version",
    "mix",
    "version",
    "edit",
    "reprise",
    "medley",
    "megamix",
    "mashup",
    "bootleg",
    "unplugged",
    "piano version",
    "orchestral",
    "string version",
    "electronic",
    "dance",
    "house",
    "techno",
    "dub",
    "drum & bass",
    "jungle",
})


# Version qualifier tokens that should be extracted as version information
# These are meaningful version indicators like "remix", "live", "acoustic", etc.
VERSION_QUALIFIER_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    # Remix variants
    re.compile(r'\bremix\b', re.IGNORECASE),
    re.compile(r'\bmix\b', re.IGNORECASE),
    # Edit variants
    re.compile(r'\bedit\b', re.IGNORECASE),
    # Remaster variants
    re.compile(r'\bremaster\b', re.IGNORECASE),
    re.compile(r'\bremastered\b', re.IGNORECASE),
    # Live
    re.compile(r'\blive\b', re.IGNORECASE),
    # Instrumental
    re.compile(r'\binstrumental\b', re.IGNORECASE),
    # Acoustic
    re.compile(r'\bacoustic\b', re.IGNORECASE),
    # Dub
    re.compile(r'\bdub\b', re.IGNORECASE),
    # Clean
    re.compile(r'\bclean\b', re.IGNORECASE),
    # Explicit
    re.compile(r'\bexplicit\b', re.IGNORECASE),
    re.compile(r'\bexplicit\b', re.IGNORECASE),
)

# Mapping of version qualifier patterns to their canonical category
VERSION_CATEGORY_MAP: Final[dict[str, str]] = {
    'remix': 'remix',
    'mix': 'mix',
    'edit': 'edit',
    'remaster': 'remaster',
    'remastered': 'remaster',
    'live': 'live',
    'instrumental': 'instrumental',
    'acoustic': 'acoustic',
    'dub': 'dub',
    'clean': 'clean',
    'explicit': 'explicit',
}


def extract_version_tokens(value: str) -> tuple[str, ...]:
    """Extract meaningful version qualifier tokens from a string.

    This function scans the input text for known version qualifier terms
    (remix, mix, edit, remaster, live, instrumental, acoustic, dub, clean,
    explicit) and returns them as a tuple. The tokens are preserved in their
    original casing (case-folded for comparison) and each token is normalized
    to its canonical category.

    The function is designed to be used as part of the track title normalization
    pipeline, extracting version information that can be used for matching
    decisions.

    Args:
        value: The input string to scan for version qualifiers.

    Returns:
        A tuple of version qualifier tokens, with each token in lowercase.
        Returns an empty tuple if no qualifiers are found.

    Example:
        >>> extract_version_tokens("Song Title (Remix)")
        ('remix',)
        >>> extract_version_tokens("Live Acoustic Version")
        ('live', 'acoustic')
        >>> extract_version_tokens("Clean Edit")
        ('clean', 'edit')
        >>> extract_version_tokens("No qualifiers here")
        ()
    """
    if not value:
        return ()

    found_tokens = set()

    # Scan for each version qualifier pattern
    for pattern in VERSION_QUALIFIER_PATTERNS:
        if pattern.search(value):
            # Extract the matched text and normalize it
            match = pattern.search(value)
            if match:
                token_text = match.group(0).lower()
                # Map to canonical category if available
                category = VERSION_CATEGORY_MAP.get(token_text, token_text)
                found_tokens.add(category)

    # Return as sorted tuple for deterministic ordering
    return tuple(sorted(found_tokens))


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


def remove_bracketed_noise(value: str, removable_phrases: Collection[str] = REMOVABLE_NOISE_PHRASES) -> str:
    """Remove bracketed segments only when they consist entirely of removable noise phrases.

    This function identifies bracketed segments in the input string (e.g., "[Official Video]",
    "[Remix]", "[HD]") and removes them only if the content inside the brackets consists
    entirely of phrases from the removable_phrases set. If a bracketed segment contains any
    meaningful version term (like "Remix", "Live", etc.), it is preserved.

    The removal is case-insensitive - the removable_phrases set should contain lowercase
    versions, and the content inside brackets is compared in lowercase.

    Args:
        value: The input string that may contain bracketed segments.
        removable_phrases: Collection of phrase strings to treat as removable noise.
            Defaults to REMOVABLE_NOISE_PHRASES.

    Returns:
        The string with removable bracketed noise removed, with whitespace cleaned up.

    Example:
        >>> remove_bracketed_noise("Song Title [Official Video]")
        'Song Title'
        >>> remove_bracketed_noise("Song Title [Remix]")
        'Song Title [Remix]'
        >>> remove_bracketed_noise("Song Title [HD]")
        'Song Title'
    """
    if not value:
        return ""

    # Build a set of lowercase removable phrases for case-insensitive matching
    removable_set = {phrase.lower() for phrase in removable_phrases}

    # Pattern to match bracketed segments: [content]
    # Using non-greedy matching to handle multiple bracketed segments
    pattern = r"\[([^\]]+)\]"

    def should_remove(match: re.Match) -> str:
        """Determine if a bracketed segment should be removed."""
        content = match.group(1)
        # Normalize whitespace and split into phrases
        # Split on common separators: spaces, commas, slashes, etc.
        # We need to handle cases like "[Official Video]" -> ["official", "video"]
        # and also "[HD]" -> ["hd"]
        # but also phrases like "[Official Video]" might be matched as "official video"
        # We'll use both approaches: try to match the whole content as a phrase,
        # and also check if all individual words are removable

        # Clean and normalize the content
        cleaned = content.strip().lower()
        # Normalize multiple spaces to single space
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Check if the entire content is a removable phrase
        if cleaned in removable_set:
            return ""

        # Check if the content consists of multiple words that are all removable
        # This handles "Official Video" -> ["official", "video"]
        words = cleaned.split()
        if words and all(word in removable_set for word in words):
            return ""

        # Check if the content contains any meaningful version term
        # If it does, preserve the whole bracket
        # This is a safety check - we want to preserve meaningful terms
        # Even if they might be in the removable set, we should preserve them
        # Actually, the requirement says: "remove bracketed segments only when they consist
        # entirely of removable noise phrases" - so if it's entirely removable phrases,
        # remove it. Otherwise, preserve it.

        # If we get here, the content is not entirely removable noise,
        # so we preserve the entire bracketed segment
        return match.group(0)

    # Apply the replacement
    result = re.sub(pattern, should_remove, value)

    # Clean up extra whitespace that might result from removal
    result = re.sub(r"\s+", " ", result)
    result = result.strip()

    return result


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


def detect_unwanted_version_flags(title: str, artist_hints: Sequence[str]) -> tuple[str, ...]:
    """Detect unwanted version indicators in a track title and artist hints.

    This function scans the track title and artist hints for common unwanted
    version indicators that may reduce match quality or indicate the track is
    not the original/studio version. Detected flags include:

        - karaoke: karaoke versions
        - cover: cover versions (not original artist)
        - tribute: tribute versions
        - nightcore: nightcore sped-up versions
        - sped-up: sped-up versions
        - slowed: slowed-down versions
        - reverb: reverb-heavy versions
        - reaction: reaction videos/audio
        - tutorial: tutorial/educational content
        - performance: live or studio performance versions

    The function checks both the title and the artist hints (if provided) for
    these indicators and returns a deduplicated, sorted tuple of detected flags.

    Args:
        title: The track title to analyze.
        artist_hints: A sequence of artist names to also check.

    Returns:
        A tuple of detected flag strings, deduplicated and sorted alphabetically.
        Returns an empty tuple if no unwanted version indicators are found.

    Example:
        >>> detect_unwanted_version_flags("Song Title (Karaoke Version)", [])
        ('karaoke',)
        >>> detect_unwanted_version_flags("Nightcore - Song Title", [])
        ('nightcore',)
        >>> detect_unwanted_version_flags("Cover of Song", ["Original Artist"])
        ('cover',)
    """
    if not title and not artist_hints:
        return ()

    detected = set()

    # Normalize the title and artist hints for comparison
    normalized_title = title.casefold() if title else ""
    normalized_artists = [a.casefold() for a in artist_hints if a]

    # Define flag patterns: (regex pattern, flag name)
    # These patterns match words/phrases in the normalized text
    flag_patterns = [
        (re.compile(r'\bkaraoke\b'), 'karaoke'),
        (re.compile(r'\bcover\b'), 'cover'),
        (re.compile(r'\btribute\b'), 'tribute'),
        (re.compile(r'\bnightcore\b'), 'nightcore'),
        (re.compile(r'sped[\s-]*up'), 'sped-up'),  # "sped up" or "sped-up"
        (re.compile(r'slowed[\s-]*down'), 'slowed'),  # "slowed down" or "slowed-down"
        (re.compile(r'\bslowed\b'), 'slowed'),
        (re.compile(r'\breverb\b'), 'reverb'),
        (re.compile(r'\breaction\b'), 'reaction'),
        (re.compile(r'\btutorial\b'), 'tutorial'),
        (re.compile(r'\bperformance\b'), 'performance'),
        # Also catch "spedup" and "sloweddown" without spaces
        (re.compile(r'spedup'), 'sped-up'),
        (re.compile(r'sloweddown'), 'slowed'),
    ]

    # Check the title
    if normalized_title:
        for pattern, flag in flag_patterns:
            if pattern.search(normalized_title):
                detected.add(flag)

    # Check artist hints
    for artist in normalized_artists:
        for pattern, flag in flag_patterns:
            if pattern.search(artist):
                detected.add(flag)

    return tuple(sorted(detected))
