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
import socket
import csv
import time

#Import the OptionParser to allow for CLI options
from optparse import OptionParser

# HPSA - Depending on Windows/Unix select the directories containing the pytwist libraries.
if (sys.platform == 'win32'):
    import win32net
    pytwist_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\smopylibs2')
    pylibs_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\agent\\pylibs')
else:
    pytwist_dir = '/opt/opsware/pylibs2'
    pylibs_dir = '/opt/opsware/agent/pylibs2'

# Add the pytwist/pylibs directories to the path and import necessary modules.
sys.path.append(pylibs_dir)
sys.path.append(pytwist_dir)

# Main Script
if (__name__ == '__main__'):
    hostname=socket.gethostname()
    (users,length,resume_handle)=win32net.NetGroupGetUsers(None,'none',1)
    for user in users:
        print "%s,%s" % (hostname,user['name'])






