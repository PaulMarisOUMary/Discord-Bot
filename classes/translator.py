from googletrans import Translator as GT # pip install googletrans==4.0.0-rc1

class Translator:

    CORRECT_CONVERSION: dict[str, str] = {
        "en": "gb",
        "ja": "jp",
        "zh-CN": "cn",
        "ko": "kr",
        "el": "gr",
    }

    @staticmethod
    def detect(content: str) -> str:
        return GT().detect(content).lang

    @staticmethod
    def translate(content: str, dest: str, src: str = None) -> str:
        return GT().translate(content, dest=dest, src=src).text

    @staticmethod
    def get_emoji(code_lang: str) -> str:
        if code_lang in Translator.CORRECT_CONVERSION:
            code_lang = Translator.CORRECT_CONVERSION[code_lang]
        
        RISLA = 0x1f1e6 # Regional Indicator Symbol Letter A
        LSLA = 0x61 # Latin Small Letter A

        flag = ''
        for code in code_lang:
            flag += chr(RISLA + (ord(code) - LSLA))
        return flag