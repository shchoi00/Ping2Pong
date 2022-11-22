from random import uniform
from re import M
from socket import *
from threading import Thread
from threading import Lock
from xml.sax.handler import DTDHandler
from protocol2 import Protocol
import pickle
from queue import Queue
from pygame import time

data=[]
class ClientThread(Thread):
    num_connection: int = 0
    lock = Lock()

    def __init__(self, clientAddress, clientsocket, my_q: Queue, other_q: Queue):
        Thread.__init__(self)
        data.append([10,200,780,200,345,195,1,1,0,0])
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
        print("asdf ",data[0])
        while True:
            self.clock.tick(60)
            response_msg = self.Receive()

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
        print("UPDATE")
        ClientThread.lock.acquire()
        self.protocol.command = "Update"
        try:
            self.my_q.put(response_msg)
            other_q: Protocol = self.other_q.get(timeout=0.1)
        except Exception as e:
            other_q: Protocol = response_msg
            print(e)
        if response_msg.player % 2 == 1:
            indicate: int = response_msg.player - 1
            if response_msg.pad_up == True:
                data[indicate][1] -= 6.5*response_msg.dt
            elif response_msg.pad_dn == True:
                data[indicate][1] += 6.5*response_msg.dt
            if data[indicate][1] < 0:
                data[indicate][1] = 0
            elif data[indicate][1] > 500:
                data[indicate][1] = 500
            self.protocol.my_paddle_x = data[indicate][0]
            self.protocol.my_paddle_y = data[indicate][1]
            self.protocol.other_paddle_x = data[indicate][2]
            self.protocol.other_paddle_y = data[indicate][3]
        else:
            indicate: int = response_msg.player - 2
            if response_msg.pad_up == True:
                data[indicate][3] -= 6.5*response_msg.dt
            elif response_msg.pad_dn == True:
                data[indicate][3] += 6.5*response_msg.dt
            if data[indicate][3] < 0:
                data[indicate][3] = 0
            elif data[indicate][3] > 500:
                data[indicate][3] = 500
            self.protocol.my_paddle_x = data[indicate][2]
            self.protocol.my_paddle_y = data[indicate][3]
            self.protocol.other_paddle_x = data[indicate][0]
            self.protocol.other_paddle_y = data[indicate][1]
        data[indicate][4] += data[indicate][6] * response_msg.dt
        data[indicate][5] += data[indicate][7] * response_msg.dt
        if data[indicate][4] >= 790:
            data[indicate][8] += 1
            data[indicate][4]=400
            data[indicate][5]=300
            data[indicate][6] = -1 * response_msg.dt
            data[indicate][7] = -1 * response_msg.dt
        elif data[indicate][4] <= 0:
            data[indicate][9] += 1
            data[indicate][4]=400
            data[indicate][5]=300
            data[indicate][6] = -1 * response_msg.dt
            data[indicate][7] = -1 * response_msg.dt
        if data[indicate][5] > 590:
            data[indicate][7] = - data[indicate][7]
        if data[indicate][5] < 10:
            data[indicate][7] = - data[indicate][7]
        if data[indicate][4] < 20 and (data[indicate][1] < data[indicate][5] and data[indicate][1] + 100 > data[indicate][5]):
            data[indicate][6] = - data[indicate][6] + uniform(-0.3,0.9) * response_msg.dt
            if response_msg.player % 2 == 1:
                if response_msg.pad_up == True:
                    data[indicate][7] = data[indicate][7]  + uniform(-1,0.3) * response_msg.dt
                elif response_msg.pad_dn == True:
                    data[indicate][7] = data[indicate][7]  + uniform(-0.3,1) * response_msg.dt                 
            data[indicate][7] = data[indicate][7]  + uniform(-0.5,0.5) * response_msg.dt 
        if data[indicate][4] > 770 and (data[indicate][3] < data[indicate][5] and data[indicate][3] + 100 > data[indicate][5]):
            data[indicate][6] = - data[indicate][6] * 1.1 + uniform(-0.3,0.9) * response_msg.dt
            if response_msg.player % 2 == 0:
                if response_msg.pad_up == True:
                    data[indicate][7] = data[indicate][7]  + uniform(-1,0.3) * response_msg.dt
                elif response_msg.pad_dn == True:
                    data[indicate][7] = data[indicate][7]  + uniform(-0.3,1) * response_msg.dt                 
            data[indicate][7] = data[indicate][7]  + uniform(-0.5,0.5) * response_msg.dt 
        self.protocol.ball_x = data[indicate][4]
        self.protocol.ball_y = data[indicate][5]
        self.protocol.score=[data[indicate][8],data[indicate][9]]


        
        # self.protocol.other_paddle_x, self.protocol.other_paddle_y = Shared.GetOtherPaddle(
        #     response_msg.player)

        print("Other Paddle: ", self.protocol.other_paddle_x,
              self.protocol.other_paddle_y)
        print("Other Ball: ", self.protocol.ball_x,
              self.protocol.ball_y)

        print("request,  ", self.protocol.command)
        ClientThread.lock.release()

    def Request(self):
        ClientThread.lock.acquire()
        send_msg = pickle.dumps(self.protocol)
        self.clientsocket.sendall(send_msg)
        ClientThread.lock.release()

    def Receive(self) -> Protocol:
        data = self.clientsocket.recv(4096)
        print(len(data))
        response_msg: Protocol = pickle.loads(data)
        print("Received: ", response_msg.command)
        print("from player: ", response_msg.player)
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
    serverSock.listen(2)
    clientsock, clientAddress = serverSock.accept()
    if ClientThread.num_connection % 2 == 0:
        print("init ", ClientThread.num_connection)
        newthread = ClientThread(
            clientAddress, clientsock, q[ClientThread.num_connection], q[ClientThread.num_connection + 1])
    else:
        newthread = ClientThread(
            clientAddress, clientsock, q[ClientThread.num_connection], q[ClientThread.num_connection - 1])
    newthread.start()
