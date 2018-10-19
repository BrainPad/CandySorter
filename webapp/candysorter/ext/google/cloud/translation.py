from google.cloud import translate


class TranslatorClient(translate.Client):
    def translate_text(self, text, source_lang, target_lang):
        return self.translate([text], source_language=source_lang, target_language=target_lang)