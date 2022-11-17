
from socket import *


class Network():
    def __init__(self):
        self.ip_addr = "127.0.0.1"
        self.port = 8082

        self.clientSock = socket(AF_INET, SOCK_STREAM)
        self.clientSock.connect((self.ip_addr, self.port))
        self.player = 0
        self.match = False
        self.game = 0
        self.init = 0
        self.Connetion_establish = 0

    def Request(self, msg):
        msg = str(msg)
        self.clientSock.send(msg.encode('ascii'))

    def Receive(self):
        result = ""
        data = self.clientSock.recv(1024)
        response_msg = data.decode("ascii")
        print("raw,  ", response_msg)
        # response_msg = response_msg[:int(len(response_msg)/2)]

        player = response_msg[0]
        print(response_msg)
        print(player)
        if player == 0:
            pass
        else:
            if player == self.player:
                print(response_msg.split('#'))
        return response_msg.split('#')

    def CheckConnetion(self):
        request_msg = "ConnChk" + "#" + self.ip_addr
        self.Request(request_msg)
        response_msg = self.Receive()
        print("receive return  ", response_msg)
        if response_msg[1] == "ConnChk":
            self.Connetion_establish += 1
            self.player = response_msg[0]
            self.game = int((int(self.player)+1) / 2)
        print("chkconn  ", self.Connetion_establish)

    def CheckSession(self):
        request_msg = "SessChk" + "#" + str(self.port)
        self.Request(request_msg)
        response_msg = self.Receive()

        print(response_msg[0], response_msg[1], response_msg[2])
        if response_msg[1] == "SessChk":
            if int(response_msg[2]) % 2 == 0:
                self.match = True
                return True
        return False

    def UpdataPaddle(self, my_paddle):
        print(my_paddle[0], my_paddle[1])

    def DisconnectSession(self):
        self.Request("bye")
