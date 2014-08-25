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
Run a server script from pytwist. Can either run on a server with the agent. Or from the Global Shell
If running from a server with an agent, username/password is required.
usage: python run_script_from_csv.py [--file "CSV filename" -s script_id -e email] Optional: [-u username -p password]
The file should be a list of hostnames on which to run the script. The first line should be 'hostname' as a headers
"""

#Import some basic python modules
import os
import sys
import getopt
import csv
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

# Script specific functions
def default_notify(email):
    jobNotify=JobNotification()
    jobNotify.onSuccessOwner=email
    jobNotify.onFailureOwner=email
    jobNotify.onFailureRecipients=[email]
    jobNotify.onSuccessRecipients=[email]
    jobNotify.onCancelRecipients=[email]
    return jobNotify



# Main Script
if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='python %prog [--file "CSV filename" -s script_id -e email] Optional: [-u username -p password]')
    parser.add_option("-f", "--file", action="store", dest="file_name", metavar="FILE_NAME", default="itr_list.csv",
                      help="File Name")
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="Password")
    parser.add_option("-e", "--email", action="store", dest="email", metavar="email", default="",
                      help="E-Mail")
    parser.add_option("-s", "--script", action="store", dest="script", metavar="script", default="",
                      help="Script ID to Run")

    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
        if not opts.email:
            parser.error("Email Required")
        if not opts.script:
            parser.error("Script ID Required")
    except getopt.GetoptError:
        parser.print_help()
        sys.exit(2)
    if opts.username and opts.password:
        ts.authenticate(opts.username,opts.password)
    else:
        print "Username and Password not provided. Script may fail unless running in OGSH. \n Specify with -u username -p password"

    try:
        server_service=ts.server.ServerService
        server_script_service=ts.script.ServerScriptService
        device_group_service=ts.device.DeviceGroupService
        auth_service=ts.fido.AuthorizationService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    input_file=csv.DictReader(open(opts.file_name))

    server_tuple=[]
    for row in input_file:
        server_filter = Filter()
        server_filter.expression="ServerVO.hostName BEGINS_WITH %s" % row["hostname"].split(".")[0]
        server_refs=server_service.findServerRefs(server_filter)

        if(len(server_refs)==1):
            print "Success: %s" % server_refs[0].name
            one_ref=[server_refs[0]]
            server_tuple.append(server_refs[0])
        else:
            print "Could not find 1 entries for: %s" % row["hostname"]

    filtered_refs=auth_service.filterSingleTypeResourceList(OperationConstants.EXECUTE_SERVER_SCRIPT, server_tuple)
    script_ref=ServerScriptRef(long(opts.script))
    current_time=long(time.time())
    five_minutes_from_now=current_time+300
    print five_minutes_from_now
    js=JobSchedule()
    js.setStartDate(five_minutes_from_now)
    ssja=ServerScriptJobArgs()
    print server_tuple
    ssja.targets=filtered_refs
    ssja.timeout=360
    job_ref=server_script_service.startServerScript(script_ref,ssja,'Script from pytwist',default_notify(opts.email),js)
    print job_ref




