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
        groups_to_lock=[97960001]

        for dgi in groups_to_lock:
                dg=spin.RoleClass.get(dgi)
                print 'DEVGROUP: %s' % (dg)
                dg.update(dgi, reserved=0, lc_certified=0)

