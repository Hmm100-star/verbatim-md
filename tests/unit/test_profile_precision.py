import pytest

from verbatim_md.config import Profile, load_profile


def test_word_font_sizes_cannot_silently_round():
    with pytest.raises(ValueError, match='half-point'):
        load_profile(Profile(font_size=11.3))
    assert load_profile(Profile(font_size=11.5)).font_size == 11.5
