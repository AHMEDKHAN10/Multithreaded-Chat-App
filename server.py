import sys
import getopt
import socket
from threading import Thread
import util


class Server:
    def __init__(self, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        # self.window = window

    def start(self):
        # print("Listening...")
        userdictionary = {}
        ipdictionary = {}
        # self.sock.sendto(("check").encode("utf-8"), address)

        while True:
            packet, address = self.sock.recvfrom(6144)
            # self.sock.sendto(("check").encode("utf-8"), address)

            msg_type, seqno, data, checksum = util.parse_packet(packet.decode("utf-8"))
            # print(data.split())

            if data.split(" ")[0] == "join":
                if len(userdictionary) >= util.MAX_NUM_CLIENTS:
                    reply = util.make_message("err_server_full", 2)
                    p = util.make_packet("data", 0, reply)
                    self.sock.sendto(p.encode("utf-8"), address)

                elif data.split(" ")[2] in userdictionary:
                    reply = util.make_message("err_username_unavailable", 2)
                    p =  util.make_packet("data", 0, reply)
                    self.sock.sendto(p.encode("utf-8"), address)

                else:
                    userdictionary[data.split(" ")[2]] = address
                    ipdictionary[address] = data.split(" ")[2]
                    print("join:", data.split(" ")[2])

            elif data.split(" ")[0] == "disconnect":
            	a = userdictionary[data.split(" ")[2]]
            	userdictionary.pop(data.split(" ")[2])
            	ipdictionary.pop(a)
            	print("disconnected:", data.split(" ")[2])

            elif data.split(" ")[0] == "request_users_list":
                user = ipdictionary[address]
                reply = str(len(userdictionary))
                for name in userdictionary:
                    reply = reply + " " + name

                # reply = str(len(userdictionary)) + "  " + reply
                print("request_users_list:", user)
                # reply = "send hoja"
                msg = util.make_message("response_users_list", 3, reply)
                p = util.make_packet("data", 0, msg)
                self.sock.sendto(p.encode("utf-8"), address)

            elif data.split(" ")[0] == "send_message":
            	if data.split(" ")[2].isnumeric() == False:
            		m = util.make_message("err_unknown_message", 2)
            		p = util.make_packet("data", 0, m)
            		self.sock.sendto(p.encode("utf-8"), address)
            		u = ipdictionary[address]
            		userdictionary.pop(u)
            		print("disconnected:", ipdictionary[address], "sent unknown command")
            		ipdictionary.pop(address)
            		continue

            	count = int(data.split(" ")[2])
            	if len(data.split(" ")) <= count + 3:
            		m = util.make_message("err_unknown_message", 2)
            		p = util.make_packet("data", 0, m)
            		self.sock.sendto(p.encode("utf-8"), address)
            		u = ipdictionary[address]
            		userdictionary.pop(u)
            		print("disconnected:", ipdictionary[address], "sent unknown command")
            		ipdictionary.pop(address)
            		continue

            	if count == 0:
            		continue

            	sender = ipdictionary[address]
            	usefuldata = ""
            	receivers = {}

            	print("msg:", sender)
            	for x in range(count):
            		username = data.split(" ")[3+x]
            		if username not in userdictionary:
            			print("msg:", sender, "to non-existent user", username)
            		else:
            			useraddress = userdictionary[username]
            			receivers[username] = useraddress


            	for x in range(3 + count, len(data.split())):
            		usefuldata = usefuldata + data.split()[x]
            		if x < len(data.split()) - 1:
            			usefuldata = usefuldata + " "
            	usefuldata = sender + " " + usefuldata
            	fwd = util.make_message("forward_message", 4, usefuldata)
            	p = util.make_packet("data", 0, fwd)

            	send = False
            	for rec in receivers:
            		a = receivers[rec]
            		self.sock.sendto(p.encode("utf-8"), a)

            
            else:
            	m = util.make_message("err_unknown_message", 2)
            	p = util.make_packet("data", 0, m)
            	self.sock.sendto(p.encode("utf-8"), address)
            	u = ipdictionary[address]
            	userdictionary.pop(u)
            	ipdictionary.pop(address)
            	print("disconnected:", ipdictionary[address], "sent unknown command")

        # raise NotImplementedError



if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    SERVER = Server(DEST, PORT)
    try:
        # T = Thread(target=SERVER.start)
        # T.daemon = True
        # T.start()
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
