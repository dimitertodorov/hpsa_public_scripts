import sys
sys.path.append('/opt/opsware/pylibs2')
from coglib import spinwrapper
spin = spinwrapper.SpinWrapper("http://127.0.0.1:1007")
for line in  open("recert_file.txt",'r'):
	if line!='':
		spin.Device.update(id = int(line), allow_recert=1)
		print line
#for sm in server_mids:
#	spin.Device.update(id = sm, allow_recert=1)
