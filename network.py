from protocol import Protocol
from socket import *
import pickle


class Network():
    def __init__(self):
        self.ip_addr = "127.0.0.1"
        self.port = 8082

        self.clientSock = socket(AF_INET, SOCK_STREAM)
        self.clientSock.connect((self.ip_addr, self.port))
        self.player = 0
        self.counter_player = 0
        self.match = False
        self.game = 0
        self.init = 0
        self.Connetion_establish = 0
        self.protocol = Protocol()

    def Request(self):
        print("Request: ", self.protocol.command)
        send_msg = pickle.dumps(self.protocol)
        self.clientSock.sendall(send_msg)

    def Receive(self) -> Protocol:
        data = self.clientSock.recv(4096)
        response_msg = pickle.loads(data)
        return response_msg

    # 서버와 연결 후 자기가 몇번째 플레어이언지 확인
    def CheckConnetion(self):
        self.protocol.command = "ConnChk"
        print("Command 1  ", self.protocol.command)
        self.Request()
        response_msg = self.Receive()
        print("receive return")
        print("Command: ", response_msg.command)
        print("Game: ", response_msg.game)
        if response_msg.command == "ConnChk":
            self.Connetion_establish += 1

            self.player = response_msg.player
            self.game = int((int(self.player)+1) / 2)
        print("chkconn  ", self.Connetion_establish)

    # 서버에 다른 클라이언트가 연결 되었는지 확인,
    # 되었으면 게임 시작
    def CheckSession(self):
        self.protocol.command = "SessChk"
        self.Request()
        response_msg = self.Receive()

        print(response_msg.player)
        if response_msg.command == "SessChk":
            if int(response_msg.player) % 2 == 0:
                self.match = True
                return True
        return False

    def Update(self):
        self.protocol.command = "Update"
        print("Command  ", self.protocol.command)
        self.Request()
        return self.Receive()

    def DisconnectSession(self):
        self.protocol.command = "bye"
        self.Request()
        self.clientSock.close()
