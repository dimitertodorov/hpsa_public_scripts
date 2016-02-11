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
        groups_to_lock=[98410001, 97420001, 98390001, 186750001, 186710001, 186700001, 186730001, 186740001, 186720001, 186770001, 98380001, 96980001, 98370001, 97370001, 96990001, 191200001, 191210001]

        for dgi in groups_to_lock:
                dg=spin.RoleClass.get(dgi)
                print 'DEVGROUP: %s' % (dg)
                dg.update(dgi, reserved=0, lc_certified=1)

