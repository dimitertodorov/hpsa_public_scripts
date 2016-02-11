import sys
sys.path.append('/opt/opsware/pylibs2')
from coglib import spinwrapper
spin = spinwrapper.SpinWrapper("http://127.0.0.1:1007")
server_mid = 123456
server_mids=[7960001, 2180002, 8300001, 860001, 8330001, 8360001, 8620001, 2190002, 8610001, 8540001, 8400001, 8470001, 8500001, 2210002, 8290001, 8060001, 8000001, 7940001, 8080001, 8520001, 8460001, 8050001, 8280001, 2200002, 8010001]
for sm in server_mids:
	spin.Device.update(id = sm, allow_recert=1)
