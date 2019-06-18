#!/usr/bin/python
# -*- coding: utf-8 -*-
# # Copyright (c) 2017-2019, The Sumokoin Project (www.sumokoin.org)
'''
Misc classes for app and wallet settings
'''

import json

from settings import *
from utils.common import *
from utils.logger import log, LEVEL_DEBUG, LEVEL_ERROR, LEVEL_INFO

config_path = os.path.join(DATA_DIR, 'config')
makeDir(config_path)

class WalletInfoException(Exception):
    pass

class WalletInfo():
    def __init__(self, app):
        self.app = app
        self.wallet_info_filepath = os.path.join(config_path, 'wallet_info.json')
        self.is_loaded = False
        self.top_tx_height = 0
        self.bc_height = -1

        self.wallet_address = None
        self.wallet_filepath = None
        self.wallet_password = None
        self.wallet_transfers = []
        self.wallet_pending_transfers = []
        self.wallet_address_book = None

    def add_transfers(self, txs):
        for tx in txs:
            if tx["height"] > self.top_tx_height:
                self.wallet_transfers.insert(0, tx)
                self.top_tx_height = tx["height"]

    def save(self):
        if self.is_loaded:
            wallet_info = {
                "wallet_filepath": self.wallet_filepath,
                "wallet_address": self.wallet_address,
            }
            try:
                writeFile(self.wallet_info_filepath, \
                          json.dumps(wallet_info, indent=2))
            except Exception, err:
                log("[WalletInfo]>>> Save error:" + str(err), LEVEL_ERROR)

        else:
            raise WalletInfoException("Wallet is not loaded!")


    def load(self):
        if os.path.exists(self.wallet_info_filepath):
            try:
                _wallet_info = json.loads(readFile(self.wallet_info_filepath))
                if os.path.exists(_wallet_info['wallet_filepath'] + '.keys'):
                    self.wallet_filepath = _wallet_info['wallet_filepath']
                    self.wallet_address =  _wallet_info['wallet_address']
                    self.is_loaded = True
                    return True
            except Exception, err:
                log("[WalletInfo]>>> Load error:" + str(err), LEVEL_ERROR)
                return False

        return False

    def reset(self):
        self.wallet_address = None
        self.wallet_filepath = None
        self.wallet_password = None
        self.wallet_transfers = []
        self.wallet_pending_transfers = []
        self.wallet_address_book = None
        self.is_loaded = False
        self.top_tx_height = 0
        self.bc_height = -1


def set_default_settings(default_settings, settings):
    for k, v in default_settings.iteritems():
        settings.setdefault(k, v)
        if type(v) is dict: set_default_settings(default_settings[k], settings[k])

class AppSettings():
    settings = {}
    default_settings = {
        "daemon": {
            "log_level": 0,
            "block_sync_size": 20,
            "limit_rate_up": 2048,
            "limit_rate_down": 8192,
        },

        "blockchain": {
            "height": 0,
        },

        "application": {
            "minimize_to_tray": False,
        }
    }

    log_levels = [0,1,2,3,4]
    block_sync_sizes = [10,20,50,100,200]
    limit_rate_ups = [512,1024,2048,3072,4096,8192,16384]
    limit_rate_downs = [512,1024,2048,4096,8192,12288,16384]


    def __init__(self):
        self.app_settings_filepath = os.path.join(config_path, 'app_settings.json')


    def load(self):
        if os.path.exists(self.app_settings_filepath):
            try:
                self.settings = json.loads(readFile(self.app_settings_filepath))
            except Exception, err:
                log("[AppSettings]>>> Load config file error:" + str(err), LEVEL_ERROR)

        # Set default values:
        set_default_settings(self.default_settings, self.settings)

        # Validate values
        if self.settings["daemon"]["log_level"] not in self.log_levels:
            self.settings["daemon"]["log_level"] = self.default_settings["daemon"]["log_level"]

        if self.settings["daemon"]["block_sync_size"] not in self.block_sync_sizes:
            self.settings["daemon"]["block_sync_size"] = self.default_settings["daemon"]["block_sync_size"]

        if self.settings["daemon"]["limit_rate_up"] not in self.limit_rate_ups:
            self.settings["daemon"]["limit_rate_up"] = self.default_settings["daemon"]["limit_rate_up"]

        if self.settings["daemon"]["limit_rate_down"] not in self.limit_rate_downs:
            self.settings["daemon"]["limit_rate_down"] = self.default_settings["daemon"]["limit_rate_down"]

        try:
            self.settings["blockchain"]["height"] = abs(int(self.settings["blockchain"]["height"]))
        except:
            self.settings["blockchain"]["height"] = self.default_settings["blockchain"]["height"]

        try:
            self.settings["application"]["minimize_to_tray"] = bool(self.settings["application"]["minimize_to_tray"])
        except:
            self.settings["application"]["minimize_to_tray"] = self.default_settings["application"]["minimize_to_tray"]


    def save(self):
        try:
            writeFile(self.app_settings_filepath, \
                json.dumps(self.settings, indent=2))
        except Exception, err:
            log("[AppSettings]>>> Save error:" + str(err), LEVEL_ERROR)
            return False

        return True
