import socket,select

port = 5678#12345
socket_list = []
users = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1',port))
server_socket.listen(5)
socket_list.append(server_socket)
server_socket.settimeout(2)

while True:
    ready_to_read,ready_to_write,in_error = select.select(socket_list,[],[],0)
    for sock in ready_to_read:
        if sock == server_socket:
            connect, addr = server_socket.accept()
            socket_list.append(connect)
            connect.send(("You are connected from:" + str(addr)).encode())
        else:
            try:
                data = sock.recv(2048).decode()
                if data.startswith("#"):
                    users[data[1:].lower()]=connect
                    print ("User " + data[1:] +" added.")
                    connect.send(("Your user detail saved as : "+str(data[1:])).encode())
                elif data.startswith("@"):
                    users[data[1:data.index(':')].lower()].send(data[data.index(':')+1:])
                    connect.send(data.encode())
                #client_socket.close()
                print(data)
            except:
                continue

server_socket.close()