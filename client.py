'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util
import time



class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username
        # self.window = window_size

    def start(self):
       msg = util.make_message("join", 1, self.name)
       packet = util.make_packet("data", 0, msg)
       self.sock.sendto(packet.encode("utf-8"), (self.server_addr, self.server_port))
       # print("Type \"help\" to get list of legal commands")

       while True:
       	command = input()
       	command = command.casefold()
       	if command == "list":
       		m = util.make_message("request_users_list", 2)
       		p = util.make_packet("data", 0, m)
       		self.sock.sendto(p.encode("utf-8"), (self.server_addr, self.server_port))
       		time.sleep(1)

       	elif command.split(" ")[0] == "msg":
       		message =  command.split(" ")[1]
       		for x in range(2, len(command.split(" "))):
       			message = message + " " + command.split(" ")[x]

       		m = util.make_message("send_message", 4, message)
       		if m.split(" ")[2].isnumeric() == False:
        		print("incorrect userinput format")
        		continue

        	count = int(m.split(" ")[2])
        	if len(m.split(" ")) <= count + 3:
        		print("incorrect userinput format")
        		continue
        		
       		p = util.make_packet("data", 0, m)
       		self.sock.sendto(p.encode("utf-8"), (self.server_addr, self.server_port))

       	elif command == "quit":
       		print("quitting")
       		m = util.make_message("disconnect", 1, self.name)
       		p = util.make_packet("data", 0, m)
       		self.sock.sendto(p.encode("utf-8"), (self.server_addr, self.server_port))
       		# print("quitting")
       		sys.exit(0)
       		break

       	# elif command == "help":
       	# 	print("LIST OF LEGAL COMMANDS")
       	# 	print("1. HELP              format: \"help\"")
       	# 	print("2. LIST OF USERS     format: \"list\"")
       	# 	print("3. SEND MESSAGE      format: \"msg <number_of_users> <username1> <username2> … <message>\"")
       	# else:
       	# 	print("incorrect userinput format")


    def receive_handler(self):
    	while True:
    		packet, address = self.sock.recvfrom(6144)
    		# print("received something")
    		msgtype, seqno, data, checksum = util.parse_packet(packet.decode("utf-8"))
    		# print(data.split(" "))
    		if data.split(" ")[0] == "response_users_list":
    			usernum = int(data.split(" ")[2])
    			# print(usernum)
    			sortlist = []
    			for x in range(3, len(data.split(" "))):
    				sortlist.append(data.split(" ")[x])

    			sortlist.sort()
    			liststring = sortlist[0]
    			for x in range(1, len(sortlist)):
    				liststring = liststring + " " + sortlist[x]
    			print("list:", liststring)

    		elif data.split(" ")[0] == "forward_message":
    			sender = data.split(" ")[2]
    			text = data.split(" ")[3]
    			if len(data.split(" ")) > 4:
    				for x in range(4, len(data.split(" "))):
    					text = text + " " + data.split(" ")[x]
    			print("msg:", sender +  ":", text)

    		
    		elif data.split(" ")[0] == "err_server_full":
    			print("disconnected: server full")
    			os._exit(1)
    		elif data.split(" ")[0] == "err_username_unavailable":
    			print("disconnected: username not available")
    			os._exit(1)
    		elif data.split(" ")[0] == "err_unknown_message":
    			print("disconnected: server received an unknown command")
    			os._exit(1)



if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None

    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a


    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
