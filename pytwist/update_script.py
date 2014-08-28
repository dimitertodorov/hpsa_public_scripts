# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
"""
Dimiter Todorov - 2014

Takes content of a file, and sets it as a script's current source.
"""

#Import some basic python modules
import os
import sys
import getopt

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
from pytwist.com.opsware.script import *

#Initialize the twist
ts = twistserver.TwistServer()


# Main Script
if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='python %prog [--file "CSV filename" -s script_id -e email] Optional: [-u username -p password]')
    parser.add_option("-f", "--file", action="store", dest="file_name", metavar="FILE_NAME", default="itr_list.csv",
                      help="Input File with Source Code")
    parser.add_option("-s", "--script", action="store", dest="script", metavar="script", default="",
                      help="Script ID to Update")
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="Password")


    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
        if not opts.script:
            parser.error("Script ID Required")
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
        sss=ts.script.ServerScriptService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    script_file=open(opts.file_name,'r')

    script_ref=ServerScriptRef(long(opts.script))
    script_vo=sss.getServerScriptVO(script_ref)
    print script_vo
    current_version=script_vo.currentVersion.versionLabel
    usage=script_vo.currentVersion.usage
    try:
        current_version_int=int(current_version)
    except:
        print "Current Version is not numerical. Set to: %s" % current_version
        sys.exit(3)

    #Keep incrementing up to current_version+50, this should allow for any cases where an older version is current.
    for x in xrange(current_version_int, current_version_int+50):
        new_version=current_version_int+1
        try:
            new_version_ref=sss.getScriptVersion(script_ref,str(new_version))
        except com.opsware.common.NotFoundException:
            print "Version %s is available" % new_version
            break

    new_script_version=ServerScriptVersion()
    new_script_version.setRunAsSuperUser(1)
    new_script_version.setServerChanging(1)
    new_script_version.setVersionLabel(str(new_version))
    new_script_version.setUsage(usage)

    sss.createScriptVersion(script_ref,new_script_version,script_file.read())
    sss.setCurrentVersion(script_ref,str(new_version))

    #Successfully
    print "Successfully updated Script: (%s) to version %s " % (script_vo.name,new_version)








