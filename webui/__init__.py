#!/usr/bin/python
# -*- coding: utf-8 -*-
# # Copyright (c) 2017-2019, The Sumokoin Project (www.sumokoin.org)
'''
App UIs
'''

from __future__ import print_function

import sys
import hashlib
import os, json
import signal
import copy
from time import sleep

from PySide.QtGui import QApplication, QMainWindow, QIcon, \
            QSystemTrayIcon, QMenu, QAction, QMessageBox, QFileDialog, \
            QInputDialog, QLineEdit

from PySide.QtCore import QObject, Slot, Signal

import PySide.QtCore as qt_core
import PySide.QtWebKit as web_core
from PySide.QtCore import QTimer


from settings import APP_NAME, USER_AGENT, VERSION, COIN,DATA_DIR, makeDir
from utils.logger import log, LEVEL_DEBUG, LEVEL_ERROR, LEVEL_INFO
from utils.common import readFile

from utils.notify import Notify
MSG_TYPE_INFO = 1
MSG_TYPE_WARNING = 2
MSG_TYPE_CRITICAL = 3

from manager.ProcessManager import SumokoindManager, WalletRPCManager
from rpc import RPCRequest, DaemonRPCRequest

from classes import AppSettings, WalletInfo
from html import index, newwallet

import psutil

wallet_dir_path = os.path.join(DATA_DIR, 'wallets')
makeDir(wallet_dir_path)

INVALID_PASSWORD_STR = "Invalid password"
UPDATE_DAEMON_STATUS_INTERVAL = 10000
UPDATE_WALLET_INFO_INTERVAL = 30000
MAX_NEW_SUBADDRESSES = 5
tray_icon_tooltip = "%s v%d.%d.%s" % (APP_NAME, VERSION[0], VERSION[1], VERSION[2])

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
            + os.path.join(self.app.property("ResPath"), "www/index.html").replace('\\', '/')


        self.is_first_load = True
        self.view = web_core.QWebView(self)

        if not self.debug:
            self.view.setContextMenuPolicy(qt_core.Qt.NoContextMenu)

        self.view.setCursor(qt_core.Qt.ArrowCursor)
        self.view.setZoomFactor(1)

        self.setWindowTitle(USER_AGENT)
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
#         self.setWindowFlags(qt_core.Qt.FramelessWindowHint)
        self.show()


class MainWebUI(BaseWebUI):
    def __init__(self, app, hub, debug):
        window_size = qt_core.QSize(800, 600)
        BaseWebUI.__init__(self, index.html, app, hub, window_size, debug)
        self.agent = USER_AGENT
        log("Starting [%s]..." % self.agent, LEVEL_INFO)

        # Setup the system tray icon
        if sys.platform == 'darwin':
            tray_icon = 'sumokoin_16x16_mac.png'
        elif sys.platform == "win32":
            tray_icon = 'sumokoin_16x16.png'
        else:
            tray_icon = 'sumokoin_32x32_ubuntu.png'

        self.trayIcon = QSystemTrayIcon(self._getQIcon(tray_icon))
        self.trayIcon.setToolTip(tray_icon_tooltip)

        self.app = app
        self.debug = debug
        self.hub = hub

        self.sumokoind_daemon_manager = None
        self.wallet_rpc_manager = None
        self.sumokoind_daemon_pid = None
        self.wallet_rpc_pid = None

        self.new_wallet_ui = None

        self.wallet_info = WalletInfo(app)

        # load app settings
        self.app_settings = AppSettings()
        self.app_settings.load()

        ## Blockchain height
        self.target_height = self.app_settings.settings['blockchain']['height']
        self.current_height = 0

        self.daemon_version = None

        # Setup the tray icon context menu
        self.trayMenu = QMenu()

        self.showAppAction = QAction('&Show %s' % APP_NAME, self)
        f = self.showAppAction.font()
        f.setBold(True)
        self.showAppAction.setFont(f)
        self.trayMenu.addAction(self.showAppAction)


        self.aboutAction = QAction('&About...', self)
        self.trayMenu.addAction(self.aboutAction)

        self.trayMenu.addSeparator()
        self.exitAction = QAction('&Exit', self)
        self.trayMenu.addAction(self.exitAction)
        # Add menu to tray icon
        self.trayIcon.setContextMenu(self.trayMenu)

        # connect signals
        self.trayIcon.activated.connect(self._handleTrayIconActivate)
        self.exitAction.triggered.connect(self.handleExitAction)
        self.aboutAction.triggered.connect(self.handleAboutAction)
        self.showAppAction.triggered.connect(self._handleShowAppAction)
        self.app.aboutToQuit.connect(self._handleAboutToQuit)

        # Setup notification support
        self.system_tray_running_notified = False
        self.notifier = Notify(APP_NAME)
        self.trayIcon.show()

        self.close_to_system_tray = self.app_settings.settings['application']['minimize_to_tray']

    def closeEvent(self, event):
        """ Override QT close event
        """
        if not self.close_to_system_tray:
            reply=QMessageBox.question(self,'Exit %s?' % APP_NAME,
                    "Are you sure to exit %s?" % APP_NAME, \
                    QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.hide_wallet()
            else:
                event.ignore()
            return

        event.ignore()
        self.hide()
        if not self.system_tray_running_notified:
            self.notify("%s is still running at system tray." % APP_NAME,
                                                        "Running Status")
            self.system_tray_running_notified = True

    def run(self):
        self.view.loadFinished.connect(self.load_finished)
#         self.view.load(qt_core.QUrl(self.url))
        self.view.setHtml(self.html, qt_core.QUrl(self.url))

        self.start_deamon()
        self.daemon_rpc_request = DaemonRPCRequest(self.app)

        self.update_daemon_status_timer = QTimer(self)
        self.update_daemon_status_timer.timeout.connect(self._update_daemon_status)
        self.update_daemon_status_timer.start(UPDATE_DAEMON_STATUS_INTERVAL)

        QTimer.singleShot(1, self._load_wallet)
        QTimer.singleShot(1000, self._update_daemon_status)


    def start_deamon(self):
        #start sumokoind daemon
        self.sumokoind_daemon_manager = SumokoindManager(self.app.property("ResPath"),
                                            self.app_settings.settings['daemon']['log_level'],
                                            self.app_settings.settings['daemon']['block_sync_size'],
                                            self.app_settings.settings['daemon']['limit_rate_up'],
                                            self.app_settings.settings['daemon']['limit_rate_down'])

        self.sumokoind_daemon_manager.start()
        self.sumokoind_daemon_pid = self.sumokoind_daemon_manager.get_pid()


    def show_wallet(self):
        QTimer.singleShot(1, self.update_wallet_info)
        if not hasattr(self, "update_wallet_info_timer"):
            self.update_wallet_info_timer = QTimer(self)
            self.update_wallet_info_timer.timeout.connect(self.update_wallet_info)
        self.update_wallet_info_timer.stop()
        self.update_wallet_info_timer.start(UPDATE_WALLET_INFO_INTERVAL)

        self.show()
        self.trayIcon.show()


    def hide_wallet(self):
        self.hide()
        self.trayIcon.hide()

    def run_wallet_rpc(self, log_level=0):
        while True:
            self.hub.app_process_events()
            sumokoind_info = self.daemon_rpc_request.get_info()
            if sumokoind_info['status'] == "OK":
                self.wallet_rpc_manager = WalletRPCManager(self.app.property("ResPath"),
                                                wallet_dir_path,
                                                self.app, log_level)
                self.wallet_rpc_manager.start()
                self.wallet_rpc_pid = self.wallet_rpc_manager.get_pid()
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
            if not self.daemon_version:
                self.daemon_version = sumokoind_info['version']
        else:
            status = sumokoind_info['status']

        info = {"status": status,
                "current_height": self.current_height,
                "target_height": self.target_height,
            }

        self.hub.update_daemon_status(json.dumps(info))

        sync_status = "Disconnected" if sumokoind_info['status'] != "OK" else "Synchronizing..."
        if sumokoind_info['status'] == "OK" and self.current_height == self.target_height:
            sync_status = "Network synchronized"

        self.trayIcon.setToolTip("%s\n%s (%d/%d)" % (tray_icon_tooltip, sync_status,
                                               self.current_height, self.target_height))


    def update_wallet_info(self):
        if self.wallet_rpc_manager is None:
            return

        wallet_info = {}
        try:
            balance, unlocked_balance, per_subaddress = self.wallet_rpc_manager.rpc_request.get_balance()
            wallet_info['balance'] = balance/COIN
            wallet_info['unlocked_balance'] = unlocked_balance/COIN
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

            adddress_info = self.wallet_rpc_manager.rpc_request.get_address()
            wallet_info['address'] = adddress_info['address']
            wallet_info['used_subaddresses'] = []
            wallet_info['new_subaddresses'] = []
            for subaddress in adddress_info['addresses']:
                if subaddress['used']:
                    wallet_info['used_subaddresses'].append(subaddress)
                    # update subaddress balance
                    subaddress['balance'] = 0.
                    subaddress['unlocked_balance'] = 0.
                    for s in per_subaddress:
                        if s['address_index'] == subaddress['address_index']:
                            subaddress['balance'] = s['balance']/COIN
                            subaddress['unlocked_balance'] = s['unlocked_balance']/COIN
                            break
                else:
                    if subaddress['address_index'] > 0:
                        wallet_info['new_subaddresses'].append(subaddress)

            wallet_info['used_subaddresses'] = sorted(wallet_info['used_subaddresses'],
                                                      key=lambda k:k['balance'],
                                                      reverse=True)

            # auto-generate new subaddresses if not enough available
            if len(wallet_info['new_subaddresses']) < MAX_NEW_SUBADDRESSES:
                for _ in range(MAX_NEW_SUBADDRESSES - len(wallet_info['new_subaddresses'])):
                    new_subaddress = self.wallet_rpc_manager.rpc_request.create_address()
                    new_subaddress['label'] = ""
                    new_subaddress['used'] = False
                    wallet_info['new_subaddresses'].append(new_subaddress)

            if len(wallet_info['new_subaddresses']) > MAX_NEW_SUBADDRESSES:
                wallet_info['new_subaddresses'] = wallet_info['new_subaddresses'][0:MAX_NEW_SUBADDRESSES]

#             print(json.dumps(wallet_info, indent=4))

            self.hub.on_wallet_update_info_event.emit(json.dumps(wallet_info))
        except Exception, err:
            log(str(err), LEVEL_ERROR)


    def show_new_wallet_ui(self):
        self.reset_wallet(delete_files=False)
        if self.wallet_rpc_manager is not None:
            self.wallet_rpc_manager.reset_block_height()
            self.wallet_rpc_manager.rpc_request.stop_wallet()
        self.hide_wallet()
        self.new_wallet_ui = NewWalletWebUI(self.app, self.hub, self.debug)
        self.hub.setNewWalletUI(self.new_wallet_ui)
        self.new_wallet_ui.run()


    def reset_wallet(self, delete_files=True):
        wallet_filepath = self.wallet_info.wallet_filepath
        if delete_files and wallet_filepath and os.path.exists(wallet_filepath):
            try:
                os.remove(wallet_filepath)
                os.remove(wallet_filepath + ".keys")
            except:
                pass

        self.wallet_info.reset()
        if self.new_wallet_ui:
            self.hub.on_new_wallet_ui_reset_event.emit()
        self.hub.on_main_wallet_ui_reset_event.emit()

    def notify(self, message, title="", icon=None, msg_type=None):
        if self.notifier.notifier is not None:
            self.notifier.notify(title, message, icon)
        else:
            self.showMessage(message, title, msg_type)

    def showMessage(self, message, title="", msg_type=None, timeout=2000):
        """Displays 'message' through the tray icon's showMessage function,
        with title 'title'. 'type' is one of the enumerations of
        'common.MessageTypes'.
        """
        if msg_type is None or msg_type == MSG_TYPE_INFO:
            icon = QSystemTrayIcon.Information

        elif msg_type == MSG_TYPE_WARNING:
            icon = QSystemTrayIcon.Warning

        elif msg_type == MSG_TYPE_CRITICAL:
            icon = QSystemTrayIcon.Critical

        title = "%s - %s" % (APP_NAME, title) if title else APP_NAME
        self.trayIcon.showMessage(title, message, icon, timeout)

    def about(self):
        daemon_version_str = "<br><br>- Core (daemon/wallet binaries) version: v%s" % self.daemon_version
        QMessageBox.about(self, "About", \
            u"%s %s <br><br>Copyright© 2017 -2019 - Sumokoin Projects (www.sumokoin.org)" % \
                                                            (self.agent, daemon_version_str))

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
                result = QMessageBox.question(self, "Create/Restore Wallet?", \
                            "Do you want to create (or restore to) a new wallet instead?", \
                            QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
                if result == QMessageBox.No:
                    self.trayIcon.hide()
                    QTimer.singleShot(250, self.app.quit)
                else:
                    self.show_new_wallet_ui()
                return

            if not self.wallet_rpc_manager:
                self.run_wallet_rpc(2)
                while not self.wallet_rpc_manager.is_ready():
                    self.app.processEvents()

            wallet_load_failed = True
            retrial_counter = 0
            while wallet_load_failed:
                ret = self.wallet_rpc_manager.rpc_request.open_wallet(
                                        os.path.basename(self.wallet_info.wallet_filepath),
                                        wallet_password)
                if ret['status'] == "ERROR":
                    error_message = ret['message']
                    QMessageBox.critical(self.new_wallet_ui, \
                            'Error Starting Wallet',\
                            "Error: %s" % error_message)
                    if INVALID_PASSWORD_STR in error_message:
                        if retrial_counter > 1:
                            break

                        wallet_password, result = self.hub._custom_input_dialog(self, \
                                    "Wallet Password", "Re-enter wallet password:", \
                                    QLineEdit.Password)
                        if not result:
                            wallet_password = None
                            break
                        elif not wallet_password:
                            QMessageBox.warning(self, "Wallet Password", \
                                                "Password is required to open wallet!")
                            break
                        retrial_counter += 1
                    else:
                        break
                else:
                    wallet_load_failed = False

            if wallet_load_failed:
                reply = QMessageBox.question(self,'Create new wallet?',
                    "Wallet failed to load! Do you want to create a new wallet instead?", QMessageBox.Yes,QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.show_new_wallet_ui()
                else:
                    self.handleExitAction(show_confirmation=False)
            else:
                self.wallet_info.wallet_password = hashlib.sha256(wallet_password).hexdigest()
                self.update_wallet_info()
                if not hasattr(self, "update_wallet_info_timer"):
                    self.update_wallet_info_timer = QTimer(self)
                    self.update_wallet_info_timer.timeout.connect(self.update_wallet_info)

                self.update_wallet_info_timer.stop()
                self.update_wallet_info_timer.start(UPDATE_WALLET_INFO_INTERVAL)
        else:
            self.show_new_wallet_ui()

    def _handleTrayIconActivate(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def handleExitAction(self, show_confirmation=True):
        reply = QMessageBox.No
        if show_confirmation:
            self._handleShowAppAction()
            reply=QMessageBox.question(self,'Exit %s?' % APP_NAME,
                    "Are you sure to exit %s?" % APP_NAME, QMessageBox.Yes,QMessageBox.No)
        if not show_confirmation or reply==QMessageBox.Yes:
            QTimer.singleShot(250, self.app.quit)

    def _handleShowAppAction(self):
        self.showNormal()
        self.activateWindow()

    def handleAboutAction(self):
        self._handleShowAppAction()
        self.about()

    def _handleAboutToQuit(self):
        self.hide_wallet()
        log("%s is about to quit..." % APP_NAME, LEVEL_INFO)
        if hasattr(self, "update_daemon_status_timer"):
            self.update_daemon_status_timer.stop()
        if hasattr(self, "update_wallet_info_timer"):
            self.update_wallet_info_timer.stop()
        if self.wallet_rpc_manager is not None:
            self.wallet_rpc_manager.stop()
        if self.sumokoind_daemon_manager is not None:
            self.sumokoind_daemon_manager.stop()

        self.app_settings.settings['blockchain']['height'] = self.target_height
        self.app_settings.save()
