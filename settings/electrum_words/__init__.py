#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
 Copyright (c) 2019, The Sumokoin Project (www.sumokoin.org)
'''

from settings.electrum_words.english import English
from settings.electrum_words.german import German
from settings.electrum_words.spanish import Spanish
from settings.electrum_words.french import French
from settings.electrum_words.italian import Italian
from settings.electrum_words.dutch import Dutch
from settings.electrum_words.portuguese import Portuguese
from settings.electrum_words.russian import Russian
from settings.electrum_words.japanese import Japanese
from settings.electrum_words.chinese_simplified import Chinese_Simplified
from settings.electrum_words.esperanto import Esperanto
from settings.electrum_words.lojban import Lojban

english_lang = English()
german_lang = German()
spanish_lang = Spanish()
french_lang = French()
italian_lang = Italian()
dutch_lang = Dutch()
portuguese_lang = Portuguese()
russian_lang = Russian()
japanese_lang = Japanese()
chinese_simplified_lang = Chinese_Simplified()
esperanto_lang = Esperanto()
lojban_lang = Lojban()

def find_seed_language(seed):
    languages = [english_lang, german_lang, spanish_lang, french_lang, italian_lang,
                 dutch_lang, portuguese_lang, russian_lang, japanese_lang,
                 chinese_simplified_lang, esperanto_lang, lojban_lang]
    seed_list = seed.split(" ")
    for l in languages:
        is_fully_matched, matched_indices = l.match(seed_list)
        if is_fully_matched:
            return l.language_name, " ".join(l.to_english_seed(matched_indices))

    return None, None
