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

# JobInfoVO.description
# JobInfoVO.endDate
# JobInfoVO.pK
# JobInfoVO.schedule.startDate
# JobInfoVO.startDate
# ServerVO.osVersion
# job_business_application_id
# job_device_assettag
# job_device_desc
# job_device_id
# job_device_intf_ip
# job_device_platform_name
# job_device_primary_ip
# job_device_serialnum
# job_device_systemname
# job_device_type
# job_dvc_group_name
# job_group_id
# job_mine_visible
# job_session_id
# job_status
# job_ticket_id
# job_type
# job_user_id
# job_username
# job_visible
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

    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
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
        job_service=ts.job.JobService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    job_filter = Filter()
    print opts.filter
    job_filter.expression="(%s)" % opts.filter
    print job_filter.expression
    job_refs=job_service.findJobRefs(job_filter)
    print job_refs

    for ref in job_refs:
        vo=job_service.getJobInfoVO(ref)
        start_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(vo.jobArgs.actionPhaseArguments.scheduleDate))
        print "%s,%s,%s" % (vo.userTag,start_time,vo.jobArgs.globalArguments.rebootOption)





