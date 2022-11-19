from re import M
from socket import *
from threading import Thread
from threading import Lock
from protocol import Protocol
import pickle
from queue import Queue
from pygame import time


class ClientThread(Thread):
    num_connection: int = 0
    lock = Lock()

    def __init__(self, clientAddress, clientsocket, my_q: Queue, other_q: Queue):
        Thread.__init__(self)

        self.clientAddress = clientAddress
        self.clientsocket: socket = clientsocket
        self.request_msg = ""

        self.clock = time.Clock()
        self.protocol = Protocol()

        # with ClientThread.lock:
        print("New connection added: ", clientAddress)

        self.my_q: Queue = my_q
        self.other_q: Queue = other_q

        self.player = ClientThread.num_connection
        if self.player % 2 == 1:
            self.counter_player = self.player + 1
        else:
            self.counter_player = self.player - 1

    def run(self):
        print("Connection from : ", self.clientAddress)
        while True:
            self.clock.tick(60)
            response_msg = self.Receive()
            print("receive, ", response_msg)

            if response_msg.command == "ConnChk":
                print(ClientThread.num_connection)
                self.CheckConnection()
            if response_msg.command == "SessChk":
                self.CheckSession()
            if response_msg.command == "Update":
                self.Update(response_msg)
            if response_msg.command == "bye":
                print(response_msg.player)
                break

            print("shared  ", ClientThread.num_connection)

            # request_msg = "[REFLECT}"+response_msg

            # print("To client: ", self.request_msg)
            self.Request()

        print("Client at ", self.clientAddress, " disconnected...")
        with ClientThread.lock:
            ClientThread.num_connection -= 1
        print(ClientThread.num_connection)

    def CheckConnection(self):
        self.protocol.command = "ConnChk"
        ClientThread.num_connection += 1
        self.protocol.player = ClientThread.num_connection
        print("num con", ClientThread.num_connection)

    def CheckSession(self):
        self.protocol.command = "SessChk"
        self.protocol.player = ClientThread.num_connection

        print("num con", ClientThread.num_connection)

    def Update(self, response_msg: Protocol):
        player = response_msg.player
        print("UPDATE")
        ClientThread.lock.acquire()
        self.protocol.command = "Updata"
        try:
            self.my_q.put(response_msg)
            other_q: Protocol = self.other_q.get(timeout=0.1)
        except Exception as e:
            other_q: Protocol = response_msg
            print(e)

        self.protocol.other_paddle_x = other_q.my_paddle_x
        self.protocol.other_paddle_y = other_q.my_paddle_y
        # self.protocol.other_paddle_x, self.protocol.other_paddle_y = Shared.GetOtherPaddle(
        #     response_msg.player)

        print("Other  ", self.protocol.other_paddle_x,
              self.protocol.other_paddle_y)

        print("request,  ", self.protocol.command)
        ClientThread.lock.release()

    def Request(self):
        ClientThread.lock.acquire()
        print("request,  ", self.protocol)
        send_msg = pickle.dumps(self.protocol)
        self.clientsocket.send(send_msg)
        ClientThread.lock.release()

    def Receive(self) -> Protocol:
        data = self.clientsocket.recv(4096)
        print(len(data))
        response_msg: Protocol = pickle.loads(data)
        print("raw,  ", response_msg.command)
        print("from  ", response_msg.player)
        return response_msg


serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', 8082))
serverSock.listen(1)


# lock = Lock()
q: Queue = []
for i in range(10):
    q.append(Queue())
    q[i].put(Protocol)

while True:
    serverSock.listen(1)
    clientsock, clientAddress = serverSock.accept()
    if ClientThread.num_connection % 2 == 0:
        print("init ", ClientThread.num_connection)
        newthread = ClientThread(
            clientAddress, clientsock, q[ClientThread.num_connection], q[ClientThread.num_connection + 1])
    else:
        newthread = ClientThread(
            clientAddress, clientsock, q[ClientThread.num_connection], q[ClientThread.num_connection - 1])
    newthread.start()
