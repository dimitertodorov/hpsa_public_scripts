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

# Script specific functions
def default_notify(email):
    jobNotify=JobNotification()
    jobNotify.onSuccessOwner=email
    jobNotify.onFailureOwner=email
    jobNotify.onFailureRecipients=[email]
    jobNotify.onSuccessRecipients=[email]
    jobNotify.onCancelRecipients=[email]
    return jobNotify

def batch(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.next()], batchiter)


# Main Script
if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='python %prog [--file "CSV filename" -s script_id -e email] Optional: [-u username -p password]')
    parser.add_option("-f", "--filter", action="store", dest="filter", metavar="filter", default="(ServerVO.hostName CONTAINS ASOJIASOJIDSAOIAJSDA)",
                      help="Filter")
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="Password")
    parser.add_option("-e", "--email", action="store", dest="email", metavar="email", default="",
                      help="E-Mail")
    parser.add_option("-s", "--script", action="store", dest="script", metavar="script", default="",
                      help="Script ID to Run")
    parser.add_option("-a", "--args", action="store", dest="args", metavar="args", default=None,
                      help="Args to pass to script")
    parser.add_option("-m", "--minutes", action="store", dest="minutes", metavar="minutes", default=4,
                      help="Minutes Between Each Run")
    parser.add_option("-x", "--runas_user", action="store", dest="runas_user", metavar="runas_user", default=None,
                      help="Run AS User")
    parser.add_option("-y", "--runas_pwd", action="store", dest="runas_pwd", metavar="runas_pwd", default=None,
                      help="Run AS PWD")
    parser.add_option("-z", "--runas_domain", action="store", dest="runas_domain", metavar="runas_domain", default=None,
                      help="Run AS Domain")
    parser.add_option("-d", "--debug", action="store", dest="debug", metavar="debug", default=0,
                      help="Debug?")


    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
        if not opts.email:
            parser.error("Email Required")
        if not opts.script:
            parser.error("Script ID Required")
        if not opts.filter:
            parser.error("Filter")
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
        job_service=ts.job.JobService
        server_script_service=ts.script.ServerScriptService
        device_group_service=ts.device.DeviceGroupService
        auth_service=ts.fido.AuthorizationService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)



    script_ref=ServerScriptRef(long(opts.script))
    script_vo=server_script_service.getServerScriptVO(script_ref)
    if script_vo.codeType in ['BAT','VBS','PS1']:
        platform_filter="device_platform_name CONTAINS Win"
    else:
        platform_filter="device_platform_name NOT_CONTAINS Win"


    server_filter = Filter()
    print opts.filter
    server_filter.expression="(%s)&(%s)" % (opts.filter,platform_filter)
    print server_filter.expression
    server_refs=server_service.findServerRefs(server_filter)


    print start_time
    server_array=[]
    for srv in server_refs:
        server_array.append(srv)
    filtered_refs=auth_service.filterSingleTypeResourceList(OperationConstants.EXECUTE_SERVER_SCRIPT, server_array)
    js=JobSchedule()
    js.setStartDate(start_time)
    ssja=ServerScriptJobArgs()
    ssja.targets=filtered_refs
    ssja.timeOut=3600
    if opts.args:
        ssja.parameters=opts.args
    if opts.runas_user and opts.runas_pwd and opts.runas_domain:
        ssja.username=opts.runas_user
        ssja.password=opts.runas_pwd
        ssja.loginDomain=opts.runas_domain
    print opts.minutes
    if int(opts.debug)!=1:
        job_ref=server_script_service.startServerScript(script_ref,ssja,'Script from pytwist',default_notify(opts.email),None)
        print job_ref
    else:
        print filtered_refs

    if int(opts.debug)!=1:
        wait_count=0
        while(True and wait_count<9000):
            wait_count=wait_count+1
            job_progress=job_service.getProgress(job_ref)
            if(job_progress):
                sys.stdout.write('.')
            else:
                print "Finished"
                job_result = job_service.getResult(job_ref)
                targets=job_result.jobInfo.args.targets
                for srv in targets:
                    try:
                        print "BEGIN_SERVER|%s" % srv.name
                        output=server_script_service.getServerScriptJobOutput(job_ref,srv)
                        print "Output: %s" % output.tailStdout
                        print "Error: %s" % output.tailStderr
                        print "Code: %s" % output.exitCode
                        print "END_SERVER|%s" % srv.name
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        print "SERVER_ERROR %s %s" % (srv.name,e)
                break




