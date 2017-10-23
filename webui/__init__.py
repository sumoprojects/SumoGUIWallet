#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
App UIs
'''

from __future__ import print_function

import sys
import hashlib
import os, json
import copy
from time import sleep

from PySide.QtGui import QApplication, QMainWindow, QIcon, \
            QSystemTrayIcon, QMenu, QAction, QMessageBox, QFileDialog, \
            QInputDialog, QLineEdit
            
from PySide.QtCore import QObject, Slot, Signal

import PySide.QtCore as qt_core
import PySide.QtWebKit as web_core
from PySide.QtCore import QTimer


from settings import APP_NAME, USER_AGENT, VERSION, COIN
from utils.logger import log, LEVEL_DEBUG, LEVEL_ERROR, LEVEL_INFO
from utils.common import readFile

from manager.ProcessManager import SumokoindManager, WalletRPCManager
from rpc import RPCRequest, DaemonRPCRequest

from classes import AppSettings, WalletInfo
from html import index, newwallet

import psutil

log_text_tmpl = """
<index>
    <head>
        <style type="text/css">
            body{
                font-family: "Lucida Console", "Courier New", Monaco, Courier, monospace;
            }
        </style>
    </head>
    <body>
        <div style="width=100%%;height:100%%">
            <code><pre>
%s
            </pre></code>
        </div>
    <body>
</index>
"""

class LogViewer(QMainWindow):
    def __init__(self, parent, log_file):
        QMainWindow.__init__(self, parent)
        self.view = web_core.QWebView(self)
        self.view.setContextMenuPolicy(qt_core.Qt.NoContextMenu)
        self.view.setCursor(qt_core.Qt.ArrowCursor)
        self.view.setZoomFactor(1)
        self.setCentralWidget(self.view)
        
        self.log_file = log_file
        self.setWindowTitle("%s - Log view [%s]" % (APP_NAME, os.path.basename(log_file)))
    
    def load_log(self):
        if not os.path.exists(self.log_file):
            _text = "[No logs]"
        else:
            with open(self.log_file) as f:
                f.seek (0, 2)           # Seek @ EOF
                fsize = f.tell()        # Get Size
                f.seek (max (fsize-4*1024*1024, 0), 0) # read last 4MB
                _text = f.read()
        self.view.setHtml(log_text_tmpl % (_text, ))
        self.resize(1100, 600)
        self.show()

class BaseWebUI(QMainWindow):
    def __init__(self, html, app, hub, window_size, debug=False):
        QMainWindow.__init__(self)
        self.app = app
        self.hub = hub
        self.debug = debug
        self.html = html
        self.url = "file:///" \
            + os.path.join(self.app.property("ResPath"), "www/").replace('\\', '/')
        
        
        self.is_first_load = True
        self.view = web_core.QWebView(self)
        
        if not self.debug:
            self.view.setContextMenuPolicy(qt_core.Qt.NoContextMenu)
        
        self.view.setCursor(qt_core.Qt.ArrowCursor)
        self.view.setZoomFactor(1)
        
        self.setWindowTitle(APP_NAME)
        self.icon = self._getQIcon('sumokoin_icon_64.png')
        self.setWindowIcon(self.icon)
        
        self.setCentralWidget(self.view)
        self.setFixedSize(window_size)
        self.center()
        
        if sys.platform == 'win32':
            psutil.Process().nice(psutil.HIGH_PRIORITY_CLASS)
        
        
    def run(self):
        self.view.loadFinished.connect(self.load_finished)
#         self.view.load(qt_core.QUrl(self.url))
        self.view.setHtml(self.html, qt_core.QUrl(self.url))
        
        
    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
        
    def load_finished(self):
        #This is the actual context/frame a webpage is running in.  
        # Other frames could include iframes or such.
        main_page = self.view.page()
        main_frame = main_page.mainFrame()
        # ATTENTION here's the magic that sets a bridge between Python to HTML
        main_frame.addToJavaScriptWindowObject("app_hub", self.hub)
        
        if self.is_first_load: ## Avoid re-settings on page reload (if happened)
            change_setting = main_page.settings().setAttribute
            settings = web_core.QWebSettings
            change_setting(settings.DeveloperExtrasEnabled, self.debug)
            change_setting(settings.LocalStorageEnabled, True)
            change_setting(settings.OfflineStorageDatabaseEnabled, True)
            change_setting(settings.OfflineWebApplicationCacheEnabled, True)
            change_setting(settings.JavascriptCanOpenWindows, True)
            change_setting(settings.PluginsEnabled, False)
            
            # Show web inspector if debug on
            if self.debug:
                self.inspector = web_core.QWebInspector()
                self.inspector.setPage(self.view.page())
                self.inspector.show()
            
            self.is_first_load = False
                    
        #Tell the HTML side, we are open for business
        main_frame.evaluateJavaScript("app_ready()")
        
    def _getQIcon(self, icon_file):
        return QIcon(os.path.join(self.app.property("ResPath"), 'icons', icon_file))


        
class NewWalletWebUI(BaseWebUI):
    def __init__(self, app, hub, debug):
        window_size = qt_core.QSize(810, 560)
        BaseWebUI.__init__(self, newwallet.html, app, hub, window_size, debug)
        self.setWindowFlags(qt_core.Qt.FramelessWindowHint)
        self.show()

        
class MainWebUI(BaseWebUI):
    def __init__(self, app, hub, debug):
        window_size = qt_core.QSize(800, 600)
        BaseWebUI.__init__(self, index.html, app, hub, window_size, debug)
        self.agent = '%s v.%s' % (USER_AGENT, '.'.join(str(v) for v in VERSION))
        log("Starting [%s]..." % self.agent, LEVEL_INFO)
        
        self.app = app
        self.debug = debug
        self.hub = hub
        
        self.app.aboutToQuit.connect(self._handleAboutToQuit)
        
        self.sumokoind_daemon_manager = None
        self.wallet_cli_manager = None
        self.wallet_rpc_manager = None
        
        self.new_wallet_ui = None
        
        self.wallet_info = WalletInfo(app)
        
        # load app settings
        self.app_settings = AppSettings()
        self.app_settings.load()
        
        ## Blockchain height
        self.target_height = self.app_settings.settings['blockchain']['height']
        self.current_height = 0
        
        
        
    
    def run(self):
        self.view.loadFinished.connect(self.load_finished)
#         self.view.load(qt_core.QUrl(self.url))
        self.view.setHtml(self.html, qt_core.QUrl(self.url))
        
        self.start_deamon()
        self.daemon_rpc_request = DaemonRPCRequest(self.app)
         
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_daemon_status)
        self.timer.start(10000)
        
        QTimer.singleShot(1000, self._load_wallet)
        QTimer.singleShot(2000, self._update_daemon_status)
        
    
    def start_deamon(self):
        #start sumokoind daemon
        self.sumokoind_daemon_manager = SumokoindManager(self.app.property("ResPath"), 
                                            self.app_settings.settings['daemon']['log_level'], 
                                            self.app_settings.settings['daemon']['block_sync_size'])
        
        self.sumokoind_daemon_manager.start()
        
        
    def show_wallet(self):
        QTimer.singleShot(1000, self.update_wallet_info)
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.update_wallet_info)
        self.timer2.start(10000)
        self.show()
        
    
    def run_wallet_rpc(self, wallet_password, log_level=0):
        # first, try to stop any wallet RPC server running
        try:
            RPCRequest('wallet_rpc').send_request({"method":"stop_wallet"})
        except:
            pass
        
        while True:
            self.hub.app_process_events()
            sumokoind_info = self.daemon_rpc_request.get_info()
            if sumokoind_info['status'] == "OK":
                self.wallet_rpc_manager = WalletRPCManager(self.app.property("ResPath"), \
                                                self.wallet_info.wallet_filepath, \
                                                wallet_password, \
                                                self.app, log_level)
                self.wallet_rpc_manager.start()
                break
        
    def _update_daemon_status(self):
        target_height = 0
        sumokoind_info = self.daemon_rpc_request.get_info()
        if sumokoind_info['status'] == "OK":
            status = "Connected"
            self.current_height = int(sumokoind_info['height'])
            target_height = int(sumokoind_info['target_height'])
            if target_height == 0 or target_height < self.current_height:
                target_height = self.current_height
            if self.target_height < target_height:
                self.target_height = target_height;
        else:
            status = sumokoind_info['status']
        
        info = {"status": status, 
                "current_height": self.current_height, 
                "target_height": self.target_height,
            }
        
        self.hub.update_daemon_status(json.dumps(info))
    
    
    def update_wallet_info(self):
        if not self.wallet_rpc_manager.is_ready():
            return
        
        wallet_info = {}
        try:
            balance, unlocked_balance = self.wallet_rpc_manager.rpc_request.get_balance()
            wallet_info['balance'] = balance/COIN
            wallet_info['unlocked_balance'] = unlocked_balance/COIN
            wallet_info['address'] = self.wallet_info.wallet_address
            if self.wallet_info.bc_height < self.current_height:
                max_height = self.current_height if self.current_height > 0 else 0x7fffffff
                min_height = self.wallet_info.top_tx_height
                if max_height > min_height:
                    transfers = self.wallet_rpc_manager.rpc_request.get_transfers(filter_by_height=True, min_height=min_height, max_height=max_height)
                    self.app.processEvents()
                    if transfers["status"] == "OK":
                        txs = []
                        if "out" in transfers:
                            for tx in transfers["out"]:
                                tx["direction"] = "out"
                                tx["status"] = "out"
                                txs.append(tx)
                                self.app.processEvents()
                            
                        if "in" in transfers:
                            for tx in transfers["in"]:
                                tx["direction"] = "in"
                                tx["status"] = "in"
                                txs.append(tx)
                                self.app.processEvents()
                                
                        sorted_txs = sorted(txs, key=lambda k: k['height'])
                        self.wallet_info.add_transfers(sorted_txs)
                self.wallet_info.bc_height = self.current_height
                        
            pending_transfers = self.wallet_rpc_manager.rpc_request.get_transfers(tx_pending=True, tx_in_pool=True)            
            pending_txs = []
            if pending_transfers["status"] == "OK":
                if "pending" in pending_transfers:
                    for tx in pending_transfers["pending"]:
                        tx["direction"] = "out"
                        tx["status"] = "pool"
                        tx["confirmation"] = 0
                        pending_txs.append(tx)
                        self.app.processEvents()
                
                if "pool" in pending_transfers:
                    for tx in pending_transfers["pool"]:
                        tx["direction"] = "in"
                        tx["status"] = "pool"
                        tx["confirmation"] = 0
                        pending_txs.append(tx)
                        self.app.processEvents()
                    
            self.wallet_info.wallet_pending_transfers = sorted(pending_txs, 
                                                    key=lambda k: k['timestamp'], 
                                                    reverse=True)
                        
            if len(self.wallet_info.wallet_pending_transfers) > 0:
                wallet_info["recent_txs"] = self.wallet_info.wallet_pending_transfers[:2]
            else:
                wallet_info["recent_txs"] = []
            
            if len(wallet_info["recent_txs"]) < 2:
                for tx in self.wallet_info.wallet_transfers[:2 - len(wallet_info["recent_txs"])]:
                    tx["confirmation"] = self.target_height - tx["height"] if self.target_height > tx["height"] else 0
                    wallet_info["recent_txs"].append(tx)
            
            self.hub.on_wallet_update_info_event.emit(json.dumps(wallet_info))
        except Exception, err:
            log(str(err), LEVEL_ERROR)
            
    
    def show_new_wallet_ui(self):
        self.reset_wallet(delete_files=False)
        self.hide()
        self.new_wallet_ui = NewWalletWebUI(self.app, self.hub, self.debug)
        self.hub.setNewWalletUI(self.new_wallet_ui)
        self.new_wallet_ui.run()
        
        
    def reset_wallet(self, delete_files=True):
        if self.wallet_rpc_manager is not None:
            self.wallet_rpc_manager.stop()
        
        wallet_filepath = self.wallet_info.wallet_filepath
        if delete_files and wallet_filepath and os.path.exists(wallet_filepath):
            try:
                os.remove(wallet_filepath)
                os.remove(wallet_filepath + ".keys")
                os.remove(wallet_filepath + ".address.txt")
            except:
                pass
        
        self.wallet_info.reset()
        if self.new_wallet_ui:
            self.hub.on_new_wallet_ui_reset_event.emit()
        self.hub.on_main_wallet_ui_reset_event.emit()
        
    def about(self):
        QMessageBox.about(self, "About", \
            u"%s <br><br>Copyright© 2017 - Sumokoin Projects (www.sumokoin.org)" % self.agent)
    
    def _load_wallet(self):
        if self.wallet_info.load():
            wallet_password = None
            self.show()
            while True:
                wallet_password, result = self.hub._custom_input_dialog(self, \
                            "Wallet Password", "Enter wallet password:", \
                            QLineEdit.Password)
                if not result:
                    wallet_password = None
                    break
                elif not wallet_password:
                    QMessageBox.warning(self, "Wallet Password", \
                                        "Password is required to open wallet!")
                else:
                    break
                
            if not wallet_password:
#                 self.new_wallet_ui = NewWalletWebUI(self.app, self.hub, self.debug)
#                 self.hub.setNewWalletUI(self.new_wallet_ui)
#                 self.new_wallet_ui.run()
                
                self.close()
                return
            else:
                self.run_wallet_rpc(wallet_password, 0)
                while not self.wallet_rpc_manager.is_ready():
                    self.hub.app_process_events(0.5)
                    if self.wallet_rpc_manager.is_invalid_password():
                        QMessageBox.critical(self, \
                            'Error Starting Wallet',\
                            "Error: Wallet password is incorrect!<br><br>Please retry...")
                        self._load_wallet()
                        return
                
                self.wallet_info.wallet_password = hashlib.sha256(wallet_password).hexdigest()
                self.update_wallet_info()
                self.timer2 = QTimer(self)
                self.timer2.timeout.connect(self.update_wallet_info)
                self.timer2.start(15000)
        else:
            self.new_wallet_ui = NewWalletWebUI(self.app, self.hub, self.debug)
            self.hub.setNewWalletUI(self.new_wallet_ui)
            self.new_wallet_ui.run()
        
    
    def _handleAboutToQuit(self):
        log("%s is about to quit..." % APP_NAME, LEVEL_INFO)
        if hasattr(self, "timer"):
            self.timer.stop()
        if hasattr(self, "timer2"):
            self.timer2.stop()
        if self.wallet_rpc_manager is not None:
            self.wallet_rpc_manager.stop()
        if self.sumokoind_daemon_manager is not None:
            self.sumokoind_daemon_manager.stop()
        
        self.app_settings.settings['blockchain']['height'] = self.target_height
        self.app_settings.save()