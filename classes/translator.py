from googletrans import Translator as GT # pip install googletrans==4.0.0-rc1

class Translator:

    # doc: https://cloud.google.com/translate/docs/languages
    CORRECT_CONVERSION: dict[str, str] = {
        "af": "za",
        "am": "et",
        "ar": "ae",
        "be": "by",
        "bn": "bd",
        "bs": "ba",
        "ca": "es", # invalid flag
        "ceb": "ph",
        "co": "fr", # invalid flag
        "cs": "cz",
        "cy": "gb",
        "da": "dk",
        "el": "gr",
        "en": "gb",
        "en-gb": "gb",
        "en-us": "us",
        "eo": "pl",
        "es-es": "es",
        "et": "ee",
        "eu": "es",
        "fa": "ir",
        "fy": "nl", # invalid flag
        "ga": "ie",
        "gd": "en",
        "gl": "es", # invalid flag
        "gu": "in", # invalid flag
        "ha": "ng",
        "haw": "us", # invalid flag
        "he": "il",
        "hi": "in",
        "hmn": "la",
        "ht": "us", # invalid flag
        "hy": "am",
        "ig": "ng", # invalid flag
        "iw": "il",
        "ja": "jp",
        "jw": "id",
        "ka": "ge",
        "kk": "kz",
        "km": "kh",
        "kn": "in",
        "ko": "kr",
        "ku": "iq",
        "ky": "kg",
        "la": "", # ! critical invalid flag
        "lb": "lu",
        "lo": "la",
        "mi": "nz",
        "ml": "in", # invalid flag
        "mr": "in",
        "ms": "in",
        "my": "mm",
        "ne": "np",
        "ny": "mw",
        "or": "in",
        "pa": "in", # invalid flag
        "ps": "af",
        "pt-br": "br",
        "sd": "pk",
        "si": "lk",
        "sl": "si",
        "sm": "ws",
        "sn": "zw",
        "sq": "al",
        "sr": "rs",
        "st": "ls",
        "su": "sd",
        "sv": "se",
        "sv-se": "sv",
        "sw": "ke",
        "ta": "in", # invalid flag
        "te": "in", # invalid flag
        "tg": "tj",
        "tl": "hn",
        "ug": "cn",
        "ur": "pk",
        "vi": "vn",
        "xh": "za",
        "yi": "il", # invalid flag
        "yo": "", # ! critical invalid flag
        "zh-cn": "cn",
        "zh-tw": "tw",
        "zu": "za" # invalid flag
    }

    # doc: https://discordpy.readthedocs.io/en/master/api.html?highlight=loca#discord.Locale
    LOCALE_CONVERSION: dict[str, str] = {
        "en-us": "en",
        "en-gb": "en",
        "es-es": "es",
        "pt-br": "pt",
        "sv-se": "sv"
    }

    @staticmethod
    def detect(content: str) -> str:
        return GT().detect(content).lang

    @staticmethod
    def translate(content: str, dest: str, src: str) -> str:
        return GT().translate(content, dest=dest, src=src).text

    @staticmethod
    def get_flag_abbr(code_lang: str) -> str:
        return Translator.CORRECT_CONVERSION.get(code_lang.lower(), code_lang.lower())

    @staticmethod
    def get_trans_abbr(locale: str) -> str:
        return Translator.LOCALE_CONVERSION.get(locale.lower(), locale.lower())

    @staticmethod
    def get_emoji(code_lang: str) -> str:
        code_lang = Translator.get_flag_abbr(code_lang)
        
        RISLA = 0x1f1e6 # Regional Indicator Symbol Letter A
        LSLA = 0x61 # Latin Small Letter A

        flag = ''
        for code in code_lang:
            flag += chr(RISLA + (ord(code) - LSLA))
        return flag