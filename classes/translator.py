from googletrans import Translator as GT # pip install googletrans==4.0.0-rc1

class Translator:

    # doc: https://cloud.google.com/translate/docs/languages
    CORRECT_CONVERSION: dict[str, str] = {
        "af": "za",
        "am": "et",
        "ar": "ae",
        "az": "az", # key == value
        "be": "by",
        "bg": "bg", # key == value
        "bn": "bd",
        "bs": "ba",
        "ca": "es", # invalid flag
        "ceb": "ph",
        "co": "fr", # invalid flag
        "cs": "cz",
        "cy": "gb",
        "da": "dk",
        "de": "de", # key == value
        "el": "gr",
        "en": "gb",
        "en-gb": "gb",
        "en-us": "us",
        "eo": "pl",
        "es": "es", # key == value
        "es-es": "es",
        "et": "ee",
        "eu": "es",
        "fa": "ir",
        "fi": "fi", # key == value
        "fr": "fr", # key == value
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
        "hr": "hr", # key == value
        "ht": "us", # invalid flag
        "hu": "hu", # key == value
        "hy": "am",
        "id": "id", # key == value
        "ig": "ng", # invalid flag
        "is": "is", # key == value
        "it": "it", # key == value
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
        "la": None, # ! critical invalid flag
        "lb": "lu",
        "lo": "la",
        "lt": "lt", # key == value
        "lv": "lv", # key == value
        "mg": "mg", # key == value
        "mi": "nz",
        "mk": "mk", # key == value
        "ml": "in", # invalid flag
        "mn": "mn", # key == value
        "mr": "in",
        "ms": "in",
        "mt": "mt", # key == value
        "my": "mm",
        "ne": "np",
        "nl": "nl", # key == value
        "no": "no", # key == value
        "ny": "mw",
        "or": "in",
        "pa": "in", # invalid flag
        "pl": "pl", # key == value
        "ps": "af",
        "pt": "pt", # key == value
        "pt-br": "br",
        "ro": "ro", # key == value
        "ru": "ru", # key == value
        "sd": "pk",
        "si": "lk",
        "sk": "sk", # key == value
        "sl": "si",
        "sm": "ws",
        "sn": "zw",
        "so": "so", # key == value
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
        "th": "th", # key == value
        "tl": "hn",
        "tr": "tr", # key == value
        "ug": "cn",
        "uk": "uk", # key == value
        "ur": "pk",
        "uz": "uz", # key == value
        "vi": "vn",
        "xh": "za",
        "yi": "il", # invalid flag
        "yo": None, # ! critical invalid flag
        "zh-cn": "cn",
        "zh-tw": "tw",
        "zu": "za" # invalid flag
    }

    @staticmethod
    def detect(content: str) -> str:
        return GT().detect(content).lang

    @staticmethod
    def translate(content: str, dest: str, src: str = None) -> str:
        return GT().translate(content, dest=dest, src=src).text

    @staticmethod
    def get_flag_abbr(code_lang: str) -> str:
        return Translator.CORRECT_CONVERSION.get(code_lang.lower(), code_lang.lower())

    @staticmethod
    def get_emoji(code_lang: str) -> str:
        code_lang = Translator.get_flag_abbr(code_lang)
        
        RISLA = 0x1f1e6 # Regional Indicator Symbol Letter A
        LSLA = 0x61 # Latin Small Letter A

        flag = ''
        for code in code_lang:
            flag += chr(RISLA + (ord(code) - LSLA))
        return flag