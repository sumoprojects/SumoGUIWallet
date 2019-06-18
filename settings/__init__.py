#!/usr/bin/python
# -*- coding: utf-8 -*-
# # Copyright (c) 2017-2019, The Sumokoin Project (www.sumokoin.org)
'''
App top-level settings
'''
__doc__ = 'default application wide settings'

import sys
import os
import logging

from utils.common import getHomeDir, makeDir

VERSION = [0, 2, 1]
APP_NAME = "Sumo GUI Wallet"
USER_AGENT = '%s v%s' % (APP_NAME, '.'.join(str(v) for v in VERSION))

_data_dir = makeDir(os.path.join(getHomeDir(), 'SumoGUIWallet'))
DATA_DIR = _data_dir

log_file = os.path.join(DATA_DIR, 'logs', 'app.log')  # default logging file
log_level = logging.DEBUG  # logging level

seed_languages = [("German", u"Deutsch"),
                  ("English", u"English"),
                  ("Spanish", u"Español"),
                  ("French", u"Français"),
                  ("Italian", u"Italiano"),
                  ("Dutch", u"Nederlands"),
                  ("Portuguese", u"Português"),
                  ("Russian", u"Русский язык"),
                  ("Japanese", u"日本語 "),
                  ("Chinese (simplified)", u"简体中文 (中国)"),
                  ("Esperanto", u"Esperanto"),
                  ("Lojban", u"Lojban"),
                ]

# COIN - number of smallest units in one coin
COIN = 1000000000.0
