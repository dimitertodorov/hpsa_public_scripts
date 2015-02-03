# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
"""
Copyright (c) 2014 Dimiter Todorov

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
import socket

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
from pytwist.com.opsware.script import ServerScriptRef, ServerScriptJobArgs

#Initialize the twist
ts = twistserver.TwistServer()


def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    try:
        s.connect((address, port))
        print "%s,%s,OPEN" % (address, port)
        return True
    except socket.error, e:
        print "%s,%s,CLOSED,%s" % (address, port, e)
        return False
# Main Script

if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='python %prog [Options]')
    parser.add_option("-l", "--list", action="store", dest="list", metavar="list",
                      help="Server List")
    parser.add_option("-t", "--tcpport", action="store", dest="tcpport", metavar="tcpport",
                      help="TCP Port")
    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
        if not opts.list:
            parser.error("List Required")
        if not opts.tcpport:
            parser.error("TCP Port Required")
    except getopt.GetoptError:
        parser.print_help()
        sys.exit(2)

    targets=opts.list.split(',')
    for target in targets:
        #print target
        check=check_server(target,int(opts.tcpport))