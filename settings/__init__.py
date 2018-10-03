#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017-2018, The Sumokoin Project (www.sumokoin.org)
'''
App top-level settings
'''

__doc__ = 'default application wide settings'

import sys
import os
import logging

from utils.common import getHomeDir, makeDir

VERSION = [0, 1, 0]
APP_NAME = "Sumo GUI Wallet"
USER_AGENT = '%s v.%s' % (APP_NAME, '.'.join(str(v) for v in VERSION))



_data_dir = makeDir(os.path.join(getHomeDir(), 'SumoGUIWallet'))
DATA_DIR = _data_dir

log_file  = os.path.join(DATA_DIR, 'logs', 'app.log') # default logging file
log_level = logging.DEBUG # logging level

seed_languages = [("0", "German"), 
                  ("1", "English"), 
                  ("2", "Spanish"), 
                  ("3", "French"), 
                  ("4", "Italian"),
                  ("5", "Dutch"),
                  ("6", "Portuguese"),
                  ("7", "Russian"),
                  ("8", "Japanese"),
                  ("9", "Chinese (Simplified)"),
                  ("10", "Esperanto"),
                  ("11", "Lojban"),
                ]

if sys.platform in ['win32','cygwin','win64']:
    seed_languages = [("1", "English"), 
                      ("3", "French"), 
                      ("4", "Italian"),
                      ("5", "Dutch"),
                      ("6", "Portuguese"),
                      ("10", "Esperanto"),
                      ("11", "Lojban"),
                    ]
    
# COIN - number of smallest units in one coin
COIN = 1000000000.0