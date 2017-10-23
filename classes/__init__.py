#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
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
                if os.path.exists(_wallet_info['wallet_filepath']):
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
        
        
class AppSettings():
    settings = {
        "daemon": {
            "log_level": 0,
            "block_sync_size": 10
        },
        
        "blockchain": {
            "height": 0,
        }
    }
    
    def __init__(self):
        self.app_settings_filepath = os.path.join(config_path, 'app_settings.json')
    
    
    def load(self):
        if os.path.exists(self.app_settings_filepath):
            try:
                self.settings = json.loads(readFile(self.app_settings_filepath))
                return True
            except Exception, err:
                log("[AppSettings]>>> Load error:" + str(err), LEVEL_ERROR)
                return False
        return False
    
    def save(self):
        try:
            writeFile(self.app_settings_filepath, \
                json.dumps(self.settings, indent=2))
        except Exception, err:
            log("[AppSettings]>>> Save error:" + str(err), LEVEL_ERROR)
            return False
        
        return True