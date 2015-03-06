import socket

UDP_IP = ["10.88.214.214","10.88.214.215"]
UDP_PORT = 514

hostname =socket.gethostname()
MESSAGE = "OKFROMs,%s" % hostname
print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
for ip in UDP_IP:
	sock.sendto(MESSAGE, (ip, UDP_PORT))