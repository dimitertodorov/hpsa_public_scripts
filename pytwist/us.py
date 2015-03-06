@"%PROGRAMFILES%\opsware\agent\lcpython15\python" -c "import sys;c=compile(''.join(open(sys.argv[1]).readlines()[2:]),'pyscript','exec');sys.argv=sys.argv[1:];eval(c)" %0 %*
@exit 0
import select, socket 

port = 514  # where do you expect to get a msg?
bufferSize = 1024 # whatever you need

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', port))
s.setblocking(0)

while True:
    result = select.select([s],[],[])
    msg = result[0][0].recv(bufferSize) 
    if msg=="CLOSE":
    	break
    print msg