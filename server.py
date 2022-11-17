from re import M
from socket import *
from threading import Thread
from threading import Lock
import json


class Shared(object):
    current_shared = 0
    player_data = [""]


class ClientThread(Thread):

    # lock = Lock()

    def __init__(self, clientAddress, clientsocket, shared):
        Thread.__init__(self)
        super(ClientThread, self).__init__()

        self.clientAddress = clientAddress
        self.clientsocket = clientsocket
        self.request_msg = "initialized"
        self.lock = Lock()
        self.shared = shared

        with self.lock:
            self.shared.current_shared += 1
        print("New connection added: ", clientAddress)

        self.player = self.shared.current_shared
        if self.player % 2 == 1:
            self.counter_player = self.player + 1
        else:
            self.counter_player = self.player - 1

    def run(self):
        print("Connection from : ", self.clientAddress)
        while True:
            data = self.clientsocket.recv(1024)
            response_msg = data.decode("ascii")
            print("receive, ", response_msg)
            arg = response_msg.split('#')
            if arg[0] == "ConnChk":
                print(self.shared.current_shared)
                self.request_msg = self.CheckConnection()
            if arg[0] == "SessChk":
                self.request_msg = self.CheckSession()
            if arg[0] == "update":
                self.request_msg = self.Update(response_msg)
            if arg[0] == "bye":
                break
            print("shared  ", self.shared.current_shared)

            # request_msg = "[REFLECT}"+response_msg

            print("To client: ", self.request_msg)
            self.Request(self.request_msg)

        print("Client at ", self.clientAddress, " disconnected...")
        with self.lock:
            self.shared.current_shared -= 1
        print(self.shared.current_shared)

    def CheckConnection(self):
        request_msg = "ConnChk#OK"
        return request_msg

    def CheckSession(self):
        request_msg = "SessChk#" + str(self.shared.current_shared)
        return request_msg

    def Update(self, response_msg):

        request_msg = response_msg
        self.lock.acquire()
        self.shared.player_data[self.player - 1] = request_msg
        request_msg += self.shared.player_data[self.counter_player - 1]
        print("request,  ", request_msg)
        self.clientsocket.send(request_msg.encode('ascii'))
        self.lock.release()

    def Request(self, request_msg):

        print(request_msg)
        request_msg = str(self.player) + "#" + request_msg + "#"
        self.lock.acquire()
        print("request,  ", request_msg)
        self.clientsocket.send(request_msg.encode('ascii'))
        self.lock.release()


serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', 8082))
serverSock.listen(1)

shared = Shared()

while True:
    serverSock.listen(1)
    clientsock, clientAddress = serverSock.accept()
    newthread = ClientThread(clientAddress, clientsock, shared)
    newthread.start()
