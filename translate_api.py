from googletrans import Translator


class MyTranslator(object):
    def __init__(self):
        self.translator = Translator()

    def translate(self, phrase, src='en', dest='ro'):
        p = self.translator.translate(phrase, src=src, dest=dest)
        return p.text
