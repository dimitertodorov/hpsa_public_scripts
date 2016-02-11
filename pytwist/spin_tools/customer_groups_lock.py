import os
import sys
import string
import pprint
import traceback
isEinstein = 1
if os.path.isdir('/opt/opsware/pylibs2/shadowbot'):
	sys.path.append('/opt/opsware/pylibs2')
	isEinstein = 0
else:
	sys.path.append('/opt/opsware/pylibs')


from coglib import spinwrapper
from coglib import certmaster
from coglib import platform

ctx = certmaster.getContextByName("spin","spin.srv","opsware-ca.crt")
spin = spinwrapper.SpinWrapper(ctx=ctx)



def getSpinVersion():
	lst = spin.sys.getAllConf()
	return lst['spin.version']


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
if __name__ == '__main__':
	exclude_update_ids = []
	groups_to_lock=[97920001, 12980001, 12950001, 12960001, 12990001, 13250001, 13000001, 13020001, 12900001, 13030001, 13040001, 13010001, 13070001, 13050001, 13090001, 13060001, 97430001, 12970001, 97880001, 97890001, 97940001, 97910001, 97860001, 97870001, 97790001, 97810001, 97900001, 97800001, 97820001, 97830001, 97840001, 97620001, 97780001, 97850001, 191270001, 191280001, 191290001]	
	for dgi in groups_to_lock:
		dg=spin.RoleClass.get(dgi)
		print 'DEVGROUP: %s' % (dg)
		dg.update(dgi, reserved=0, lc_certified=1)		
	
	
