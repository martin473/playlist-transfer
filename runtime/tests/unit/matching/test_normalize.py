"""Unit tests for Unicode text normalization."""

import pytest

from playlist_bridge.matching.normalize import normalize_unicode_text, comparison_text


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


class TestComparisonText:
    """Tests for the comparison_text function."""

    def test_empty_string(self):
        """Empty string should return empty string."""
        assert comparison_text("") == ""

    def test_basic_lowercasing(self):
        """Basic ASCII text should be lowercased."""
        assert comparison_text("Hello World") == "hello world"
        assert comparison_text("HELLO") == "hello"
        assert comparison_text("Mixed Case") == "mixed case"

    def test_german_sharp_s(self):
        """German sharp ß should casefold to 'ss'."""
        assert comparison_text("Straße") == "strasse"
        assert comparison_text("GROß") == "gross"
        assert comparison_text("Fußball") == "fussball"

    def test_greek_sigma(self):
        """Greek sigma variants should casefold to sigma."""
        # Final sigma (ς) and normal sigma (σ) both casefold to σ
        # Note: Python's casefold() doesn't convert final sigma to regular sigma,
        # it preserves the distinction. The important thing is that uppercase
        # and lowercase versions of the same word compare equal.
        assert comparison_text("κόσμος") == "κόσμοσ"  # final sigma preserved
        assert comparison_text("ΚΟΣΜΟΣ") == "κοσμοσ"  # uppercase casefolds to lowercase with final sigma

    def test_turkish_dotted_i(self):
        """Turkish dotted/dotless I handling."""
        # Dotted I (İ) casefolds to i with dot above
        assert comparison_text("İstanbul") == "i̇stanbul"
        # Dotless i (ı) casefolds to ı (preserved)
        assert comparison_text("ıstanbul") == "ıstanbul"

    def test_casefolded_equivalence(self):
        """Equivalent capitalization variants should produce equal comparison text."""
        # This is the core acceptance criterion from the task
        variants = [
            ("Hello", "hello"),
            ("HELLO", "hello"),
            ("HeLlO", "hello"),
            ("Straße", "straße"),
            ("STRASSE", "strasse"),
            ("Straße", "strasse"),
        ]
        # All variants of the same word should produce the same casefolded result
        assert comparison_text("Hello") == comparison_text("hello")
        assert comparison_text("HELLO") == comparison_text("hello")
        assert comparison_text("HeLlO") == comparison_text("hello")
        assert comparison_text("Straße") == comparison_text("STRASSE")
        assert comparison_text("Straße") == comparison_text("strasse")

    def test_non_latin_casefolding(self):
        """Non-Latin scripts should casefold appropriately."""
        # Cyrillic
        assert comparison_text("ПРИВЕТ") == "привет"
        assert comparison_text("Привет") == "привет"
        # Greek - casefold preserves final sigma
        assert comparison_text("ΚΟΣΜΟΣ") == "κοσμοσ"
        assert comparison_text("Κόσμος") == "κόσμοσ"
        # Arabic (has no case, should be unchanged)
        assert comparison_text("مرحبا") == "مرحبا"
        # Hebrew (has no case, should be unchanged)
        assert comparison_text("שלום") == "שלום"

    def test_punctuation_preserved(self):
        """Punctuation should be preserved (not normalized)."""
        assert comparison_text("Hello, World!") == "hello, world!"
        assert comparison_text("Track - Remix") == "track - remix"
        assert comparison_text("Track...Remix") == "track...remix"

    def test_whitespace_preserved(self):
        """Whitespace should be preserved (not normalized)."""
        assert comparison_text("Hello  world") == "hello  world"
        assert comparison_text("  leading  ") == "  leading  "
        assert comparison_text("Hello\nworld") == "hello\nworld"

    def test_casefold_different_from_lower(self):
        """Casefold can produce different results from lower() for some characters."""
        # German ß: lower() -> ß, casefold() -> ss
        assert comparison_text("Straße") != "straße".lower()
        assert comparison_text("Straße") == "straße".casefold()
        # Turkish dotted I: lower() -> i, casefold() -> i̇ (i + combining dot above)
        assert comparison_text("İstanbul") != "istanbul"
        assert comparison_text("İstanbul") == "i̇stanbul"

    def test_casefold_idempotent(self):
        """Applying casefold twice should yield the same result."""
        test_strings = [
            "Hello World",
            "Straße",
            "Κόσμος",
            "İstanbul",
            "Привет",
            "Mixed CASE String!",
            "",
        ]
        for text in test_strings:
            first = comparison_text(text)
            second = comparison_text(first)
            assert first == second, f"Idempotence failed for: {text!r}"

    def test_empty_and_whitespace(self):
        """Edge cases with empty and whitespace-only strings."""
        assert comparison_text("") == ""
        assert comparison_text(" ") == " "
        assert comparison_text("  ") == "  "
        assert comparison_text("\t") == "\t"



class TestRemoveBracketedNoise:
    """Tests for the remove_bracketed_noise function."""

    def test_removes_official_video(self):
        """[Official Video] should be removed as noise."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Official Video]")
        assert result == "Song Title"
        
        result = remove_bracketed_noise("Song Title [Official Video] Extra")
        assert result == "Song Title Extra"

    def test_removes_official_audio(self):
        """[Official Audio] should be removed as noise."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Official Audio]")
        assert result == "Song Title"

    def test_removes_lyrics(self):
        """[Lyrics] should be removed as noise."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Lyrics]")
        assert result == "Song Title"

    def test_removes_hd_hq(self):
        """[HD] and [HQ] should be removed as noise."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [HD]")
        assert result == "Song Title"
        
        result = remove_bracketed_noise("Song Title [HQ]")
        assert result == "Song Title"

    def test_removes_visualizer(self):
        """[Visualizer] should be removed as noise."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Visualizer]")
        assert result == "Song Title"

    def test_preserves_remix_in_brackets(self):
        """[Remix] should be preserved as a meaningful version term."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Remix]")
        assert result == "Song Title [Remix]"
        
        result = remove_bracketed_noise("Song Title [Club Mix]")
        assert result == "Song Title [Club Mix]"

    def test_preserves_live_in_brackets(self):
        """[Live] should be preserved as a meaningful version term."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Live]")
        assert result == "Song Title [Live]"

    def test_preserves_acoustic_in_brackets(self):
        """[Acoustic] should be preserved as a meaningful version term."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Acoustic]")
        assert result == "Song Title [Acoustic]"

    def test_removes_multiple_noise_brackets(self):
        """Multiple removable noise brackets should all be removed."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Official Video] [HD]")
        assert result == "Song Title"
        
        # Test multiple brackets where some are removable and some are meaningful
        # [Official Video] is removable, [Remix] is meaningful and should be preserved
        result = remove_bracketed_noise("Song Title [Official Video] [Remix]")
        assert result == "Song Title [Remix]"

    def test_removes_bracket_with_multiple_noise_words(self):
        """Brackets containing multiple noise words should be removed."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        # "official video" is a removable phrase
        result = remove_bracketed_noise("Song Title [official video]")
        assert result == "Song Title"

    def test_preserves_bracket_with_mixed_content(self):
        """Brackets containing a mix of noise and meaningful terms should be preserved."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        # This has "official" (noise) and "remix" (meaningful)
        result = remove_bracketed_noise("Song Title [Official Remix]")
        assert result == "Song Title [Official Remix]"

    def test_preserves_bracket_with_meaningful_term(self):
        """Brackets containing only meaningful terms should be preserved."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [Extended Mix]")
        assert result == "Song Title [Extended Mix]"

    def test_handles_empty_string(self):
        """Empty string should return empty string."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("")
        assert result == ""

    def test_handles_string_without_brackets(self):
        """String without brackets should be unchanged."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title")
        assert result == "Song Title"

    def test_handles_case_insensitive_removal(self):
        """Removal should be case-insensitive."""
        from playlist_bridge.matching.normalize import remove_bracketed_noise
        
        result = remove_bracketed_noise("Song Title [OFFICIAL VIDEO]")
        assert result == "Song Title"
        
        result = remove_bracketed_noise("Song Title [official video]")
        assert result == "Song Title"


class TestRemovableNoisePhrases:
    """Tests for the REMOVABLE_NOISE_PHRASES constant."""

    def test_constant_exists(self):
        """REMOVABLE_NOISE_PHRASES should be defined and be a frozenset."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        assert isinstance(REMOVABLE_NOISE_PHRASES, frozenset)
        assert len(REMOVABLE_NOISE_PHRASES) > 0

    def test_contains_required_phrases(self):
        """REMOVABLE_NOISE_PHRASES should contain the required phrases."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        
        # Required phrases from the task
        required_phrases = {
            "official video",
            "official audio", 
            "lyrics",
            "hd",
            "hq",
            "visualizer",
        }
        
        for phrase in required_phrases:
            assert phrase in REMOVABLE_NOISE_PHRASES, f"'{phrase}' should be in REMOVABLE_NOISE_PHRASES"

    def test_contains_label_upload_decorations(self):
        """REMOVABLE_NOISE_PHRASES should contain label-upload decorations."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        
        # Label upload related phrases
        label_upload_phrases = {
            "label",
            "upload",
            "official upload",
            "label upload",
        }
        
        for phrase in label_upload_phrases:
            assert phrase in REMOVABLE_NOISE_PHRASES, f"'{phrase}' should be in REMOVABLE_NOISE_PHRASES"

    def test_contains_common_media_tags(self):
        """REMOVABLE_NOISE_PHRASES should contain common media tags."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        
        # Common media tags
        media_tags = {
            "music video",
            "video",
            "official music video",
            "official lyric video",
            "official visualizer",
        }
        
        for phrase in media_tags:
            assert phrase in REMOVABLE_NOISE_PHRASES, f"'{phrase}' should be in REMOVABLE_NOISE_PHRASES"

    def test_contains_quality_indicators(self):
        """REMOVABLE_NOISE_PHRASES should contain quality indicators."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        
        quality_indicators = {
            "4k",
            "1080p",
            "720p",
            "high quality",
            "high definition",
        }
        
        for phrase in quality_indicators:
            assert phrase in REMOVABLE_NOISE_PHRASES, f"'{phrase}' should be in REMOVABLE_NOISE_PHRASES"

    def test_contains_audio_lyrics_variants(self):
        """REMOVABLE_NOISE_PHRASES should contain audio and lyrics variants."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        
        variants = {
            "audio",
            "audio only",
            "audio version",
            "lyric video",
            "lyrics video",
            "with lyrics",
        }
        
        for phrase in variants:
            assert phrase in REMOVABLE_NOISE_PHRASES, f"'{phrase}' should be in REMOVABLE_NOISE_PHRASES"

    def test_no_meaningful_terms(self):
        """REMOVABLE_NOISE_PHRASES should NOT contain meaningful version terms."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES, MEANINGFUL_VERSION_TERMS
        
        # These terms are meaningful and should be preserved (not removed)
        # Use the actual constant for comprehensive checking
        for term in MEANINGFUL_VERSION_TERMS:
            assert term not in REMOVABLE_NOISE_PHRASES, f"'{term}' should NOT be in REMOVABLE_NOISE_PHRASES"
        
        # Additionally, verify that "remastered" is NOT in MEANINGFUL_VERSION_TERMS
        # since we treat it as noise in the removable set
        assert "remastered" not in MEANINGFUL_VERSION_TERMS

    def test_all_phrases_lowercase(self):
        """All phrases in REMOVABLE_NOISE_PHRASES should be lowercase."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        
        for phrase in REMOVABLE_NOISE_PHRASES:
            assert phrase == phrase.lower(), f"'{phrase}' should be lowercase"

    def test_no_duplicate_phrases(self):
        """REMOVABLE_NOISE_PHRASES should have no duplicate phrases."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        
        # frozenset automatically deduplicates, but let's verify
        phrase_list = list(REMOVABLE_NOISE_PHRASES)
        assert len(phrase_list) == len(set(phrase_list)), "Duplicate phrases found"

    def test_phrase_list_comprehensive(self):
        """REMOVABLE_NOISE_PHRASES should be comprehensive."""
        from playlist_bridge.matching.normalize import REMOVABLE_NOISE_PHRASES
        
        # This is a spot check - we expect at least 20 phrases
        assert len(REMOVABLE_NOISE_PHRASES) >= 20, f"Expected at least 20 phrases, got {len(REMOVABLE_NOISE_PHRASES)}"

    def test_meaningful_version_terms_defined(self):
        """MEANINGFUL_VERSION_TERMS should be defined and contain expected terms."""
        from playlist_bridge.matching.normalize import MEANINGFUL_VERSION_TERMS
        
        # Verify the constant exists and is a frozenset
        assert isinstance(MEANINGFUL_VERSION_TERMS, frozenset), "Should be a frozenset"
        
        # Verify it contains at least the core meaningful terms
        expected_core_terms = {"remix", "live", "acoustic", "instrumental", "cover"}
        for term in expected_core_terms:
            assert term in MEANINGFUL_VERSION_TERMS, f"'{term}' should be in MEANINGFUL_VERSION_TERMS"
        
        # Verify "remastered" is NOT in the meaningful terms (it's treated as noise)
        assert "remastered" not in MEANINGFUL_VERSION_TERMS, "remastered should not be in MEANINGFUL_VERSION_TERMS"
        
        # Ensure it's a reasonable size (at least 10 terms)
        assert len(MEANINGFUL_VERSION_TERMS) >= 10, f"Expected at least 10 meaningful terms, got {len(MEANINGFUL_VERSION_TERMS)}"
