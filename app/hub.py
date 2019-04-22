#!/usr/bin/python
# -*- coding: utf-8 -*-
# # Copyright (c) 2017-2019, The Sumokoin Project (www.sumokoin.org)
'''
Hub is a communication medium between Python codes and web UI
'''

from __future__ import print_function

import sys, os, binascii
from time import sleep
import json
import re
import hashlib
import webbrowser
from shutil import copy2


from PySide.QtGui import QApplication, QMessageBox, QFileDialog, \
            QInputDialog, QLineEdit
from PySide.QtCore import QObject, Slot, Signal

from utils.common import print_money, print_money2

from settings import APP_NAME, VERSION, DATA_DIR, COIN, makeDir, seed_languages
from utils.logger import log, LEVEL_ERROR, LEVEL_INFO

tray_icon_tooltip = "%s v%d.%d" % (APP_NAME, VERSION[0], VERSION[1])

wallet_dir_path = os.path.join(DATA_DIR, 'wallets')
makeDir(wallet_dir_path)

wallet_log_dir_path = os.path.join(DATA_DIR, 'logs')
makeDir(wallet_log_dir_path)

password_regex = re.compile(r"^([a-zA-Z0-9!@#\$%\^&\*]{1,256})$")
wallet_file_regex = re.compile(r"wallet_(\d+)")

from webui import LogViewer

class Hub(QObject):
    current_block_height = 0

    def __init__(self, app):
        super(Hub, self).__init__()
        self.app = app


    def setUI(self, ui):
        self.ui = ui

    def setNewWalletUI(self, new_wallet_ui):
        self.new_wallet_ui = new_wallet_ui

    @Slot()
    def import_wallet(self):
        dlg = QFileDialog(self.new_wallet_ui, "Select Import Wallet File")
        dlg.setFileMode(QFileDialog.ExistingFile)
        wallet_filename = None
        if dlg.exec_():
            wallet_filename = dlg.selectedFiles()[0]
        else:
            return

        new_wallet_file = os.path.join(wallet_dir_path, self.get_new_wallet_file_name())
        if wallet_filename:
            wallet_key_filename = wallet_filename + '.keys'

            if not os.path.exists(wallet_key_filename):
                QMessageBox.warning(self.new_wallet_ui, \
                    'Import Wallet',\
                     """Error: Key file does not exist!<br>
                     Are you sure to select correct wallet file?<br><br>
                     Hint: Wallet file often ends with .bin""")
                return False
            try:
                copy2(wallet_filename, os.path.join(wallet_dir_path, new_wallet_file))
                copy2(wallet_key_filename, os.path.join(wallet_dir_path, \
                                                           new_wallet_file + '.keys'))
            except IOError, err:
                self._detail_error_msg("Importing Wallet", "Error importing wallet!", str(err))
                self.ui.reset_wallet()
                return False

        if not os.path.exists(new_wallet_file):
            return False

        wallet_password = None
        while True:
            wallet_password, result = self._custom_input_dialog(self.new_wallet_ui, \
                "Wallet Password", "Enter password of the imported wallet:", QLineEdit.Password)
            if result:
                if not wallet_password:
                    QMessageBox.warning(self.new_wallet_ui, \
                            'Wallet Password',\
                             "You must provide password to open the imported wallet")
                else:
                    break
            else:
                return False

        self.on_new_wallet_show_progress_event.emit('Importing wallet...')
        self.app_process_events()

        ret = self.ui.wallet_rpc_manager.rpc_request.open_wallet(
                                            os.path.basename(new_wallet_file),
                                            wallet_password)

        if ret['status'] == "ERROR":
            error_message = ret['message']
            QMessageBox.critical(self.new_wallet_ui, \
                    'Error Importing Wallet',\
                    "Error: %s" % error_message)
            self.ui.reset_wallet()
            return False

        self.current_block_height = 0 # reset current wallet block height

        self.ui.wallet_info.wallet_password = hashlib.sha256(wallet_password).hexdigest()
        self.ui.wallet_info.wallet_filepath = new_wallet_file
        self.ui.wallet_info.is_loaded =True
        self.ui.wallet_info.save()

        self.show_wallet_info()
        return True


    @Slot()
    def close_new_wallet_dialog(self):
        log("Closing new wallet dialog...", LEVEL_INFO)
        self.ui.new_wallet_ui.close();
        if self.ui.wallet_info.wallet_filepath \
                    and os.path.exists(self.ui.wallet_info.wallet_filepath):
            self.ui.show_wallet();


    @Slot()
    def create_new_wallet(self):
        wallet_password = None
        wallet_filepath = ""
        try:
            has_password = False
            while True:
                wallet_password, result = self._custom_input_dialog(self.new_wallet_ui, \
                        "Wallet Password", "Set new wallet password:", QLineEdit.Password)
                if result:
                    if not password_regex.match(wallet_password):
                        QMessageBox.warning(self.new_wallet_ui, \
                            'Wallet Password',\
                             "Password must contain at least 1 character [a-zA-Z] or number [0-9]\
                                        <br>or special character like !@#$%^&* and not contain spaces")
                        continue

                    confirm_password, result = self._custom_input_dialog(self.new_wallet_ui, \
                        'Wallet Password', \
                        "Confirm wallet password:", QLineEdit.Password)
                    if result:
                        if confirm_password != wallet_password:
                            QMessageBox.warning(self.new_wallet_ui, \
                                'Wallet Password',\
                                 "Confirm password does not match password!\
                                                 <br>Please re-enter password")
                        else:
                            has_password = True
                            break
                    else:
                        break
                else:
                    break

            if has_password:
                mnemonic_seed_language = "English"
                seed_language_list = [sl[1] for sl in seed_languages]
                list_select_index = 1
                lang, ok = QInputDialog.getItem(self.new_wallet_ui, "Mnemonic Seed Language",
                            "Select a language for wallet mnemonic seed:",
                            seed_language_list, list_select_index, False)
                if ok and lang:
                    for sl in seed_languages:
                        if sl[1] == lang:
                            mnemonic_seed_language = sl[0]
                            break
                else:
                    return

                self.on_new_wallet_show_progress_event.emit("Creating wallet...")
                self.app_process_events(0.1)
                wallet_filename = self.get_new_wallet_file_name()
                wallet_filepath = os.path.join(wallet_dir_path, wallet_filename)

                while not self.ui.wallet_rpc_manager.is_ready():
                    self.app_process_events(0.1)
                ret = self.ui.wallet_rpc_manager.rpc_request.create_wallet(wallet_filename,
                                                                     wallet_password,
                                                                     mnemonic_seed_language)
                if ret['status'] == "ERROR":
                    error_message = ret['message']
                    QMessageBox.critical(self.new_wallet_ui, \
                            'Error Creating Wallet',\
                            "Error: %s" % error_message)
                    raise Exception("Error creating wallet: %s" % error_message)

                self.current_block_height = 0 # reset current wallet block height

                self.ui.wallet_info.wallet_filepath = wallet_filepath
                self.ui.wallet_info.wallet_password = hashlib.sha256(wallet_password).hexdigest()
                self.ui.wallet_info.is_loaded = True
                self.ui.wallet_info.save()

                self.show_wallet_info()
        except Exception, err:
            log(str(err), LEVEL_ERROR)
            self.ui.reset_wallet(delete_files=False)
            self.on_new_wallet_ui_reset_event.emit()
            return


    @Slot(unicode, int, unicode)
    def restore_deterministic_wallet(self, mnemonic_seed, restore_height=0, seed_offset_passphrase=u''):
        from settings.electrum_words import find_seed_language
        language_name, english_seed = find_seed_language(mnemonic_seed)
        if language_name is None:
            QMessageBox.critical(self.new_wallet_ui, \
                    'Error Restoring Wallet',\
                    """ERROR: Invalid mnemonic seed!<br>
                    Seed words missing, incorrect or not match any language<br><br>
                    NOTE: Sumokoin mnemonic seed must be a list of 26 (valid) words""")
            return

        if restore_height > 0:
            ret = QMessageBox.warning(self.new_wallet_ui, \
                    'Restore Wallet',\
                     """Are you sure to restore wallet from blockchain height# %d?<br><br>
                     WARNING: Incorrect height# will lead to incorrect balance and failed transactions!""" % restore_height, \
                     QMessageBox.Yes|QMessageBox.No, defaultButton = QMessageBox.No)
            if ret == QMessageBox.No:
                return

        wallet_password = None
        try:
            has_password = False
            while True:
                wallet_password, result = self._custom_input_dialog(self.new_wallet_ui, \
                        "Wallet Password", "Set new wallet password:", QLineEdit.Password)
                if result:
                    if not password_regex.match(wallet_password):
                        QMessageBox.warning(self.new_wallet_ui, \
                            'Wallet Password',\
                             "Password must contain at least 1 character [a-zA-Z] or number [0-9]\
                                        <br>or special character like !@#$%^&* and not contain spaces")
                        continue

                    confirm_password, result = self._custom_input_dialog(self.new_wallet_ui, \
                        'Wallet Password', \
                        "Confirm wallet password:", QLineEdit.Password)
                    if result:
                        if confirm_password != wallet_password:
                            QMessageBox.warning(self.new_wallet_ui, \
                                'Wallet Password',\
                                 "Confirm password does not match password!\
                                                 <br>Please re-enter password")
                        else:
                            has_password = True
                            break
                    else:
                        break
                else:
                    break

            if has_password:
                self.on_new_wallet_show_progress_event.emit("Restoring wallet...")
                self.app_process_events(0.1)
                wallet_filename = self.get_new_wallet_file_name()
                wallet_filepath = os.path.join(wallet_dir_path, wallet_filename)

                while not self.ui.wallet_rpc_manager.is_ready():
                    self.app_process_events(0.1)
                ret = self.ui.wallet_rpc_manager.rpc_request.restore_deterministic_wallet(english_seed,
                            restore_height, wallet_filename, seed_offset_passphrase, wallet_password, "English")
                if ret['status'] == "ERROR":
                    error_message = ret['message']
                    QMessageBox.critical(self.new_wallet_ui, \
                            'Error Restoring Wallet',\
                            "Error: %s" % error_message)
                    raise Exception("Error restoring wallet: %s" % error_message)

                ret = self.ui.wallet_rpc_manager.rpc_request.set_wallet_seed_language(language_name)
                if ret['status'] == "ERROR":
                    error_message = ret['message']
                    QMessageBox.critical(self.new_wallet_ui, \
                            'Error Restoring Wallet',\
                            "Error setting seed language: %s" % error_message)
                    raise Exception("Error restoring wallet: %s" % error_message)

                self.ui.wallet_info.wallet_filepath = wallet_filepath
                self.ui.wallet_info.wallet_password = hashlib.sha256(wallet_password).hexdigest()
                self.ui.wallet_info.is_loaded = True
                self.ui.wallet_info.save()

                self.current_block_height = 0 # reset current wallet block height
                self.ui.wallet_rpc_manager.set_ready(False)
                while not self.ui.wallet_rpc_manager.is_ready():
                    self.app_process_events(1)
                    h = self.ui.wallet_rpc_manager.get_block_height()
                    if h > 0:
                        block_hash = self.ui.wallet_rpc_manager.get_block_hash()
                        self.on_new_wallet_update_processed_block_height_event.emit(h, self.ui.current_height, block_hash)

                self.show_wallet_info()
        except Exception, err:
            log(str(err), LEVEL_ERROR)
            self.ui.reset_wallet(delete_files=False)
            return


    def _is_wallet_files_existed(self, wallet_filepath):
        return os.path.exists(wallet_filepath) and os.path.exists(wallet_filepath + ".keys")

    def get_new_wallet_file_name(self):
        wallet_files = os.listdir(wallet_dir_path)
        wallet_file_numbers = [0]
        for wf in wallet_files:
            m_file_num = wallet_file_regex.search(wf)
            if m_file_num:
                wallet_file_numbers.append(int(m_file_num.group(1)))
        return "wallet_%d.bin" % (max(wallet_file_numbers) + 1)

    @Slot()
    def rescan_spent(self):
        self.app_process_events()
        self.ui.wallet_rpc_manager.rpc_request.rescan_spent()

        # refresh wallet_info tx cache
        self.ui.wallet_info.top_tx_height = 0
        self.ui.wallet_info.bc_height = -1
        self.ui.wallet_info.wallet_transfers = []
        self.ui.update_wallet_info()

        self.on_wallet_rescan_spent_completed_event.emit()


    @Slot()
    def rescan_bc(self):
        result = QMessageBox.question(self.ui, "Rescan Blockchain", \
                                  "Rescanning blockchain can take a lot of time.<br><br>Are you sure to proceed?", \
                                   QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if result == QMessageBox.No:
            self.on_wallet_rescan_bc_completed_event.emit()
            return

        self.app_process_events()
        self.ui.wallet_rpc_manager.rpc_request.rescan_bc()

        # refresh wallet_info tx cache
        self.ui.wallet_info.top_tx_height = 0
        self.ui.wallet_info.bc_height = -1
        self.ui.wallet_info.wallet_transfers = []
        self.ui.update_wallet_info()

        self.on_wallet_rescan_bc_completed_event.emit()


    @Slot(float, str, str, int, int, str, bool, bool)
    def send_tx(self, amount, address, payment_id, priority, mixin, tx_desc, save_address, sweep_all):
        if not payment_id and not address.startswith("Sumi"):
            result = QMessageBox.question(self.ui, "Sending Coins Without Payment ID?", \
                                      "Are you sure to send coins without Payment ID?", \
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
            if result == QMessageBox.No:
                return

        if sweep_all:
            result = QMessageBox.question(self.ui, "Sending all your coins?", \
                                      "This will send all your coins to target address.<br><br>Are you sure you want to proceed?", \
                                      QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
            if result == QMessageBox.No:
                return

        wallet_password, result = self._custom_input_dialog(self.ui, \
                        "Wallet Password", "Please enter wallet password:", QLineEdit.Password)

        if not result:
            return

        if hashlib.sha256(wallet_password).hexdigest() != self.ui.wallet_info.wallet_password:
            QMessageBox.warning(self.ui, "Incorrect Wallet Password", "Wallet password is not correct!")
            return


        self.on_wallet_send_tx_start_event.emit()
        amount = int(amount*COIN)

        if sweep_all:
            _, _, per_subaddress = self.ui.wallet_rpc_manager.rpc_request.get_balance()
            subaddr_indices = []
            for s in per_subaddress:
                if s['unlocked_balance'] > 0:
                    subaddr_indices.append(s['address_index'])
            ret = self.ui.wallet_rpc_manager.rpc_request.transfer_all(address, payment_id, priority, mixin, 0, subaddr_indices)
        else:
            ret = self.ui.wallet_rpc_manager.rpc_request.transfer_split(amount, \
                                                address, payment_id, priority, mixin)

        if ret['status'] == "ERROR":
            self.on_wallet_send_tx_completed_event.emit(json.dumps(ret));
            self.app_process_events()
            if ret['message'] == "tx not possible":
                msg = "Not possible to send coins. Probably, there is not enough money left for fee."
            else:
                msg = ret['message']

            QMessageBox.critical(self.ui, \
                            'Error Sending Coins',\
                            "<b>ERROR</b><br><br>" + msg)

        if ret['status'] == "OK":
            if tx_desc:
                # set the same note for all txs:
                notes = []
                for i in range(len(ret['tx_hash_list'])):
                    notes.append(tx_desc)
                self.ui.wallet_rpc_manager.rpc_request.set_tx_notes(ret['tx_hash_list'], notes)

            self.on_wallet_send_tx_completed_event.emit(json.dumps(ret));
            self.app_process_events()

            msg = "<b>Coins successfully sent in the following transaction(s):</b><br><br>"
            for i in range(len(ret['tx_hash_list'])):
                if sweep_all:
                    msg += "- Transaction ID: %s <br>" % (ret['tx_hash_list'][i])
                else:
                    msg += "- Transaction ID: %s <br>  - Amount: %s <br>  - Fee: %s <br><br>" % (ret['tx_hash_list'][i], \
                                                        print_money2(ret['amount_list'][i]), \
                                                        print_money2(ret['fee_list'][i]))
            QMessageBox.information(self.ui, 'Coins Sent', msg)
            self.ui.update_wallet_info()

            if save_address:
                desc, _ = self._custom_input_dialog(self.ui, \
                        'Saving Address...', \
                        "Address description/note (optional):")
                ret = self.ui.wallet_rpc_manager.rpc_request.add_address_book(address, \
                                                                              payment_id, desc)
                if ret['status'] == "OK":
                    if self.ui.wallet_info.wallet_address_book:
                        address_entry = {"address": address,
                                     "payment_id": payment_id,
                                     "description": desc[0:200],
                                     "index": ret["index"]
                                     }
                        self.ui.wallet_info.wallet_address_book.append(address_entry)

                    QMessageBox.information(self.ui, "Address Saved", \
                                            "Address (and payment ID) saved to address book.")


    @Slot(int)
    def generate_payment_id(self, hex_length=16):
        payment_id = binascii.b2a_hex(os.urandom(hex_length/2))
        integrated_address = self.ui.wallet_rpc_manager.rpc_request.make_integrated_address(payment_id)["integrated_address"]
        self.on_generate_payment_id_event.emit(payment_id, integrated_address);


    @Slot(str)
    def copy_text(self, text):
        QApplication.clipboard().setText(text)


    @Slot()
    def load_address_book(self):
        if not self.ui.wallet_info.wallet_address_book:
            address_book = []
            ret = self.ui.wallet_rpc_manager.rpc_request.get_address_book()
            if ret['status'] == "OK" and "entries" in ret:
                address_book = ret["entries"]
            self.ui.wallet_info.wallet_address_book = address_book

        self.on_load_address_book_completed_event.emit( json.dumps(self.ui.wallet_info.wallet_address_book) )

    @Slot(int)
    def delete_address_book(self, index):
        result = QMessageBox.question(self.ui, "Delete Address Book Entry", \
                                      "Are you sure to delete this address?", \
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.Yes)
        if result == QMessageBox.Yes:
            ret = self.ui.wallet_rpc_manager.rpc_request.delete_address_book(index)
            if ret['status'] == "OK":
                address_book = self.ui.wallet_info.wallet_address_book
                for i in range(len(address_book)):
                    if address_book[i]['index'] == index:
                        address_book.pop(i)
                        break
        self.load_address_book()


    def _find_tx(self, transfers, tx_id, bc_height):
        if transfers["status"] == "OK":
            if "out" in transfers:
                for tx in transfers["out"]:
                    if tx['txid'] == tx_id:
                        tx["direction"] = "out"
                        tx["status"] = "out"
                        tx["confirmation"] = bc_height - tx["height"] if bc_height > tx["height"] else 0
                        return tx

            if "in" in transfers:
                for tx in transfers["in"]:
                    if tx['txid'] == tx_id:
                        tx["direction"] = "in"
                        tx["status"] = "in"
                        tx["confirmation"] = bc_height - tx["height"] if bc_height > tx["height"] else 0
                        return tx

            if "pending" in transfers:
                for tx in transfers["pending"]:
                    if tx['txid'] == tx_id:
                        tx["direction"] = "out"
                        tx["status"] = "pool"
                        tx["confirmation"] = 0
                        return tx

            if "pool" in transfers:
                for tx in transfers["pool"]:
                    if tx['txid'] == tx_id:
                        tx["direction"] = "in"
                        tx["status"] = "pool"
                        tx["confirmation"] = 0
                        return tx
        return None

    @Slot(int, str)
    def view_tx_detail(self, height, tx_id):
        if height > 0:
            transfers = self.ui.wallet_rpc_manager.rpc_request.get_transfers(filter_by_height=True, min_height=height-1, max_height=height)
        else:
            transfers = self.ui.wallet_rpc_manager.rpc_request.get_transfers(tx_pending=True, tx_in_pool=True)

        tx = self._find_tx(transfers, tx_id, self.ui.target_height)
        if not tx:
            self.on_tx_detail_found_event.emit('{"status": "ERROR"}')
            QMessageBox.warning(self.ui, "Transaction Details", "Transaction id: %s <br><br>not found!" % tx_id)
            return

        self.on_tx_detail_found_event.emit( json.dumps(tx) )


    @Slot(int)
    def load_tx_history(self, current_page=0):
        if current_page <= 0: current_page = 1
        txs_per_page = 10
        tx_start_index = (current_page - 1)*txs_per_page
        all_txs = self.ui.wallet_info.wallet_pending_transfers + self.ui.wallet_info.wallet_transfers
        txs = all_txs[tx_start_index:tx_start_index + txs_per_page]
        for tx in txs:
            tx["confirmation"] = self.ui.target_height - tx["height"] \
                if self.ui.target_height > tx["height"] and tx["height"] > 0 else 0

        num_of_pages = int(len(all_txs) + txs_per_page - 1)/txs_per_page
        pagination_slots = 10
        start_page = (int(current_page - 1)/pagination_slots)*pagination_slots + 1
        end_page = start_page + (pagination_slots - 1) \
                if start_page + (pagination_slots - 1) < num_of_pages else num_of_pages
        ret = {"txs": txs,
               "current_page": current_page,
               "num_of_pages": num_of_pages,
               "start_page": start_page,
               "end_page": end_page}

        self.on_load_tx_history_completed_event.emit( json.dumps(ret) );


    @Slot()
    def new_wallet_ui(self):
        result = QMessageBox.question(self.ui, "Open/Create New Wallet", \
                                      "<b>This will close current wallet to create/restore a new wallet!</b><br><br>Are you sure to continue?", \
                                       QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if result == QMessageBox.No:
            return

        wallet_password, result = self._custom_input_dialog(self.ui, \
                        "Wallet Password", "Please enter wallet password:", QLineEdit.Password)
        if not result:
            return

        if hashlib.sha256(wallet_password).hexdigest() != self.ui.wallet_info.wallet_password:
            QMessageBox.warning(self.ui, "Incorrect Wallet Password", "Wallet password is not correct!")
            return

        ret = self.ui.wallet_rpc_manager.rpc_request.close_wallet()
        if ret['status'] == "ERROR":
            error_message = ret['message']
            QMessageBox.critical(self.ui, \
                    'Error Closing Current Wallet',\
                    "Error: %s" % error_message)
            return

        self.current_block_height = 0
        self.ui.show_new_wallet_ui()


    @Slot()
    def open_existing_wallet(self):
        current_wallet_password, result = self._custom_input_dialog(self.ui, \
                        "Wallet Password", "Current wallet password:", QLineEdit.Password)
        if not result:
            return

        if hashlib.sha256(current_wallet_password).hexdigest() != self.ui.wallet_info.wallet_password:
            QMessageBox.warning(self.ui, "Incorrect Wallet Password", "Wallet password is not correct!")
            return

        dlg = QFileDialog(self.ui, "Open Wallet File", wallet_dir_path, "Wallet files (*.bin)")
        dlg.setFileMode(QFileDialog.ExistingFile)
        wallet_filename = None
        if dlg.exec_():
            wallet_filename = dlg.selectedFiles()[0]
        else:
            self.on_open_existing_wallet_complete_event.emit()
            return
        if not wallet_filename:
            return

        wallet_key_filename = wallet_filename + '.keys'
        if not os.path.exists(wallet_key_filename):
            QMessageBox.warning(self.ui, \
                'Open Wallet File',\
                 """Error: Key file does not exist!<br>
                 Please make sure to select correct wallet file""")
            return

        if os.path.normpath(os.path.dirname(wallet_filename)) != os.path.normpath(wallet_dir_path):
            QMessageBox.warning(self.ui, \
                'Open Wallet File',\
                 """Error: Only wallet files at default location are available for opening.<br>
                 You can import wallet via 'New... > Import' feature instead.""")
            return

        if os.path.basename(wallet_filename) == os.path.basename(self.ui.wallet_info.wallet_filepath):
            QMessageBox.warning(self.ui, \
                'Open Wallet File',\
                 """Error: Cannot open the same wallet!""")
            return

        while True:
            wallet_password, result = self._custom_input_dialog(self.ui, \
                "Wallet Password", "Enter wallet password for opening:", QLineEdit.Password)
            if result:
                if not wallet_password:
                    QMessageBox.warning(self.ui, \
                            'Wallet Password',\
                             "You must provide password to open wallet")
                    continue
                else:
                    break
            else:
                return

        self.ui.stop_update_wallet_info_timer()
        self.on_open_existing_wallet_start_event.emit()
        current_wallet_filename = self.ui.wallet_info.wallet_filepath
        try:
            ret = self.ui.wallet_rpc_manager.rpc_request.stop_wallet()
            if ret['status'] == "ERROR":
                error_message = ret['message']
                QMessageBox.critical(self.ui, \
                        'Error Closing Current Wallet',\
                        "Error: %s" % error_message)
                raise Exception(error_message)

            self.ui.wallet_rpc_manager.set_ready(False)
            self.ui.run_wallet_rpc()
            while not self.ui.wallet_rpc_manager.is_ready():
                self.app_process_events(0.1)

            ret = self.ui.wallet_rpc_manager.rpc_request.open_wallet(
                                                os.path.basename(wallet_filename),
                                                wallet_password)
            if ret['status'] == "ERROR":
                error_message = ret['message']
                QMessageBox.critical(self.ui, 'Error Opening Wallet', error_message)
                raise Exception(error_message)

            self.ui.reset_wallet(False)
            self.ui.wallet_info.wallet_password = hashlib.sha256(wallet_password).hexdigest()
            self.ui.wallet_info.wallet_filepath = wallet_filename
            self.ui.wallet_info.is_loaded =True
            self.ui.wallet_info.save()

            while not self.ui.wallet_rpc_manager.is_ready():
                self.app_process_events(0.1)
        except Exception, err:
            log(str(err), LEVEL_ERROR)
            ret = self.ui.wallet_rpc_manager.rpc_request.open_wallet(
                                                os.path.basename(current_wallet_filename),
                                                current_wallet_password)
            self.ui.wallet_info.wallet_password = hashlib.sha256(current_wallet_password).hexdigest()
            self.ui.wallet_info.wallet_filepath = current_wallet_filename
            self.ui.wallet_info.is_loaded =True
            self.ui.wallet_info.save()
            self.on_open_existing_wallet_complete_event.emit()
        finally:
            self.ui.start_update_wallet_info_timer()


    @Slot(int)
    def view_wallet_key(self, key_type):
        wallet_password, result = self._custom_input_dialog(self.ui, \
                        "Wallet Password", "Please enter wallet password:", QLineEdit.Password)
        if not result:
            self.on_view_wallet_key_completed_event.emit("", "");
            return

        if hashlib.sha256(wallet_password).hexdigest() != self.ui.wallet_info.wallet_password:
            self.on_view_wallet_key_completed_event.emit("", "");
            QMessageBox.warning(self.ui, "Incorrect Wallet Password", "Wallet password is not correct!")
            return

        title = None
        if key_type == 1:
            passphrase, result = self._custom_input_dialog(self.ui, \
                "Seed Offset Passphrase (Optional)",
                "Enter optional seed offset passphrase (just leave it blank to see <br>original, unencrypted seed):",
                QLineEdit.Password)
            if result:
                if passphrase:
                    confirm_passphrase, result = self._custom_input_dialog(self.ui, \
                        "Confirm Passphrase",
                        "Confirm seed offset passphrase:",
                        QLineEdit.Password)
                    if confirm_passphrase != passphrase:
                        QMessageBox.warning(self.ui,
                            'Confirm Passphrase Not Match',
                            "Confirm passphrase does not match passphrase!")
                        return
            else:
                return

            if not passphrase:
                passphrase = ""
            title = "Wallet Mnemonic Seed"
            ret = self.ui.wallet_rpc_manager.rpc_request.query_key("mnemonic", passphrase)
        elif key_type == 2:
            title = "Wallet Viewkey"
            ret = self.ui.wallet_rpc_manager.rpc_request.query_key("view_key")
        elif key_type == 3:
            title = "Wallet Spendkey"
            ret = self.ui.wallet_rpc_manager.rpc_request.query_key("spend_key")
        else:
            QMessageBox.critical(self.ui, "Unknown Key Type", "Unknown key type");
            return

        self.on_view_wallet_key_completed_event.emit(title, ret)

    @Slot()
    def change_wallet_password(self):
        old_password, result = self._custom_input_dialog(self.ui, \
                        "Wallet Password", "Enter current wallet password:", QLineEdit.Password)
        if not result:
            return

        if hashlib.sha256(old_password).hexdigest() != self.ui.wallet_info.wallet_password:
            self.on_view_wallet_key_completed_event.emit("", "");
            QMessageBox.warning(self.ui, "Incorrect Wallet Password", "Wallet password is not correct!")
            return

        new_password = None
        while True:
            new_password, result = self._custom_input_dialog(self.ui, \
                    "Wallet New Password", "Set new wallet password:", QLineEdit.Password)
            if result:
                if not password_regex.match(new_password):
                    QMessageBox.warning(self.ui, \
                        'Wallet New Password',\
                         "Password must contain at least 1 character [a-zA-Z] or number [0-9]\
                                    <br>or special character like !@#$%^&* and not contain spaces")
                    continue

                confirm_password, result = self._custom_input_dialog(self.ui, \
                    'Wallet New Password', \
                    "Confirm new wallet password:", QLineEdit.Password)
                if result:
                    if confirm_password != new_password:
                        QMessageBox.warning(self.ui, \
                            'Wallet New Password',\
                             "Confirm password does not match new password!\
                                             <br>Please re-enter password")
                        continue
                    else:
                        break
                else:
                    return
            else:
                return

        if new_password is not None:
            if new_password == old_password:
                QMessageBox.information(self.ui, "Wallet Password",
                "New wallet password is the same as old one. Nothing changed!")
                return

            ret = self.ui.wallet_rpc_manager.rpc_request.change_wallet_password(old_password, new_password)
            if ret['status'] == "ERROR":
                error_message = ret['message']
                QMessageBox.critical(self.ui, \
                        'Error Changing Wallet Password',\
                        "Error: %s" % error_message)
                return

            self.ui.wallet_info.wallet_password = hashlib.sha256(new_password).hexdigest()
            self.ui.wallet_info.save()

            QMessageBox.information(self.ui, "Wallet Password Changed",
                "Wallet password successfully changed!<br>Please make sure you never lose it.")


    @Slot(int)
    def set_daemon_log_level(self, level):
        # save log level
        self.ui.app_settings.settings['daemon']['log_level'] = level
        self.ui.app_settings.save()


    @Slot(int)
    def set_block_sync_size(self, sync_size):
        self.ui.app_settings.settings['daemon']['block_sync_size'] = sync_size
        self.ui.app_settings.save()

    @Slot()
    def load_app_settings(self):
        self.on_load_app_settings_completed_event.emit( json.dumps(self.ui.app_settings.settings) )

    @Slot()
    def about_app(self):
        self.ui.about()

    @Slot(str)
    def open_link(self, link):
        webbrowser.open(link)

    @Slot()
    def restart_daemon(self):
        self.app_process_events(0.1)
        self.ui.sumokoind_daemon_manager.stop()
        self.ui.start_deamon()
        while True:
            sumokoind_info = self.ui.daemon_rpc_request.get_info()
            if sumokoind_info['status'] == "OK":
                break;
            self.app_process_events(1)
        self.on_restart_daemon_completed_event.emit()


    @Slot()
    def view_daemon_log(self):
        log_file = os.path.join(DATA_DIR, 'logs', "sumokoind.log")
        log_dialog = LogViewer(parent=self.ui, log_file=log_file)
        log_dialog.load_log()


    @Slot(str)
    def copy_seed(self, seed):
        self.copy_text(seed)
        QMessageBox.information(self.new_wallet_ui, "Wallet Mnemonic Seed Copied", \
                            """Wallet mnemonic seed words have been copied!<br><br>
                            Please save them to a safe place for wallet restoration<br>
                            in case you forget wallet password or computer failure etc.""")

    @Slot()
    def paste_seed_words(self):
        text = QApplication.clipboard().text()
        self.on_paste_seed_words_event.emit(text)

    @Slot()
    def update_wallet_loading_height(self):
        if self.ui.wallet_rpc_manager is None:
            return

        h = self.ui.wallet_rpc_manager.get_block_height()
        if h > self.current_block_height:
            self.ui.stop_update_wallet_info_timer()
            block_hash = self.ui.wallet_rpc_manager.get_block_hash()
            self.on_update_wallet_loading_height_event.emit(h, self.ui.current_height, block_hash)
            self.current_block_height = h
        else:
            self.ui.start_update_wallet_info_timer()

    @Slot(bool)
    def change_minimize_to_tray(self, status):
        self.ui.close_to_system_tray = status
        self.ui.app_settings.settings['application']['minimize_to_tray'] = status
        self.ui.app_settings.save()

    @Slot(int)
    def change_limit_rate_up(self, limit_rate_up):
        self.ui.app_settings.settings['daemon']['limit_rate_up'] = limit_rate_up
        self.ui.app_settings.save()


    @Slot(int)
    def change_limit_rate_down(self, limit_rate_down):
        self.ui.app_settings.settings['daemon']['limit_rate_down'] = limit_rate_down
        self.ui.app_settings.save()


    def update_daemon_status(self, status):
        self.on_daemon_update_status_event.emit(status)


    def app_process_events(self, seconds=1):
        for _ in range(int(seconds*10)):
            self.app.processEvents()
            sleep(.1)



    def _detail_error_msg(self, title, error_text, error_detailed_text):
        msg = QMessageBox(self.new_wallet_ui)
        msg.setWindowTitle(title)
        msg.setText(error_text)
        msg.setInformativeText("Detailed error information below:")
        msg.setDetailedText(error_detailed_text)
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def _custom_input_dialog(self, ui, title, label,
                             text_echo_mode=QLineEdit.Normal,
                             input_mode=QInputDialog.TextInput):
        dlg = QInputDialog(ui)
        dlg.setTextEchoMode(text_echo_mode)
        dlg.setInputMode(input_mode)
        dlg.setWindowTitle(title)
        dlg.setLabelText(label)
        dlg.resize(250, 100)
        result = dlg.exec_()
        text = dlg.textValue()
        return (text, result)


    def show_wallet_info(self):
        wallet_rpc_request = self.ui.wallet_rpc_manager.rpc_request
        wallet_info = {}
        ret = wallet_rpc_request.get_address()
        if ret['status'] == "OK" and 'address' in ret:
            wallet_info['address'] = ret['address']
        else:
            wallet_info['address'] = ""
        wallet_info['seed'] = wallet_rpc_request.query_key(key_type="mnemonic")
        wallet_info['view_key'] = wallet_rpc_request.query_key(key_type="view_key")
        balance, unlocked_balance, _ = wallet_rpc_request.get_balance()
        wallet_info['balance'] = print_money(balance)
        wallet_info['unlocked_balance'] = print_money(unlocked_balance)

        self.on_new_wallet_show_info_event.emit(json.dumps(wallet_info))


    on_new_wallet_show_info_event = Signal(str)
    on_new_wallet_show_progress_event = Signal(str)
    on_new_wallet_ui_reset_event = Signal()
    on_new_wallet_update_processed_block_height_event = Signal(int, int, str)

    on_daemon_update_status_event = Signal(str)
    on_main_wallet_ui_reset_event = Signal()
    on_wallet_update_info_event = Signal(str)
    on_wallet_rescan_spent_completed_event = Signal()
    on_wallet_rescan_bc_completed_event = Signal()
    on_wallet_send_tx_completed_event = Signal(str)
    on_generate_payment_id_event = Signal(str, str)
    on_load_address_book_completed_event = Signal(str)
    on_tx_detail_found_event = Signal(str)
    on_load_tx_history_completed_event = Signal(str)
    on_view_wallet_key_completed_event = Signal(str, str)
    on_load_app_settings_completed_event = Signal(str)
    on_restart_daemon_completed_event = Signal()
    on_paste_seed_words_event = Signal(str)
    on_update_wallet_loading_height_event = Signal(int, int, str)
    on_open_existing_wallet_start_event = Signal()
    on_open_existing_wallet_complete_event = Signal()
    on_wallet_send_tx_start_event = Signal()
