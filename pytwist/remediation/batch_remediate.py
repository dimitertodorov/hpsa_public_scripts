# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
"""
The MIT License (MIT)

Copyright (c) 2014 Dimiter Todorov
dimiter.todorov@gmail.com

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

import os
import sys
import getopt
import time
import calendar
import math

# Import the OptionParser to allow for CLI options
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
from pytwist.com.opsware.swmgmt import PolicyAttachableMap, RemediateGlobalParamSet, AnalyzeArgument, StageArgument, \
    ActionArgument, PolicyRemediateJobArgument
import sa_utilities
# Script specific functions

ts = twistserver.TwistServer()


def get_long_time(time_str):
    parsed_time = time.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
    return long(calendar.timegm(parsed_time))


def get_normal_date_time(in_long_time):
    parsed_time = time.gmtime(in_long_time)
    return time.strftime('%Y-%m-%dT%H:%M:%S', parsed_time)


# Main Script
if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="1.0.0",
                          usage='python %prog [-f "Server Filter" -r "Policy IDs" -e email] Optional: [-u username -p password]')
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="(Optional) User Name Only required if running outside of OGSH context.")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="(Optional) Password. Only required if running outside of OGSH context.")
    parser.add_option("-e", "--email", action="store", dest="email", metavar="email", default="",
                      help="(Required) E-Mail")
    parser.add_option("--server_filter", action="store", dest="server_filter", metavar="server_filter", default="",
                      help="(Required) Servers which to Remediate")
    parser.add_option("--facility_filter", action="store", dest="facility_filter", metavar="facility_filter",
                      default="",
                      help="(Required) Facilities which to Remediate")
    parser.add_option("--platform_filter", action="store", dest="platform_filter", metavar="platform_filter",
                      default="",
                      help="(Required) Platforms which to Remediate")
    parser.add_option("--sw_policy_filter", action="store", dest="sw_policy_filter", metavar="sw_policy_filter",
                      default=None,
                      help="(Optional) SW Policies Filter to Remediate")
    parser.add_option("--patch_policy_filter", action="store", dest="patch_policy_filter",
                      metavar="patch_policy_filter", default=None,
                      help="(Optional) Patch Policies Filter to Remediate")
    parser.add_option("--analyze_time", action="store", dest="analyze_time", metavar="analyze_time", default=None,
                      help="(Optional) Time to start Analyze. Staging follows. Format: '%Y-%m-%dT%H:%M:%S' e.g. 2014-08-29T20:15:15")
    parser.add_option("--analyze_spread", action="store", dest="analyze_spread", metavar="analyze_spread", default=None,
                      help="(Optional) Time for the last job to start in minutes after analyze time. (e.g. 240=4hours) If left blank, analyze stage will be separated by 5 minutes")
    parser.add_option("--action_time", action="store", dest="action_time", metavar="action_time", default=None,
                      help="(Optional) Time to start actual Remediation. Format: '%Y-%m-%dT%H:%M:%S'")
    parser.add_option("--action_spread", action="store", dest="action_spread", metavar="action_spread", default=None,
                      help="(Optional) Time for the last job to start in minutes after action time. (e.g. 240=4hours) If left blank, action stage will be separated by 5 minutes")
    parser.add_option("--chunk", action="store", dest="chunk", metavar="chunk", default=50,
                      help="(Optional) Maximum number of servers per job. Default: 50")
    parser.add_option("--dry_run", action="store", dest="dry_run", metavar="dry_run", default=0,
                      help="(Optional) Specify 1 here to skip remediation. Only print what would be done.")

    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
    except getopt.GetoptError:
        parser.print_help()
        sys.exit(2)

    if opts.username and opts.password:
        ts.authenticate(opts.username, opts.password)
    elif os.environ.has_key('SA_USER') and os.environ.has_key('SA_PWD'):
        ts.authenticate(os.environ['SA_USER'], os.environ['SA_PWD'])
    else:
        print "Username and Password not provided. Script may fail unless running in OGSH. \n Specify with -u username -p password"

    try:
        server_service = ts.server.ServerService
        server_script_service = ts.script.ServerScriptService
        device_group_service = ts.device.DeviceGroupService
        auth_service = ts.fido.AuthorizationService
        swps = ts.swmgmt.SoftwarePolicyService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    default_platform_filter = '(platform_name CONTAINS "Windows") & (platform_name NOT_CONTAINS "IA64") & (platform_name NOT_CONTAINS "Windows 2000") & (platform_name NOT_CONTAINS "Windows XP") & (platform_name NOT_CONTAINS "4.0")'
    sa_utilities.ts = ts

    chunk = int(opts.chunk)

    #Map Servers according to Facility and Platform
    mapped_servers = sa_utilities.map_by_platform_facility(opts.facility_filter, opts.platform_filter,
                                                           opts.server_filter, chunk)
    batch_count = len(mapped_servers)

    current_time = long(time.time())
    analyze_time = None
    action_time = None
    default_seconds_spread = 300
    if (opts.analyze_time):
        analyze_time = get_long_time(opts.analyze_time)
    else:
        analyze_time = long(time.time()) + 200

    if opts.analyze_spread:
        analyze_minutes_spread = int(math.floor(int(opts.analyze_spread) / batch_count))
        analyze_seconds_spread = analyze_minutes_spread * 60
    else:
        analyze_seconds_spread = default_seconds_spread

    if (opts.action_time):
        action_time = get_long_time(opts.action_time)

    if opts.action_spread:
        action_minutes_spread = int(math.floor(int(opts.action_spread) / batch_count))
        action_seconds_spread = action_minutes_spread * 60
    else:
        action_seconds_spread = default_seconds_spread

    #If an action time is specified, ensure that the first action starts at least 5 minutes after last analyze job starts.
    if action_time:
        last_analyze_job = analyze_time + analyze_seconds_spread * batch_count
        print get_normal_date_time(last_analyze_job)
        if (action_time < (last_analyze_job + (300))):
            print "When specifying only an action start time it should be at least 5 minutes after last analyze job starts at: %s \nFor Action time you entered: %s" % (
            get_normal_date_time(last_analyze_job), get_normal_date_time(action_time))
            sys.exit(3)

    for batch_group in mapped_servers:
        policies = sa_utilities.get_policies(batch_group['platform'], opts.sw_policy_filter, opts.patch_policy_filter)
        #print "Returned policies: %s" % policies
        filtered_resources = sa_utilities.filter_servers_and_policies(batch_group['target_servers'], policies)
        if filtered_resources['patch'] or filtered_resources['sw']:
            ticket_string = "REMEDIATE-PY-%s-%s-CHUNK#-%s" % (
            batch_group['facility'].name, batch_group['platform'].name, batch_group['chunk'])
            print ticket_string
            policy_map = []
            if filtered_resources['patch']:
                pam = PolicyAttachableMap()
                pam.setPolicies(filtered_resources['patch'])
                pam.setPolicyAttachables(filtered_resources['servers'])
                pam.setAttached(1)
                print "Adding Patch Policies to Map: %s" % len(filtered_resources['patch'])
                policy_map.append(pam)
            if filtered_resources['sw']:
                sam = PolicyAttachableMap()
                sam.setPolicies(filtered_resources['sw'])
                sam.setPolicyAttachables(filtered_resources['servers'])
                sam.setAttached(1)
                print "Adding SW Policies to Map: %s" % len(filtered_resources['sw'])
                policy_map.append(sam)

            param_set = RemediateGlobalParamSet()
            param_set.setRebootOption('suppress')
            param_set.setContinueOnFailure(1)

            analyze_argument = AnalyzeArgument()
            if analyze_time:
                print "Starting ANALYZE at: %s" % get_normal_date_time(analyze_time)
                analyze_argument.setScheduleDate(analyze_time)
                analyze_time = analyze_time + analyze_seconds_spread

            stage_argument = StageArgument()

            action_argument = ActionArgument()
            if action_time:
                print "Starting ACTION at: %s" % get_normal_date_time(action_time)
                action_argument.setScheduleDate(action_time)
                action_time = action_time + action_seconds_spread

            action_argument.setNotificationSpec(sa_utilities.default_notify(opts.email))

            prja = PolicyRemediateJobArgument()
            prja.setRecommendedOnly(0)
            prja.setInstallTemplate(0)

            prja.setGlobalArguments(param_set)
            prja.setAnalyzePhaseArguments(analyze_argument)
            prja.setStagePhaseArguments(stage_argument)
            prja.setActionPhaseArguments(action_argument)

            prja.setPolicyAttachableMap(policy_map)
            prja.setTicketId(ticket_string)
            prja.setNotificationSpec(sa_utilities.default_notify(opts.email))

            print prja

            if opts.dry_run == 0:
                job_ref = swps.startRemediate(prja)
                print "Started: %s" % job_ref







