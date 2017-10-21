#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
QSingleApplication is a wrapper class for creating single interface
of appliaction
'''

from __future__ import print_function
import sys, os


from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QIODevice, QTimer
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

from utils.common import getSockDir, makeDir

DATA_DIR = makeDir(os.path.join(getSockDir(), 'SumokoinGUIWallet'))

class QSingleApplication(QApplication):
    sock_file = 'sumokoin_wallet_sock'
    if sys.platform == 'win32':
        sock_file = "\\\\.\\pipe\\%s" % sock_file
    elif sys.platform == 'darwin':
        sock_file = os.path.join(DATA_DIR, '.%s' % sock_file)
    else:
        sock_file = os.path.join(getSockDir(), sock_file)

    def singleStart(self, appMain):
        self.appMain = appMain
        # Socket
        self.m_socket = QLocalSocket()
        self.m_socket.connected.connect(self.connectToExistingApp)
        self.m_socket.error.connect(lambda:self.startApplication(first_start=True))
        self.m_socket.connectToServer(self.sock_file, QIODevice.WriteOnly)

    def connectToExistingApp(self):
        # Quit application in 250 ms
        QTimer.singleShot(250, self.quit)
        print( "App is already running.", file=sys.stderr )


    def startApplication(self, first_start=True):
        self.m_server = QLocalServer()
        if self.m_server.listen(self.sock_file):
            print( "Starting app..." )
            self.appMain.run()
        else:
            if not first_start:
                print( "Error listening the socket. App can't start!", file=sys.stderr )
                QTimer.singleShot(250, self.quit)
                return

            # remove the listener path file and try to restart app one more time
            print( "Error listening the socket. Try to restart application...", file=sys.stderr )
            if sys.platform != 'win32':
                try:
                    os.unlink(self.sock_file)
                except Exception as err:
                    print( err, file=sys.stderr )

            QTimer.singleShot(250, lambda : self.startApplication(first_start=False))

    def getNewConnection(self):
        self.new_socket = self.m_server.nextPendingConnection()
        self.new_socket.readyRead.connect(self.readSocket)

    def readSocket(self):
        f = self.new_socket.readLine()
        self.appMain.processURLProtocol(str(f))
