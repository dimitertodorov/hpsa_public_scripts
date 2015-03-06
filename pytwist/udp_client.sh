#!/bin/bash
# Dimiter Todorov - ITS - DCO - 2014
# Run UDP Test

PYTHONPATH=/opt/opsware/agent/pylibs
export PYTHONPATH
PATH=/opt/opsware/agent/bin:${PATH}
export PATH
SRC=/opt/opsware/agent/pylibs/coglib

rm -f /tmp/udptest.py

### Be very careful when editing the following heredoc. If the tabs do not line up perfectly, you will get a syntax error.
### You can work around this by editing the python file separately in a good editor like sublime, then copy/pasting it into here.
### Keep in mind that if testing the python independently, you will need to replace any bash variables with proper names. (Only $zonename and $agent_filename are currently used)
cat << EOT > /tmp/udptest.py
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
EOT

chmod u+x /tmp/udptest.py
/opt/opsware/agent/bin/python /tmp/udptest.py
