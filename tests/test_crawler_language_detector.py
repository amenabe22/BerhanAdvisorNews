from pipeline.utils.language_detector import detect_language


def test_detect_language_prefers_amharic_for_ethiopic_text():
    text = "ብሔራዊ ባንክ ኢትዮጵያ የውጭ ምንዛሬ መመሪያ አወጣ"
    assert detect_language(text) == "am"


def test_detect_language_handles_english_text():
    text = "National Bank of Ethiopia issued a new foreign exchange directive."
    assert detect_language(text) == "en"
