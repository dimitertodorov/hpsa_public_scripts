# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
"""
Dimiter Todorov - 2014
Sets folder permissions to read/execute recursively. Currently uses a hard-coded UserGroup Filter
"""

#Import some basic python modules
import os
import sys
import getopt
import csv
import datetime,time
import urllib2, base64
import simplejson
import re

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
from pytwist.com.opsware.fido import *
from pytwist.com.opsware.folder import *


#INITIALIZE Twist and Options
ts = twistserver.TwistServer()
parser = OptionParser(description=__doc__, version="0.0.1",
                      usage='python %prog options')

parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                  help="User Name")
parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                  help="Password")
parser.add_option("-f", "--folder", action="store", dest="folder", metavar="folder", default="",
                  help="Folder ID")


try:
    (opts, args) = parser.parse_args(sys.argv[1:])
    if not opts.folder:
        print 'Folder ID is required'
        sys.exit(3)
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
    server_service=ts.server.ServerService
    user_role_service=ts.fido.UserRoleService
    folder_service=ts.folder.FolderService
except:
    print "Error initializing services to HPSA"
    sys.exit(2)
###END INTIALIZATION

# Script specific functions


# Main Script
if (__name__ == '__main__'):
    target_folder=FolderRef(long(opts.folder))
    role_filter=Filter()
    role_filter.expression='UserRoleVO.roleName CONTAINS PATCH'
    role_filter.objectType='user_role'
    roles=user_role_service.findUserRoleRefs(role_filter)

    access_levels=['READ','X']
    if len(roles)>0:
        role_acls=[]
        for role in roles:
            for access_level in access_levels:
                print "ACL: %s rights to %s. Folder: %s" % (access_level,role.name,target_folder.name)
                access_acl=FolderACL()
                access_acl.folder=target_folder
                access_acl.role=role
                access_acl.accessLevel=access_level
                role_acls.append(access_acl)
        folder_service.addFolderACLs(role_acls,1,1)





