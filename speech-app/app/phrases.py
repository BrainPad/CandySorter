#!/usr/bin/python
# -*- coding: utf-8 -*-

import json


class PhraseGenerator:
    @classmethod
    def get_phrases(self, filename, key):
        with open(filename, 'r', encoding='utf8') as config:
            self.data = json.loads(config.read())

        if key not in self.data.keys():
            return []

        sentences = []
        for stem in self.data[key]['stems']:
            for word in self.data[key]['words']:
                sentences.append(stem + " " + word)

        return sentences