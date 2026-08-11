"""Unit tests for Unicode text normalization."""

import pytest

from playlist_bridge.matching.normalize import normalize_unicode_text


class TestNormalizeUnicodeText:
    """Tests for the normalize_unicode_text function."""

    def test_empty_string(self):
        """Empty string should return empty string."""
        assert normalize_unicode_text("") == ""

    def test_whitespace_normalization(self):
        """Multiple whitespace should collapse to single space."""
        assert normalize_unicode_text("Hello  world") == "Hello world"
        assert normalize_unicode_text("Hello\nworld") == "Hello world"
        assert normalize_unicode_text("Hello\t\t world") == "Hello world"
        assert normalize_unicode_text("  leading and trailing  ") == "leading and trailing"

    def test_non_breaking_space(self):
        """Non-breaking spaces should be normalized."""
        text = "Hello\u00A0world"  # NBSP
        assert normalize_unicode_text(text) == "Hello world"

    def test_smart_quotes_single(self):
        """Smart single quotes should become straight quotes."""
        # LEFT SINGLE QUOTATION MARK
        assert normalize_unicode_text("\u2018Hello\u2019") == "'Hello'"
        # SINGLE LOW-9 QUOTATION MARK
        assert normalize_unicode_text("\u201AHello") == "'Hello"
        # SINGLE HIGH-REVERSED-9 QUOTATION MARK
        assert normalize_unicode_text("\u201BHello") == "'Hello"

    def test_smart_quotes_double(self):
        """Smart double quotes should become straight double quotes."""
        # LEFT DOUBLE QUOTATION MARK
        assert normalize_unicode_text("\u201CHello\u201D") == '"Hello"'
        # DOUBLE LOW-9 QUOTATION MARK
        assert normalize_unicode_text("\u201EHello") == '"Hello'
        # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
        assert normalize_unicode_text("\u201FHello") == '"Hello'

    def test_angle_quotes(self):
        """Angle quotes should become straight quotes."""
        assert normalize_unicode_text("\u00ABHello\u00BB") == '"Hello"'
        assert normalize_unicode_text("\u2039Hello\u203A") == "'Hello'"

    def test_dash_variants(self):
        """Various dash characters should be normalized to separators."""
        # EM DASH, EN DASH, FIGURE DASH, etc. - all collapse to single space
        assert normalize_unicode_text("Track\u2014Remix") == "Track Remix"
        assert normalize_unicode_text("Track\u2013Remix") == "Track Remix"
        assert normalize_unicode_text("Track\u2012Remix") == "Track Remix"
        assert normalize_unicode_text("Track\u2010Remix") == "Track Remix"
        assert normalize_unicode_text("Track\u2011Remix") == "Track Remix"
        # HORIZONTAL BAR
        assert normalize_unicode_text("Track\u2015Remix") == "Track Remix"
        # FULLWIDTH HYPHEN-MINUS
        assert normalize_unicode_text("Track\uFF0DRemix") == "Track Remix"

    def test_wave_dash(self):
        """Wave dash and tilde variants should become tildes."""
        # Tilde is preserved as-is without adding extra space
        assert normalize_unicode_text("~hello") == "~hello"
        assert normalize_unicode_text("\u223Chello") == "~hello"  # TILDE OPERATOR
        assert normalize_unicode_text("\u301Chello") == "~hello"  # WAVE DASH
        assert normalize_unicode_text("\u3030hello") == "~hello"  # WAVY DASH

    def test_separator_collapsing(self):
        """Repeated separators should collapse to single space."""
        assert normalize_unicode_text("Track--Remix") == "Track Remix"
        assert normalize_unicode_text("Track - Remix") == "Track Remix"
        assert normalize_unicode_text("Track  -  Remix") == "Track Remix"
        assert normalize_unicode_text("Track...Remix") == "Track Remix"
        # Underscores should be preserved or collapsed depending on implementation
        # The current implementation preserves them as word separators
        assert normalize_unicode_text("Track___Remix") == "Track___Remix"
        assert normalize_unicode_text("Track.Remix") == "Track.Remix"
        assert normalize_unicode_text("Track/Remix") == "Track/Remix"
        assert normalize_unicode_text("Track:Remix") == "Track:Remix"
        assert normalize_unicode_text("Track;Remix") == "Track;Remix"

    def test_mixed_punctuation(self):
        """Mixed punctuation should be handled correctly."""
        # Multiple types of separators in a row - the current implementation
        # normalizes dashes and spaces but preserves other punctuation
        assert normalize_unicode_text("Track--._Remix") == "Track ._Remix"
        assert normalize_unicode_text("Track  -  .  Remix") == "Track . Remix"

    def test_non_latin_preservation(self):
        """Non-Latin scripts should be preserved."""
        # Japanese
        assert normalize_unicode_text("こんにちは 世界") == "こんにちは 世界"
        # Chinese
        assert normalize_unicode_text("你好 世界") == "你好 世界"
        # Korean
        assert normalize_unicode_text("안녕하세요 세계") == "안녕하세요 세계"
        # Cyrillic
        assert normalize_unicode_text("Привет мир") == "Привет мир"
        # Greek
        assert normalize_unicode_text("Γειά σου κόσμε") == "Γειά σου κόσμε"
        # Arabic
        assert normalize_unicode_text("مرحبا بالعالم") == "مرحبا بالعالم"
        # Devanagari
        assert normalize_unicode_text("नमस्ते दुनिया") == "नमस्ते दुनिया"

    def test_accented_characters(self):
        """Accented characters should be preserved via NFC normalization."""
        # Precomposed é (U+00E9) stays as é
        assert normalize_unicode_text("Café") == "Café"
        # Combining sequence e + combining accent becomes é
        assert normalize_unicode_text("Cafe\u0301") == "Café"
        # Both should produce the same result
        assert normalize_unicode_text("Café") == normalize_unicode_text("Cafe\u0301")

    def test_fullwidth_halfwidth(self):
        """Fullwidth characters should be normalized."""
        # Fullwidth space (U+3000)
        assert normalize_unicode_text("Hello\u3000world") == "Hello world"
        # Fullwidth hyphen-minus (U+FF0D) is handled in dash normalization
        assert normalize_unicode_text("Track\uFF0DRemix") == "Track Remix"

    def test_idempotence(self):
        """Applying the function twice should yield the same result."""
        test_strings = [
            "Hello  world",
            "Track — Remix",
            "Smart “quotes” here",
            "Fullwidth　space",
            "Multiple---dashes",
            "Mixed  ,  punctuation!",
            "Café  au  lait",
            "こんにちは 世界",
            "Título  con  acentos",
            "",
            "  leading  and  trailing  ",
            "Track--._Remix",
            "Track\u2014Remix",
            "\u201CHello\u201D",
        ]
        for text in test_strings:
            first = normalize_unicode_text(text)
            second = normalize_unicode_text(first)
            assert first == second, f"Idempotence failed for: {text!r}"

    def test_real_world_examples(self):
        """Test with realistic track title examples."""
        # Dashes and spaces are normalized
        assert normalize_unicode_text("Bohemian Rhapsody - Remastered 2011") == "Bohemian Rhapsody Remastered 2011"
        assert normalize_unicode_text("Stairway to Heaven – Live") == "Stairway to Heaven Live"
        # Parentheses with content are removed by the current implementation
        assert normalize_unicode_text("Wonderwall (Remastered)") == "Wonderwall"
        assert normalize_unicode_text("Smells Like Teen Spirit — Remix") == "Smells Like Teen Spirit Remix"
        # With smart quotes
        assert normalize_unicode_text("\u201CShape of You\u201D") == '"Shape of You"'
        # With accented characters
        assert normalize_unicode_text("Héllö Wörld") == "Héllö Wörld"
