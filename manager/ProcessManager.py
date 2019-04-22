#!/usr/bin/python
# -*- coding: utf-8 -*-
# # Copyright (c) 2017-2019, The Sumokoin Project (www.sumokoin.org)

'''
Process managers for sumokoind, sumo-wallet-cli and sumo-wallet-rpc
'''

from __future__ import print_function

import sys, os
import re
from subprocess import Popen, PIPE, STDOUT
import signal
from threading import Thread
from time import sleep
from uuid import uuid4

from utils.logger import log, LEVEL_DEBUG, LEVEL_ERROR, LEVEL_INFO

from rpc import WalletRPCRequest

file_system_encoding = sys.getfilesystemencoding()

class ProcessManager(Thread):
    def __init__(self, exec_path, proc_args, proc_name=""):
        super(ProcessManager, self).__init__()
        args = proc_args.split(u' ')
        args.insert(0, exec_path)
        args_array = [a.encode(file_system_encoding) for a in args]
        self.proc = Popen(args_array,
                          shell= True if sys.platform in ['win32','cygwin','win64'] else False,
                          stdout=PIPE, stderr=STDOUT, stdin=PIPE)
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


    def get_pid(self):
        return self.proc.pid

    def is_proc_running(self):
        return (self.proc.poll() is None)



class SumokoindManager(ProcessManager):
    def __init__(self, resources_path, log_level=1, block_sync_size=20, limit_rate_up=2048, limit_rate_down=8192):
        exec_path = u'%s/bin/sumokoind' % resources_path
        proc_args = u'--log-level=%d --block-sync-size=%d --limit-rate-up=%d --limit-rate-down=%d' % (log_level, block_sync_size, limit_rate_up, limit_rate_down)
        super(SumokoindManager, self).__init__(exec_path, proc_args, "sumokoind")

    def run(self):
        err_str = "ERROR"
        for line in iter(self.proc.stdout.readline, b''):
            if err_str in line:
                self.last_error = line.rstrip()
                log("[%s] %s" % (self.proc_name, line.rstrip()), LEVEL_ERROR, self.proc_name)
            else:
                log("[%s] %s" % (self.proc_name, line.rstrip()), LEVEL_DEBUG, self.proc_name)

        if not self.proc.stdout.closed:
            self.proc.stdout.close()


    def stop(self):
        try:
            self.send_command("exit")
            counter = 1
            while self.is_proc_running():
                if counter < 60:
                    if counter % 5 == 0:
                        self.send_command("exit")
                    sleep(1)
                    counter += 1
                else:
                    self.proc.kill()
                    log("[%s] killed" % self.proc_name, LEVEL_INFO, self.proc_name)
                    break
        except:
            pass
        log("[%s] stopped" % self.proc_name, LEVEL_INFO, self.proc_name)



class WalletRPCManager(ProcessManager):
    def __init__(self, resources_path, wallet_dir_path, app, log_level=1):
        self.rpc_user_name = str(uuid4().hex)[:12]
        self.rpc_password = str(uuid4().hex)[:12]
        wallet_log_dir_path = os.path.abspath(os.path.join(wallet_dir_path, ".." , "logs", "sumo-wallet-rpc-bin.log"))
        exec_path = u'%s/bin/sumo-wallet-rpc' % resources_path
        wallet_rpc_args = u'--rpc-bind-port=19738 --wallet-dir=%s --log-file=%s --rpc-login=%s:%s --log-level=%d' \
                                                % (wallet_dir_path, wallet_log_dir_path, self.rpc_user_name, self.rpc_password, log_level)
        super(WalletRPCManager, self).__init__(exec_path, wallet_rpc_args, "sumo-wallet-rpc")
        self.rpc_request = WalletRPCRequest(app, self.rpc_user_name, self.rpc_password)

        self._ready = False
        self._block_height = 0
        self._block_hash = None
        self._stopped = False

    def run(self):
        rpc_ready_strs = ["Binding on 127.0.0.1", "Starting wallet rpc server", "Run net_service loop", "Refresh done"]
        err_str = "ERROR"
        height_regex = re.compile(r"Processed block: \<([a-z0-9]+)\>, height (\d+)")

        for line in iter(self.proc.stdout.readline, b''):
            m_height = height_regex.search(line)
            if m_height:
                self._block_hash = m_height.group(1)
                self._block_height = m_height.group(2)
                self._ready = False

            if not self._ready and any(s in line for s in rpc_ready_strs):
                self._ready = True
                log("[%s] Ready!" % self.proc_name, LEVEL_INFO, self.proc_name)

            if err_str in line:
                self.last_error = line.rstrip()
                log("[%s] %s" % (self.proc_name, line.rstrip()), LEVEL_ERROR, self.proc_name)
            elif m_height:
                log("[%s] %s" % (self.proc_name, line.rstrip()), LEVEL_DEBUG, self.proc_name)
            else:
                log("[%s] %s" % (self.proc_name, line.rstrip()), LEVEL_DEBUG, self.proc_name)
            if self._stopped:
                break

#         if not self.proc.stdout.closed:
#             self.proc.stdout.close()

    def is_ready(self):
        return self._ready

    def set_ready(self, status):
        self._ready = status

    def get_block_height(self):
        return int(self._block_height)

    def get_block_hash(self):
        return self._block_hash

    def reset_block_height(self):
        self._block_height = 0

    def stop(self):
        self._stopped = True
        self.rpc_request.stop_wallet(no_wait=True)
        sleep(2)
        counter = 1
        while self.is_proc_running():
            try:
                if counter < 30:
                    if counter % 5 == 0:
                        if hasattr(signal, 'CTRL_C_EVENT'):
                            try:
                                os.kill(self.proc.pid, signal.CTRL_C_EVENT)
                            except KeyboardInterrupt:
                                pass
                        else:
                            os.kill(self.proc.pid, signal.SIGINT)
                    sleep(1)
                    counter += 1
                else:
                    self.proc.kill()
                    log("[%s] killed" % self.proc_name, LEVEL_INFO, self.proc_name)
                    break
            except:
                break
        log("[%s] stopped" % self.proc_name, LEVEL_INFO, self.proc_name)

