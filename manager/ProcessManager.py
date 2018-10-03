#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)

'''
Process managers for sumokoind, sumo-wallet-cli and sumo-wallet-rpc
'''

from __future__ import print_function

import sys, os
import re
from subprocess import Popen, PIPE, STDOUT
import signal
from threading import Thread
from multiprocessing import Process, Event
from time import sleep
from uuid import uuid4

from utils.logger import log, LEVEL_DEBUG, LEVEL_ERROR, LEVEL_INFO

from rpc import WalletRPCRequest

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # disable creating the window
DETACHED_PROCESS = 0x00000008  # forcing the child to have no console at all

class ProcessManager(Thread):
    def __init__(self, proc_args, proc_name=""):
        Thread.__init__(self)
        args_array = proc_args.encode( sys.getfilesystemencoding() ).split(u' ')
        self.proc = Popen(args_array,
                          shell=False, 
                          stdout=PIPE, stderr=STDOUT, stdin=PIPE, 
                          creationflags=CREATE_NO_WINDOW)
        self.proc_name = proc_name
        self.daemon = True
        log("[%s] started" % proc_name, LEVEL_INFO, self.proc_name)
    
    def run(self):
        for line in iter(self.proc.stdout.readline, b''):
            log(">>> " + line.rstrip(), LEVEL_DEBUG, self.proc_name)
        
        if not self.proc.stdout.closed:
            self.proc.stdout.close()
            
    def send_command(self, cmd):
        self.proc.stdin.write( (cmd + u"\n").encode("utf-8") )
        sleep(0.1)
    
        
    def stop(self):
        if self.is_proc_running():
            try:
                self.send_command('exit')
                #self.proc.stdin.close()
                counter = 0
                while True:
                    if self.is_proc_running():
                        if counter < 30:
                            if counter == 10:
                                try:
                                    self.send_command('exit')
                                except:
                                    pass
                            sleep(1)
                            counter += 1
                        else:
                            self.proc.kill()
                            log("[%s] killed" % self.proc_name, LEVEL_INFO, self.proc_name)
                            break
                    else:
                        break
                log("[%s] stopped" % self.proc_name, LEVEL_INFO, self.proc_name)
            except IOError:
                pass
        
    
    def is_proc_running(self):
        return (self.proc.poll() is None)
    

class SumokoindManager(ProcessManager):
    def __init__(self, resources_path, log_level=0, block_sync_size=20, limit_rate_up=2048, limit_rate_down=8192):
        proc_args = u'%s/bin/sumokoind --log-level %d --block-sync-size %d --limit-rate-up %d --limit-rate-down %d' % (resources_path, log_level, block_sync_size, limit_rate_up, limit_rate_down)
        ProcessManager.__init__(self, proc_args, "sumokoind")
        self.synced = Event()
        self.stopped = Event()
        
    def run(self):
        err_str = "ERROR"
        for line in iter(self.proc.stdout.readline, b''):
            if err_str in line:
                self.last_error = line.rstrip()
                log("[%s]>>> %s" % (self.proc_name, line.rstrip()), LEVEL_ERROR, self.proc_name)
            else:
                log("[%s]>>> %s" % (self.proc_name, line.rstrip()), LEVEL_INFO, self.proc_name)
        
        if not self.proc.stdout.closed:
            self.proc.stdout.close()
        
        self.stopped.set()

class WalletCliManager(ProcessManager):
    fail_to_connect_str = "wallet failed to connect to daemon"
    
    def __init__(self, resources_path, wallet_file_path, wallet_log_dir_path, restore_wallet=False, restore_height=0):
        if not restore_wallet:
            wallet_args = u'%s/bin/sumo-wallet-cli --generate-new-wallet=%s --log-file=%s' \
                                                % (resources_path, wallet_file_path, wallet_log_dir_path)
        else:
            wallet_args = u'%s/bin/sumo-wallet-cli --restore-deterministic-wallet --restore-height %d --generate-new-wallet=%s --log-file=%s --daemon-port 99999' \
                                                % (resources_path, restore_height, wallet_file_path, wallet_log_dir_path)
        ProcessManager.__init__(self, wallet_args, "sumo-wallet-cli")
        self._ready = Event()
        self.last_error = ""
        self.block_height = 0
        self.top_height = 0
        
    def run(self):
        height_regex = re.compile(r"Height (\d+) / (\d+)")
        is_ready_str = "Background refresh thread started"
        err_str = "Error:"
        for line in iter(self.proc.stdout.readline, b''):
            m_height = height_regex.search(line)
            if m_height: 
                self.block_height = int(m_height.group(1))
                self.top_height = int(m_height.group(2))
            
            if not self._ready.is_set() and is_ready_str in line:
                self._ready.set()
                log("[%s]>>> %s" % (self.proc_name, line.rstrip()), LEVEL_INFO, self.proc_name)
                log("[%s]>>> %s" % (self.proc_name, "Wallet ready!") , LEVEL_INFO, self.proc_name)
            
            if err_str in line:
                self.last_error = line.rstrip()
                log("[%s]>>> %s" % (self.proc_name, line.rstrip()), LEVEL_ERROR, self.proc_name)
            elif m_height:
                log("[%s]>>> %s" % (self.proc_name, line.rstrip()), LEVEL_INFO, self.proc_name)
#             else:
#                 log("[%s]>>> %s" % (self.proc_name, line.rstrip()), LEVEL_DEBUG, self.proc_name)
        
        if not self.proc.stdout.closed:
            self.proc.stdout.close()
    
    def is_ready(self):
        return self._ready.is_set()
            
    
    def is_connected(self):
        self.send_command("refresh")
        if self.fail_to_connect_str in self.last_error:
            return False
        return True
    


class WalletRPCManager(ProcessManager):
    def __init__(self, resources_path, wallet_file_path, wallet_password, app, log_level=1):
        self.rpc_user_name = str(uuid4().hex)[:12]
        self.rpc_password = str(uuid4().hex)[:12]
        wallet_log_dir_path = os.path.join(os.path.dirname(wallet_file_path), ".." , "logs", "sumo-wallet-rpc-bin.log")
        wallet_rpc_args = u'%s/bin/sumo-wallet-rpc --wallet-file %s --log-file %s --rpc-bind-port 19738 --rpc-login %s:%s --prompt-for-password --log-level %d' \
                                            % (resources_path, wallet_file_path, wallet_log_dir_path, self.rpc_user_name, self.rpc_password, log_level)
                                                                                
        ProcessManager.__init__(self, wallet_rpc_args, "sumo-wallet-rpc")
        sleep(0.2)
        self.send_command(wallet_password)
        
        self.rpc_request = WalletRPCRequest(app, self.rpc_user_name, self.rpc_password)
#         self.rpc_request.start()
        self._ready = Event()
        self.block_height = 0
        self.is_password_invalid = Event()
        self.last_log_lines = []
    
    def run(self):
        rpc_ready_strs = ["Binding on 127.0.0.1", "Starting wallet rpc server", "Run net_service loop", "Refresh done"]
        err_str = "ERROR"
        invalid_password_str = "invalid password"
        height_regex = re.compile(r"Processed block: \<([a-z0-9]+)\>, height (\d+)")
        height_regex2 = re.compile(r"Skipped block by height: (\d+)")
        height_regex3 = re.compile(r"Skipped block by timestamp, height: (\d+)")
        
        for line in iter(self.proc.stdout.readline, b''):
            m_height = height_regex.search(line)
            if m_height: self.block_height = m_height.group(2)
            if not m_height:
                m_height = height_regex2.search(line)
                if m_height: self.block_height = m_height.group(1)
            if not m_height:
                m_height = height_regex3.search(line)
                if m_height: self.block_height = m_height.group(1)
                
            if not self._ready.is_set() and any(s in line for s in rpc_ready_strs):
                self._ready.set()
                log("RPC server ready!", LEVEL_INFO, self.proc_name)
            
            if err_str in line:
                self.last_error = line.rstrip()
                log(line.rstrip(), LEVEL_ERROR, self.proc_name)
                if not self.is_password_invalid.is_set() and invalid_password_str in self.last_error:
                    self.is_password_invalid.set()
            elif m_height:
                log(line.rstrip(), LEVEL_INFO, self.proc_name)
            else:
                log(line.rstrip(), LEVEL_DEBUG, self.proc_name)
            
            if len(self.last_log_lines) > 1:
                self.last_log_lines.pop(0)
            self.last_log_lines.append(line.rstrip())
            
        
        if not self.proc.stdout.closed:
            self.proc.stdout.close()
            
    def is_ready(self):
        return self._ready.is_set()
    
    def is_invalid_password(self):
        return self.is_password_invalid.is_set()
    
    def stop(self):
        self.rpc_request.stop_wallet()
        if self.is_proc_running():
            counter = 0
            while True:
                if self.is_proc_running():
                    if counter < 5:
                        sleep(1)
                        counter += 1
                    else:
                        self.proc.kill()
                        log("[%s] killed" % self.proc_name, LEVEL_INFO, self.proc_name)
                        break
                else:
                    break
        self._ready = Event()
        log("[%s] stopped" % self.proc_name, LEVEL_INFO, self.proc_name)        
        
