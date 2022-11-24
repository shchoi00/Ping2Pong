# -*- coding: utf-8 -*-
from random import choice, randint, uniform
from re import M
from socket import *
from threading import Thread
from threading import Lock
from xml.sax.handler import DTDHandler
from protocol import Protocol
import pickle
from queue import Queue
from pygame import time


#쓰레드간 공유할 변수 선언
data=[]

class ClientThread(Thread):
    num_connection: int = 0
    lock = Lock()

    def __init__(self, clientAddress, clientsocket, my_q: Queue, other_q: Queue):
        Thread.__init__(self)

        #쓰레드 공유변수 초기화, 
        #이 변수를 사용하여 서버-클라이언트간 통신을 구현함.
        data.append([10,200,780,200,345,195,
                     1,1,0,0,1,-999,-999,False,
                     0,False,0,False,0,
                     100,100,[0,0,0],[0,0,0],[False,False,False],[False,False,False],
                     0,0])
        # P1_X, P1_Y, P2_X, P2_Y, Ball_X, Ball_Y, 0, 1, 2, 3, 4, 5
        # velo_x, velo_y, P1_score, P2_Score, Item_constructor, item_x, item_y, item_existence 6, 7, 8, 9, 10, 11, 12, 13,
        # Last_hit, P1_item, P1_item_type, P2_item, P2_item_type, 14, 15, 16, 17, 18,
        # p1_paddle_height, p2_paddle_height, p1_item_time, p2_item_time, p1_item_used, p2_item_used  19, 20, 21, 22, 23, 24 
        # tempvelo_x, tempvelo_y  25, 26
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

            #클라이언트의 키 입력을 처리하는 부분
            #identifier = 각 쓰레드간 다른 공유변수를 사용하도록 하는 식별자
            #쓰레드 1,2의 식별자 값은 0, 
            #3과 4의 식별자 값은 2가 된다.

            #홀수번째 플레이어일 경우 (좌측 막대 배정)
        if response_msg.player % 2 == 1: 
            identifier: int = response_msg.player - 1
            if response_msg.pad_up == True:
                data[identifier][1] -= 6.5*response_msg.dt
            elif response_msg.pad_dn == True:
                data[identifier][1] += 6.5*response_msg.dt
    
            #아이템 사용
            #1번 아이템 = 막대 길이 증가
            #2번 아이템 = 원하는 타이밍에 공 일시정지
            #3번 아이템 = 꽝(임시, 보류중)
            if response_msg.item_use == True and not data[identifier][23][data[identifier][16]-1]:
                data[identifier][23][data[identifier][16]-1] = True
                data[identifier][15] = False
                data[identifier][21][data[identifier][16]-1] = 0
                if data[identifier][16] == 2:
                    data[identifier][25] = data[identifier][6]
                    data[identifier][26] = data[identifier][7]
                    data[identifier][7] = 0
                    data[identifier][6] = 0
                data[identifier][16] = 0
            #아이템 종료
            if data[identifier][23][0]:
                if data[identifier][21][0] >= 10000:
                    if data[identifier][19] > 100:
                        data[identifier][19] -= 5
                    else:
                        data[identifier][19] = 100
                        data[identifier][21][0] = 0
                        data[identifier][23][0] = False
                else:
                    if data[identifier][19] < 300:
                        data[identifier][19] += 5
                    else:
                        data[identifier][19] = 300
            if data[identifier][23][1]:
                if data[identifier][21][1] >= 1000:
                    data[identifier][21][1] = 0
                    data[identifier][23][1] = False
                    data[identifier][6] = data[identifier][25] * uniform(1.5,2)
                    data[identifier][7] = data[identifier][26] * choice([uniform(-2,-1.1),uniform(1.1,2)])


            if data[identifier][1] < 0:
                data[identifier][1] = 0
            elif data[identifier][1] + data[identifier][19] > 600:
                data[identifier][1] = 600 - data[identifier][19]
            self.protocol.my_paddle_x = data[identifier][0]
            self.protocol.my_paddle_y = data[identifier][1]
            self.protocol.other_paddle_x = data[identifier][2]
            self.protocol.other_paddle_y = data[identifier][3]
            self.protocol.has_item = data[identifier][15]
            self.protocol.item_type = data[identifier][16]
            self.protocol.my_paddle_height = data[identifier][19]
            self.protocol.other_paddle_height = data[identifier][20]

            #아이템 지속시간 처리
            for i in range(3):
                if data[identifier][23][i]:
                    data[identifier][21][i] += self.clock.get_time()

            #짝수번째 플레이어일 경우 (우측 막대 배정)
        else:
            identifier: int = response_msg.player - 2
            if response_msg.pad_up == True:
                data[identifier][3] -= 6.5*response_msg.dt
            elif response_msg.pad_dn == True:
                data[identifier][3] += 6.5*response_msg.dt
            if data[identifier][3] < 0:
                data[identifier][3] = 0
            elif data[identifier][3] + data[identifier][20] > 600:
                data[identifier][3] = 600 - data[identifier][20]
            self.protocol.my_paddle_x = data[identifier][2]
            self.protocol.my_paddle_y = data[identifier][3]
            self.protocol.other_paddle_x = data[identifier][0]
            self.protocol.other_paddle_y = data[identifier][1]
            self.protocol.has_item = data[identifier][17]  
            self.protocol.item_type = data[identifier][18]
            self.protocol.my_paddle_height = data[identifier][20]
            self.protocol.other_paddle_height = data[identifier][19]

            #아이템 사용
            #1번 아이템 = 막대 길이 증가
            #2번 아이템 = 원하는 타이밍에 공 일시정지
            #3번 아이템 = 꽝(임시, 보류중)
            if response_msg.item_use == True and not data[identifier][24][data[identifier][18]-1]:
                data[identifier][24][data[identifier][18]-1] = True
                data[identifier][17] = False
                data[identifier][22][data[identifier][18]-1] = 0
                if data[identifier][18] == 2:
                    data[identifier][25] = data[identifier][6]
                    data[identifier][26] = data[identifier][7]
                    data[identifier][7] = 0
                    data[identifier][6] = 0
                data[identifier][18] = 0
            #아이템 종료
            if data[identifier][24][0]:
                if data[identifier][22][0] >= 10000:
                    if data[identifier][20] > 100:
                        data[identifier][20] -= 5
                    else:
                        data[identifier][20] = 100
                        data[identifier][22][0] = 0
                        data[identifier][24][0] = False
                else:
                    if data[identifier][20] < 300:
                        data[identifier][20] += 5
                    else:
                        data[identifier][20] = 300
            if data[identifier][24][1]:
                if data[identifier][22][1] >= 1000:
                    data[identifier][22][1] = 0
                    data[identifier][24][1] = False
                    data[identifier][6] = data[identifier][25] * uniform(1.5,2)
                    data[identifier][7] = data[identifier][26] * choice([uniform(-2,-1.1),uniform(1.1,2)])

            #아이템 지속시간 처리
            for i in range(3):
                if data[identifier][24][i]:
                    data[identifier][22][i] += self.clock.get_time()
            
            #공의 움직임
        data[identifier][4] += data[identifier][6] * response_msg.dt
        data[identifier][5] += data[identifier][7] * response_msg.dt

            #승패 처리부분
        if data[identifier][4] >= 790:
            data[identifier][14] = 1
            data[identifier][10] += 100
            data[identifier][8] += 1
            data[identifier][4]=400
            data[identifier][5]=300
            data[identifier][6] = -1 * response_msg.dt
            data[identifier][7] = -1 * response_msg.dt
            data[identifier][10] += data[identifier][10] * 2
        elif data[identifier][4] <= 0:
            data[identifier][14] = 2
            data[identifier][10] += 100
            data[identifier][9] += 1
            data[identifier][4]=400
            data[identifier][5]=300
            data[identifier][6] = 1 * response_msg.dt
            data[identifier][7] = -1 * response_msg.dt
            data[identifier][10] += data[identifier][10] * 2

            #공과 상단 또는 하단의 충돌 처리부분
        if data[identifier][5] >= 590:
            if randint(1,16384) <= data[identifier][10] and not data[identifier][13]:
                data[identifier][11] = randint(250,500)
                data[identifier][12] = randint(150,400)
                data[identifier][10] = 0
                data[identifier][13] = True
            else:
                data[identifier][10] += 10
            data[identifier][7] = - data[identifier][7]
        if data[identifier][5] <= 0:
            if randint(1,16384) <= data[identifier][10] and not data[identifier][13]:
                data[identifier][11] = randint(250,500)
                data[identifier][12] = randint(150,400)
                data[identifier][10] = 0
                data[identifier][13] = True
            else:
                data[identifier][10] += 10
            data[identifier][7] = - data[identifier][7]

            #공과 막대의 충돌 처리부분
            #좌측 플레이어 막대와 공 충돌
        if data[identifier][4] < 20 and (data[identifier][1] < data[identifier][5] and data[identifier][1] + data[identifier][19] > data[identifier][5]):
            if randint(1,4096) <= data[identifier][10] and not data[identifier][13]:
                data[identifier][11] = randint(250,500)
                data[identifier][12] = randint(150,400)
                data[identifier][10] = 0
                data[identifier][13] = True
            else:
                data[identifier][10] += data[identifier][10]
            data[identifier][6] = - data[identifier][6] + uniform(-0.1,0.9) * response_msg.dt
            data[identifier][14] = 1

            #좌측 플레이어 끌어치기 구현용 코드
            if response_msg.player % 2 == 1:
                if response_msg.pad_up == True:
                    data[identifier][7] = data[identifier][7]  + uniform(-1,-0.1) * response_msg.dt
                elif response_msg.pad_dn == True:
                    data[identifier][7] = data[identifier][7]  + uniform(0.1,1) * response_msg.dt   
            else:
                data[identifier][7] = data[identifier][7]  + uniform(-0.5,0.5) * response_msg.dt 

            #우측 플레이어 막대와 공 충돌
        if data[identifier][4] > 770 and (data[identifier][3] < data[identifier][5] and data[identifier][3] + data[identifier][20] > data[identifier][5]):
            if randint(1,4096) <= data[identifier][10] and not data[identifier][13]:
                data[identifier][11] = randint(250,500)
                data[identifier][12] = randint(150,200)
                data[identifier][10] = 0
                data[identifier][13] = True
            else:
                data[identifier][10] += data[identifier][10]
            data[identifier][6] = - data[identifier][6] * 1.1 + uniform(-0.1,0.9) * response_msg.dt
            data[identifier][14] = 2

            #우측 플레이어 끌어치기 구현용 코드
            if response_msg.player % 2 == 0:
                if response_msg.pad_up == True:
                    data[identifier][7] = data[identifier][7]  + uniform(-1,-0.1) * response_msg.dt
                elif response_msg.pad_dn == True:
                    data[identifier][7] = data[identifier][7]  + uniform(0.1,1) * response_msg.dt                 
            else:
                data[identifier][7] = data[identifier][7]  + uniform(-0.5,0.5) * response_msg.dt 

            #아이템 획득처리
        if (data[identifier][4]+10 > data[identifier][11] and data[identifier][4] < data[identifier][11]+50 ) and (data[identifier][12] < data[identifier][5] and data[identifier][12] + 50 > data[identifier][5]):
            data[identifier][11] = -999
            data[identifier][12] = -999
            data[identifier][13] = False
            data[identifier][10] = 0
            if data[identifier][14] == 1:
                data[identifier][15] = True
                data[identifier][16] = randint(1,3)
            elif data[identifier][14] == 2:
                data[identifier][17] = True
                data[identifier][18] = randint(1,3)  
        #서버에서 처리한 여러 데이터를 프로토콜에 저장하여 클라이언트에 전송
        self.protocol.ball_x = data[identifier][4]
        self.protocol.ball_y = data[identifier][5]
        self.protocol.score=[data[identifier][8],data[identifier][9]]
        self.protocol.item_x = data[identifier][11]
        self.protocol.item_y = data[identifier][12]

        
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
