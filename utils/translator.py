from asyncio import to_thread
from typing import Final

from deep_translator import GoogleTranslator
from discord import Locale
from langcodes import Language
from langdetect import LangDetectException
from langdetect import detect as _detect_langcode

_UNKNOWN_FLAG: Final = '🏳️'
_REGIONAL_INDICATOR_OFFSET: Final = 0x1F1E6

_FLAG_REGION_FALLBACK: Final[dict[str, str]] = {
    "bg": "BG",
    "cs": "CZ",
    "da": "DK",
    "de": "DE",
    "el": "GR",
    "es": "ES",
    "fi": "FI",
    "fr": "FR",
    "hi": "IN",
    "hr": "HR",
    "hu": "HU",
    "id": "ID",
    "it": "IT",
    "ja": "JP",
    "ko": "KR",
    "lt": "LT",
    "nl": "NL",
    "no": "NO",
    "pl": "PL",
    "ro": "RO",
    "ru": "RU",
    "th": "TH",
    "tr": "TR",
    "uk": "UA",
    "vi": "VN",
}

_TRANSLATION_KEEPS_REGION: Final = {"zh"}


def region_to_flag(region: str) -> str:
    if len(region) != 2 or not region.isalpha():
        return _UNKNOWN_FLAG

    return "".join(
        chr(_REGIONAL_INDICATOR_OFFSET + ord(letter) - ord("A"))
        for letter in region.upper()
    )


def _require_language(parsed: Language) -> str:
    if parsed.language is None:
        raise ValueError(f"{parsed} has no language subtag.")

    return parsed.language


def locale_to_flag(locale: Locale) -> str:
    parsed = Language.get(locale.value)
    region = parsed.territory

    if region is None or len(region) != 2 or not region.isalpha():
        region = _FLAG_REGION_FALLBACK.get(_require_language(parsed))

    return region_to_flag(region) if region else _UNKNOWN_FLAG


def locale_to_langcode(locale: Locale) -> str:
    parsed = Language.get(locale.value)
    language = _require_language(parsed)

    if language in _TRANSLATION_KEEPS_REGION and parsed.territory:
        return f"{language}-{parsed.territory}"

    return language


_LOCALE_BY_LANGCODE: Final[dict[str, Locale]] = {
    locale_to_langcode(locale): locale for locale in Locale
}

_locales_without_flag = [
    locale for locale in Locale if locale_to_flag(locale) == _UNKNOWN_FLAG
]
if _locales_without_flag:
    raise RuntimeError(
        f"_FLAG_REGION_FALLBACK is missing an entry for: {', '.join(locale.name for locale in _locales_without_flag)}"
    )


def langcode_to_locale(code: str) -> Locale | None:
    parsed = Language.get(code)
    language = _require_language(parsed)

    if language in _TRANSLATION_KEEPS_REGION and parsed.territory:
        regional = _LOCALE_BY_LANGCODE.get(f"{language}-{parsed.territory}")
        if regional:
            return regional

    return _LOCALE_BY_LANGCODE.get(language)


def display_name(locale: Locale, in_locale: Locale | None = None) -> str:
    language = Language.get(locale.value)

    if in_locale is None:
        return language.display_name()

    target = _require_language(Language.get(in_locale.value))
    return language.display_name(target)


class Translator:
    @staticmethod
    async def detect(text: str) -> Locale | None:
        try:
            code = await to_thread(_detect_langcode, text)
        except LangDetectException:
            return None

        return langcode_to_locale(code)

    @staticmethod
    async def translate(text: str, dest: Locale, src: Locale | None = None) -> str:
        source = locale_to_langcode(src) if src else "auto"
        target = locale_to_langcode(dest)

        translator = GoogleTranslator(source=source, target=target)
        return await to_thread(translator.translate, text)
