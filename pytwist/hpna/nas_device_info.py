# Create CSV Files of NetworkAutomation - ServerAutomation relationships

import os
import re
import subprocess
import os
import sys
import getopt
import csv

from optparse import OptionParser


if (sys.platform == 'win32'):
    pytwist_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\smopylibs2')
    pylibs_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\agent\\pylibs')
    if os.path.isdir(pylibs_dir):
        pylibs_dir = (os.environ['SystemDrive'] + '\\Program Files\\Loudcloud\\Blackshadow')
        if os.path.isdir(pylibs_dir):
            raise 'The Opsware pylibs modules cannot be located'
else:
    pytwist_dir = '/opt/opsware/pylibs2'
    pylibs_dir = '/opt/opsware/agent/pylibs'
    if os.path.isdir(pylibs_dir):
        pylibs_dir = '/lc/blackshadow/coglib'
        if os.path.isdir(pylibs_dir):
            raise 'The Opsware pylibs modules cannot be located'
sys.path.append(pylibs_dir)
sys.path.append(pytwist_dir)
from pytwist import *
from pytwist.com.opsware.search import Filter
from pytwist.com.opsware.server import *
from pytwist.com.opsware.nas import *

ts = twistserver.TwistServer()

if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='%prog [--user username --password password --devices "device1,device2"]')
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="Password")
    parser.add_option("-d", "--devices", action="store", dest="devices", metavar="devices", default=None,
                      help="Devices to collect info for.")
    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
    except getopt.GetoptError:
        parser.print_help()
        sys.exit(2)

    if opts.username and opts.password:
        ts.authenticate(opts.username,opts.password)
    elif os.environ.has_key('SA_USER') and os.environ.has_key('SA_PWD'):
        ts.authenticate(os.environ['SA_USER'],os.environ['SA_PWD'])
    else:
        print "Username and Password not provided. Script may fail unless running in OGSH. \n Specify with -u username -p password"


    try:
        device_names=opts.devices.split(',')
    except:
        print "Error Parsing devices. Ensure they are in comma separated format"

    
    count = 0
    out_dict=[]
    for nas_device in device_names:
        
        deviceFilter = Filter()
        deviceFilter.expression = "hostName = %s" % nas_device

        device=ts.nas.NetworkDeviceService.findNetworkDeviceRefs(deviceFilter)
        ntVOFilter=Filter()
        ntVOFilter.expression="deviceId = %s" % device[0].id
        print nas_device
        ntVOs = ts.nas.NetworkTopologyService.findNetworkTopologyVOs(ntVOFilter)
        for ntVO in ntVOs:
            count+=1
            ntVORow={}

            if ntVO.remoteSasServerId is not None:
                macId = iter(ntVO.macAddress)
                macProper = ":".join(a+b for a,b in zip(macId,macId))
                serverFilter = Filter()

                serverFilter.expression = "device_interface_mac EQUAL_TO %s" % macProper
                serverRefs = ts.server.ServerService.findServerRefs(serverFilter)
                if len(serverRefs) is not 0:
                    for sRef in serverRefs:
                        sVO = ts.server.ServerService.getServerVO(sRef)
                        ntVORow["hostname"]=sVO.hostName
                        ntVORow["osVersion"]=sVO.osVersion
                        sHardwareVO = ts.server.ServerService.getServerHardwareVO(sRef)
                        if len(sHardwareVO.interfaces) is not 0:
                            for interface in sHardwareVO.interfaces:
                                if interface.hardwareAddress==macProper:
                                    ntVORow["slot"]=interface.slot
                                    ntVORow["hardwareAddress"]=interface.hardwareAddress
                                    ntVORow["ipAddress"]=interface.ipAddress
                                    ntVORow["configuredSpeed"]=interface.configuredSpeed
                                    ntVORow["netmask"]=interface.netmask
            elif ntVO.remoteDeviceId is not None:
                ndRef = NetworkDeviceRef(ntVO.remoteDeviceId)
                ndVO = ts.nas.NetworkDeviceService.getNetworkDeviceVO(ndRef)
                if ndVO.hostName!="":
                    ntVORow["hostname"]=ndVO.hostName
                else:
                    ntVORow["hostname"]="BLANK_NAME"



                ntVORow["osVersion"]=ndVO.osVersion
                if ntVO.remoteDevicePortId is not None:
                    remoteNpRef = NetworkPortRef(ntVO.devicePortId)
                    remoteNpVO = ts.nas.NetworkPortService.getNetworkPortVO(remoteNpRef)
                    ntVORow["slot"]=remoteNpVO.portName
                    macId = iter(ntVO.macAddress)
                    ntVORow["hardwareAddress"]= ":".join(a+b for a,b in zip(macId,macId))
                    ntVORow["ipAddress"]=""
                    ntVORow["configuredSpeed"]=remoteNpVO.negotiatedSpeed
                    ntVORow["netmask"]=""
                else:
                    macId = iter(ntVO.macAddress)
                    ntVORow["hardwareAddress"]= ":".join(a+b for a,b in zip(macId,macId))
                    ntVORow["slot"]=""
                    ntVORow["hardwareAddress"]=""
                    ntVORow["ipAddress"]=""
                    ntVORow["configuredSpeed"]=""
                    ntVORow["netmask"]=""
            else:
                ntVORow["hostname"]="NOT_FOUND"
                macId = iter(ntVO.macAddress)
                ntVORow["hardwareAddress"]= ":".join(a+b for a,b in zip(macId,macId))
                ntVORow["osVersion"]=""
                ntVORow["slot"]=""
                ntVORow["hardwareAddress"]=""
                ntVORow["ipAddress"]=""
                ntVORow["configuredSpeed"]=""
                ntVORow["netmask"]=""

            npRef = NetworkPortRef(ntVO.devicePortId)
            npVO = ts.nas.NetworkPortService.getNetworkPortVO(npRef)
            ntVORow["description"]=npVO.description
            ntVORow["associatedVlanId"]=npVO.associatedVlanId
            ntVORow["negotiatedSpeed"]=npVO.negotiatedSpeed
            ntVORow["portName"]=npVO.portName
            ntVORow["portType"]=npVO.portType
            ntVORow["portStatus"]=npVO.portStatus
            ntVORow["switchDevice"]=nas_device

            out_dict.append(ntVORow)
            print ntVORow


    keys=['hostname',
          'slot',
          'description',
          'ipAddress',
          'netmask',
          'hardwareAddress',
          'configuredSpeed',
          'portName',
          'portType',
          'portStatus',
          'osVersion',
          'associatedVlanId',
          'negotiatedSpeed',
          'switchDevice']

    f=open("nw_info_compiled.csv",'wb')
    dict_writer=csv.DictWriter(f,keys,quoting=csv.QUOTE_ALL)

    dict_writer.writer.writerow(keys)
    dict_writer.writerows(out_dict)



