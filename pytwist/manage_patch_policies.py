# Manage Patch Policies
# Dimiter Todorov
# 2017

import re
import os
import sys
import getopt
import time
import logging
import csv

from string import Template

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
from pytwist.com.opsware.device import *
from pytwist.com.opsware.swmgmt import *

ts = twistserver.TwistServer()
global server_service, wpps, platform_service
global hotfix_service, update_rollup_service, service_pack_service
global logger


def setupLogging(level=logging.DEBUG):
    FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=FORMAT)
    # create logger
    logger = logging.getLogger('patch_import')
    logger.setLevel(level)
    return logger


# converts from string date time of format ("YYYYMMDD .HHmmss") to epoch for Opsware
def convertToEpoch(DATE_TIME_STRING):
    try:
        return int(time.mktime(time.strptime(DATE_TIME_STRING, '%Y%m%d.%H%M%S'))) * 1000.0
    except Exception, detail:
        raise Exception, "Exception on convert: %s" % (detail)
        return


def GetPatchRefsByFilter(type='hotfix', filter=None, blacklist=[], whitelist=None):
    returnRefs = []
    approvedKbs = None
    logger.debug("loading %s with filter: %s" % (type, filter.expression))
    if type == 'hotfix':
        patchRefs = hotfix_service.findHotfixRefs(filter)
        patchVOs = hotfix_service.getHotfixVOs(patchRefs)
    elif type == 'update_rollup':
        patchRefs = update_rollup_service.findUpdateRollupRefs(filter)
        patchVOs = update_rollup_service.getUpdateRollupVOs(patchRefs)
    elif type == 'service_pack':
        patchRefs = service_pack_service.findServicePackRefs(filter)
        patchVOs = service_pack_service.getServicePackVOs(patchRefs)
    else:
        return []
    if opts.whitelist:
        approvedKbs = re.sub(r'\s', '', opts.whitelist).split(',')
    for patch in patchVOs:
        if len(patch.supersededByPatches) == 0:
            if approvedKbs and patch.kbId in approvedKbs:
                logger.debug("whitelisted and approved %s", patch.kbId)
                returnRefs.append(patch)
            elif approvedKbs and not (patch.kbId in approvedKbs):
                logger.debug("not in whitelist %s", patch.kbId)
            else:
                logger.debug("approved %s", patch.kbId)
                returnRefs.append(patch)

        else:
            logger.debug("superseded %s" % patch.kbId)
    logger.info("loaded %s records %s with filter: %s " % (len(returnRefs), type, filter.expression))
    return returnRefs


def mapReportRow(patch):
    row = {
        "patchKbId": patch.kbId,
        "patchName": patch.unitName,
        "patchHpsaId" : patch.ref.id,
        "fileName" : patch.fileName,
        "patchStatus" : patch.patchStatus,
        "metadataSource" : patch.metadataSource,
        "unitType" : patch.unitType,
        "title": patch.title,
    }
    return row


def PrintReport(policyDict, file=None):
    keys = [
        "platformName",
        "platformId",
        "policyName",
        "patchKbId",
        "patchName",
        "patchHpsaId",
        "unitType",
        "fileName",
        "patchStatus",
        "metadataSource",
        "title"
    ]
    rows = []
    for platformName, policyObject in policyDict.iteritems():
        rowDefaults = {
            "platformName": platformName,
            "platformId": policyObject["platform"].id,
            "policyName": policyObject["policyName"]
        }
        for type in ["hotfix","update_rollup","service_pack"]:
            for patch in policyObject[type]:
                row = rowDefaults.copy()
                patchRow = mapReportRow(patch)
                if patchRow:
                    row.update(patchRow)
                    rows.append(row)
    if file:
        f=open(file,'wb')
        dict_writer=csv.DictWriter(f,keys,quoting=csv.QUOTE_ALL)
    else:
        dict_writer = csv.DictWriter(sys.stdout, keys, quoting=csv.QUOTE_ALL)
    dict_writer.writer.writerow(keys)
    dict_writer.writerows(rows)


def FindOrCreatePolicy(name, items):
    return ""


if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='%prog [--user username --password password]')
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default=None,
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default=None,
                      help="Password")
    parser.add_option("", "--policy_name", action="store", dest="policy_name", metavar="policy_name",
                      default=None,
                      help="Policy Name. Example \"OS Security Updates - July 2017 - $platformName\"")
    parser.add_option("", "--platform_filter", action="store", dest="platform_filter", metavar="platform_filter",
                      default=None,
                      help="Filter PlatformRefs e.g. \"platform_name CONTAINS 2012\"")
    parser.add_option("", "--begin_date", action="store", dest="begin_date", metavar="begin_date",
                      default=None,
                      help="Date Filter - e.g. 20170501.103212")
    parser.add_option("", "--end_date", action="store", dest="end_date", metavar="end_date",
                      default=None,
                      help="Date Filter - e.g. 20220611.103212")
    parser.add_option("", "--whitelist", action="store", dest="whitelist", metavar="whitelist",
                      default=None,
                      help="Optional comma-separated Whitelist to allow only specific KBs. Numbers Only. Default: Allow All. \n Example \"4022717,4022722,4019111\"")
    parser.add_option("", "--report", action="store_true", dest="report", metavar="report", default=False,
                      help="Instead of creating policies, report what would be done in CSV format.")
    parser.add_option("", "--report_file", action="store", dest="report_file", metavar="report_file", default=None,
                      help="Optional CSV file to store the results. Will overwrite.")
    # SETUP Logging
    logger = setupLogging()



    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
    except getopt.GetoptError:
        parser.print_help()
        sys.exit(2)

    if not opts.policy_name:
        logger.error("--policy_name is required")
        sys.exit(2)

    if opts.username and opts.password:
        ts.authenticate(opts.username, opts.password)
    elif os.environ.has_key('SA_USER') and os.environ.has_key('SA_PWD'):
        ts.authenticate(os.environ['SA_USER'], os.environ['SA_PWD'])
    else:
        logger.info("Username and Password not provided. Script may fail unless running in OGSH. \n Specify with -u username -p password")

    try:
        server_service = ts.server.ServerService
        platform_service = ts.device.PlatformService
        wpps = ts.swmgmt.WindowsPatchPolicyService
        hotfix_service = ts.pkg.windows.HotfixService
        update_rollup_service = ts.pkg.windows.UpdateRollupService
        service_pack_service = ts.pkg.windows.ServicePackService
    except:
        logger.error("Error initializing services to HPSA")
        sys.exit(2)

    filter = Filter()
    filter.expression = '(platform_name CONTAINS "Windows") & (platform_name NOT_CONTAINS "IA64") & (platform_name NOT_CONTAINS "Windows 2000") & (platform_name NOT_CONTAINS "Windows XP") & (platform_name NOT_CONTAINS "Windows NT 4.0")'
    if opts.platform_filter:
        filter.expression = "%s & (%s)" % (filter.expression, opts.platform_filter)
    platformRefs = platform_service.findPlatformRefs(filter)

    nameTemplate = Template(opts.policy_name)
    policyDict = {}
    for platformRef in platformRefs:
        platformObject = {}
        platformObject["platform"] = platformRef
        hfFilter = Filter()
        hfFilter.objectType = "patch_unit"
        hfFilter.expression = '(patch_unit_platform_id = %s)' % platformRef.id
        if opts.begin_date:
            hfFilter.expression = "%s & (PatchVO.createdDate GREATER_THAN_OR_EQUAL_TO %d)" % ( hfFilter.expression, convertToEpoch(opts.begin_date))
        if opts.end_date:
            hfFilter.expression = "%s & (PatchVO.createdDate LESS_THAN_OR_EQUAL_TO %d)" % (hfFilter.expression, convertToEpoch(opts.end_date))

        platformObject["hotfix"] = GetPatchRefsByFilter(type="hotfix", filter=hfFilter, whitelist=opts.whitelist)
        platformObject["update_rollup"] = GetPatchRefsByFilter(type="update_rollup", filter=hfFilter,
                                                               whitelist=opts.whitelist)
        platformObject["service_pack"] = GetPatchRefsByFilter(type="service_pack", filter=hfFilter,
                                                              whitelist=opts.whitelist)

        platformObject["policyName"] = nameTemplate.substitute({"name":platformRef.name})
        policyDict[platformRef.name] = platformObject
    PrintReport(policyDict, file = opts.report_file)
