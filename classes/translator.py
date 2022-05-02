from googletrans import Translator as GT # pip install googletrans==4.0.0-rc1

class Translator:

    CORRECT_CONVERSION: dict[str, str] = {
        "cs": "cz",
        "da": "dk",
        "el": "gr",
        "en": "gb",
        "en-GB": "gb",
        "en-US": "us",
        "es-ES": "es",
        "hi": "in",
        "ja": "jp",
        "ko": "kr",
        "pt-BR": "br",
        "sv-SE": "sv",
        "zh-CN": "cn",
        "zh-TW": "tw",
    }

    @staticmethod
    def detect(content: str) -> str:
        return GT().detect(content).lang

    @staticmethod
    def translate(content: str, dest: str, src: str = None) -> str:
        return GT().translate(content, dest=dest, src=src).text

    @staticmethod
    def get_flag_abbr(code_lang: str) -> str:
        if code_lang in Translator.CORRECT_CONVERSION:
            return Translator.CORRECT_CONVERSION[code_lang]
        return code_lang

    @staticmethod
    def get_emoji(code_lang: str) -> str:
        code_lang = Translator.get_flag_abbr(code_lang)
        
        RISLA = 0x1f1e6 # Regional Indicator Symbol Letter A
        LSLA = 0x61 # Latin Small Letter A

        flag = ''
        for code in code_lang:
            flag += chr(RISLA + (ord(code) - LSLA))
        return flag