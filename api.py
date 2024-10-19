class api():
    # Attributes
    _key = ""

    # Behaviors

    # Setters:
    def pick_key(self, code):
        # Not all of these are API Keys/tokens, but they all need to be hidden
        if code == 1:
            self._key = 'c999ec5e-fab9-4360-8326-3825ffcb3fb9'
        elif code == 2:
            self._key = 'PTb5ae26a882762022a798154a1efa7f5e5a9ddce08994b6c3'
        elif code == 3:
            self._key = 'test1928u.signalwire.com'
        elif code == 4:
            self._key = '+12068288235'
        elif code == 5:
            self._key = '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'
        elif code == 6:
            self._key = 'https://api.openai.com/v1/chat/completions'