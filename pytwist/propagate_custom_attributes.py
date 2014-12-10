# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
"""
The MIT License (MIT)

Copyright (c) 2014 Dimiter Todorov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Script Details:
Propagate Custom Attributes From a base static device group to all children until reaching:
A dynamic group.
A static group with no device group children.

"""

#Import some basic python modules
import os
import sys
import getopt
from itertools import islice, chain

import time

#Import the OptionParser to allow for CLI options
from optparse import OptionParser

# HPSA - Depending on Windows/Unix select the directories containing the pytwist libraries.
if (sys.platform == 'win32'):
    pytwist_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\smopylibs2')
    pylibs_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\agent\\pylibs')
else:
    pytwist_dir = '/opt/opsware/pylibs2'
    pylibs_dir = '/opt/opsware/agent/pylibs2'

# Add the pytwist/pylibs directories to the path and import necessary modules.
sys.path.append(pylibs_dir)
sys.path.append(pytwist_dir)
from pytwist import *
from pytwist.com.opsware.search import Filter
from pytwist.com.opsware.fido import OperationConstants
from pytwist.com.opsware.device import DeviceGroupRef
from pytwist.com.opsware.job import JobRef,JobNotification,JobSchedule,JobInfoVO
from pytwist.com.opsware.script import ServerScriptRef, ServerScriptJobArgs

#Initialize the twist
ts = twistserver.TwistServer()

def propagate_attributes(device_group,attributes):
    #Get CustAttrs for current group
    custom_attributes=device_group_service.getCustAttrs(device_group,'DEFAULT',"ITS.*",False)
    print "Name: %s, Atts: %s" % (device_group,custom_attributes)
    #Add and/or overwrite custom attributes
    for cust_attr in custom_attributes:
        if custom_attributes[cust_attr]:
            attributes[cust_attr]=custom_attributes[cust_attr]
    #Set the attributes.
    device_group_service.setCustAttrs(device_group,attributes)

    #Call the same function on all children if there are any.
    children=device_group_service.getChildren(device_group)
    for child in children:
        propagate_attributes(child,attributes)

# Main Script
if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage=' Optional: [-u username -p password]')
    parser.add_option("-g", "--filter", action="store", dest="device_group", metavar="device_group", default=0,
                      help="device_group id")
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="Password")
    parser.add_option("-d", "--debug", action="store", dest="debug", metavar="debug", default=0,
                      help="Debug?")


    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
        if not opts.device_group:
            parser.error("device_group ID missing")
    except getopt.GetoptError:
        parser.print_help()
        sys.exit(2)

    if opts.username and opts.password:
        ts.authenticate(opts.username,opts.password)
    elif os.environ.has_key('SA_USER') and os.environ.has_key('SA_PWD'):
        ts.authenticate(os.environ['SA_USER'],os.environ['SA_PWD'])
    else:
        print "Username and Password not provided. Script may fail unless running in OGSH. \nSpecify with -u username -p password"

    try:
        server_service=ts.server.ServerService
        server_script_service=ts.script.ServerScriptService
        device_group_service=ts.device.DeviceGroupService
        auth_service=ts.fido.AuthorizationService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    #Get the parent group.
    parent_group=DeviceGroupRef(opts.device_group)
    parent_attributes=device_group_service.getCustAttrs(parent_group,'DEFAULT',"ITS.*",False)
    children=device_group_service.getChildren(parent_group)
    for child in children:
        propagate_attributes(child,parent_attributes)







