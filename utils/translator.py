from discord import Locale
from discord.enums import _UNICODE_LANG_MAP

from googletrans import Translator as GGTranslator
from googletrans.constants import LANGUAGES

translator = GGTranslator()

class Translator:
    """Supported languages are correlated to supported discord.Locale."""

    # Locale (key) -> GGLang code (value) 
    LOCALE_TO_LANGCODE = {
        code: code.split('-')[0] 
        for code in _UNICODE_LANG_MAP.keys()
        if code.split('-')[0] in LANGUAGES
    }

    LANG_TO_COUNTRY = {
        "en": "gb",
        "sv": "se",
        "zh": "cn",
        "zh-cn": "cn",
        "zh-tw": "tw",
        "ja": "jp",
        "ko": "kr",
        "hi": "in",
        "el": "gr",
        "vi": "vn",
        "cs": "cz",
        "da": "dk",
        "uk": "ua",
    }

    @staticmethod
    async def detect(text: str) -> str:
        detect = await translator.detect(text)
        if detect:
            return detect.lang
        raise RuntimeError("Language not detected.")

    @staticmethod
    async def translate(text: str, dest: str = "en", src: str = "auto") -> str:
        translation = await translator.translate(text, dest=dest, src=src)
        if translation:
            return translation.text
        raise RuntimeError("Translation failed.")
    
    @staticmethod
    async def translate_to_locale(text: str, locale: Locale, src: str = "auto") -> str:
        dest = Translator.LOCALE_TO_LANGCODE.get(locale.language_code, None)
        return await Translator.translate(text, dest=dest, src=src)
    
    @staticmethod
    def code_to_flag(code: str) -> str:
        code = Translator.LANG_TO_COUNTRY.get(code.lower(), code)

        if len(code) != 2:
            return '🏳️'

        OFFSET = 0x1F1E6
        return ''.join(chr(OFFSET + ord(c.upper()) - ord('A')) for c in code)

    @staticmethod
    def locale_to_flag(locale: Locale) -> str:
        code = locale.language_code
        region = code.split('-')[-1] if '-' in code else code

        return Translator.code_to_flag(region)