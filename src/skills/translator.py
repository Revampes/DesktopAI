from deep_translator import GoogleTranslator

class TranslatorSkill:
    def __init__(self):
        self.langs = {
            "english": "en",
            "chinese": "zh-CN",
            "chinese simplified": "zh-CN",
            "chinese traditional": "zh-TW",
            "mandarin": "zh-CN"
        }

    def translate(self, text, target_lang):
        target_code = self.langs.get(target_lang.lower())
        
        # Auto-detect common "translate X to Y" patterns passed in as raw text
        # But usually the engine will extract the text. 
        # Here we assume 'text' is the content to translate.
        
        if not target_code:
            # Fallback or smart detection
            if "chinese" in target_lang.lower():
                target_code = "zh-CN" # Default to simplified
            elif "english" in target_lang.lower():
                target_code = "en"
            else:
                return f"Unsupported language: {target_lang}. Supported: English, Chinese (Simplified/Traditional)."

        try:
            translator = GoogleTranslator(source='auto', target=target_code)
            result = translator.translate(text)
            return f"Translated to {target_lang}: {result}"
        except Exception as e:
            return f"Translation error: {str(e)}"
