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
from itertools import groupby

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
from pytwist.com.opsware.swmgmt import WindowsPatchPolicyVO

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


def GetPatchRefsByFilter(type='hotfix', filter=None, blacklist=None, whitelist=None):
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
    whitelist_pattern_string = ""
    for whitelistKb in whitelist:
        whitelist_pattern_string = whitelist_pattern_string + "(.*%s.*)|" % whitelistKb
    whitelist_pattern = re.compile(whitelist_pattern_string.rstrip("|"))
    for patch in patchVOs:
        if len(patch.supersededByPatches) == 0:
            if whitelist and patch.kbId in whitelist:
                logger.debug("whitelisted and approved %s", patch.kbId)
            elif whitelist and whitelist_pattern.match(patch.fileName):
                logger.debug("filename whitelisted and approved %s", patch.kbId)
            elif whitelist and not (patch.kbId in whitelist):
                #logger.debug("not in whitelist %s", patch.kbId)
                continue
            else:
                logger.debug("approved %s", patch.kbId)
            if patch.kbId in blacklist:
                logger.debug("patch in blacklist %s", patch.kbId)
            else:
                returnRefs.append(patch)
        else:
            logger.debug("superseded %s" % patch.kbId)
    logger.info("loaded %s records %s with filter: %s " % (len(returnRefs), type, filter.expression))
    return returnRefs


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
        for type in ["hotfix", "update_rollup", "service_pack"]:
            for patch in policyObject[type]:
                row = rowDefaults.copy()
                patchRow = mapReportRow(patch)
                if patchRow:
                    row.update(patchRow)
                    rows.append(row)
    if file:
        f = open(file, 'wb')
        dict_writer = csv.DictWriter(f, keys, quoting=csv.QUOTE_ALL)
    else:
        dict_writer = csv.DictWriter(sys.stdout, keys, quoting=csv.QUOTE_ALL)
    dict_writer.writer.writerow(keys)
    dict_writer.writerows(rows)


def mapReportRow(patch):
    row = {
        "patchKbId": patch.kbId,
        "patchName": patch.unitName,
        "patchHpsaId": patch.ref.id,
        "fileName": patch.fileName,
        "patchStatus": patch.patchStatus,
        "metadataSource": patch.metadataSource,
        "unitType": patch.unitType,
        "title": patch.title,
    }
    return row


def AddPatchesToPolicy(policyRef, patchRefs, removeUnmatched=False):
    print policyRef
    return


# create new windows patch policy
def CreateWindowsPatchPolicy(policyName, platformRef, description=None):
    try:
        # check for existing policy by name
        filter = Filter()
        filter.expression = '(patch_policy_name = "%s")' % (policyName)
        policyRefs = wpps.findWindowsPatchPolicyRefs(filter)

        if len(policyRefs) == 1:
            if description:
                # found policy... change description and return it.
                policyVO = wpps.getWindowsPatchPolicyVO(policyRefs[0])
                if policyVO.description != description:
                    logger.debug("Updating existing Policy %s for platform %s" % (policyName, platformRef.name))
                    policyVO.description = description
                    wpps.update(policyRefs[0], policyVO, 0, 1)
                else:
                    logger.debug("Found existing Policy %s for platform %s" % (policyName, platformRef.name))
                    return policyRefs[0]
            else:
                logger.debug("Found existing Policy %s for platform %s" % (policyName, platformRef.name))
                return policyRefs[0]
        elif len(policyRefs) == 0:
            # no policies found... create it.
            logger.debug("Creating Policy %s for platform %s" % (policyName, platformRef.name))
            wppVO = WindowsPatchPolicyVO()
            wppVO.name = policyName
            wppVO.platform = platformRef
            wppVO.type = 'STATIC'
            wppVO.description = description
            wppVO = wpps.create(wppVO)
        else:
            logger.error("Policy not unique by filter %s" % filter.expression)
            return
        policyRefs = wpps.findWindowsPatchPolicyRefs(filter)
        return policyRefs[0]
    except Exception, detail:
        logger.error("Exception occurred during Windows patch Policy creation: %s" % (detail))
        return


def GeneratePolicyDescription(policyRef, baseDescription="Associated: "):
    description = ""
    patches = wpps.getPatches([policyRef])
    for type, p in groupby(patches, lambda x: x.__class__.__name__):
        type = type.replace("Ref", "")
        description = "%s (%s %s) " % (description, type, len(list(p)))
    description = "%s %s" % (baseDescription, description)
    return description


if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='%prog [--user username --password password]')
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default=None,
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default=None,
                      help="Password")
    parser.add_option("", "--policy_name", action="store", dest="policy_name", metavar="policy_name",
                      #default=None,
                      default="OS Security Updates - January 2019 - $name Patch Policy",
                      help="Policy Name. Example \"OS Security Updates - October 2018 - $platformName\"")
    parser.add_option("", "--platform_filter", action="store", dest="platform_filter", metavar="platform_filter",
                      default="((platform_name CONTAINS 2012)|(platform_name CONTAINS 2008)|(platform_name CONTAINS 2016))&(platform_name NOT_CONTAINS IA)",
                      #default=None,
                      help="Filter PlatformRefs e.g. \"platform_name CONTAINS 2012\"")
    parser.add_option("", "--begin_date", action="store", dest="begin_date", metavar="begin_date",
                      default=None,
                      help="Date Filter - e.g. 20170501.103212")
    parser.add_option("", "--end_date", action="store", dest="end_date", metavar="end_date",
                      default=None,
                      help="Date Filter - e.g. 20220611.103212")
    parser.add_option("", "--whitelist", action="store", dest="whitelist", metavar="whitelist",
                      default="4461589,4461595,4461591,4480960,4480056,4480961,4480962,4480964,4480965,4480966,4471389,4468742,4476698,4461623,4461620,4461624,4461625,4022162,3172522,4461537,4461535,4480072,4480083,4480070,4480071,4480076,4480074,4461601,4462112,2596760,4480086,4461598,4480116,4480075,4461594,4480973,4480972,4461596,2553332,4480957,4480978,4461635,4461634,4461633,4461543,4476755,4461612,4480085,4480084,4461617,4461614",
                      help="Optional comma-separated Whitelist to allow specific KBs. Numbers Only. Default: Allow All. \n Example \"4022717,4022722,4019111\"")
    parser.add_option("", "--blacklist", action="store", dest="blacklist", metavar="blacklist",
                      default=None,
                      help="Optional comma-separated blacklist to ignore specific KBs. Numbers Only. Default: Allow All. \n Example \"4022717,4022722,4019111\"")
    parser.add_option("", "--report", action="store_true", dest="report", metavar="report", default=False,
                      help="Report Policy Object to File")
    parser.add_option("", "--report_file", action="store", dest="report_file", metavar="report_file", default="june_updates.csv",
                      help="Optional CSV file to store the results. Will overwrite.")
    parser.add_option("", "--dry_run", action="store_true", dest="dry_run", metavar="dry_run", default=False,
                      help="Instead of creating policies. Don't make any changes to SA. Only report")
    parser.add_option("", "--attach_platform_group", action="store_true", dest="attach_platform_group", metavar="attach_platform_group", default=False,
                      help="Use this to attach the policies to the OS Level Group.")
    parser.add_option("", "--remove_existing_patches", action="store_true", dest="remove_existing_patches", metavar="remove_existing_patches", default=False,
                      help="Use this flag to clean policy of all existing patches")
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
        logger.info(
            "Username and Password not provided. Script may fail unless running in OGSH. \n Specify with -u username -p password")

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
    filter.expression = '((platform_name CONTAINS "2008")|(platform_name CONTAINS "2012")|(platform_name CONTAINS "2016")) (platform_name CONTAINS "Windows") & (platform_name NOT_CONTAINS "IA64") & (platform_name NOT_CONTAINS "Windows 2000") & (platform_name NOT_CONTAINS "Windows XP") & (platform_name NOT_CONTAINS "Windows NT 4.0")'
    if opts.platform_filter:
        filter.expression = "%s & (%s)" % (filter.expression, opts.platform_filter)
    platformRefs = platform_service.findPlatformRefs(filter)

    nameTemplate = Template(opts.policy_name)
    policyDict = {}

    patchBlackList = ["890830"]
    if opts.blacklist:
        mergedList = patchBlackList + re.sub(r'\s', '', opts.blacklist).split(',')
        patchBlackList = mergedList

    patchWhiteList=None
    if opts.whitelist:
        patchWhiteList = re.sub(r'\s', '', opts.whitelist).split(',')

    for p in platformRefs:
        platformDeviceGroup = platform_service.getPlatformDeviceGroup(p)
        logger.info("Platform %s to DeviceGroup: %s (%s)" % (p.name, platformDeviceGroup.name, platformDeviceGroup.id))

    for platformRef in platformRefs:
        platformObject = {}
        platformObject["platform"] = platformRef
        hfFilter = Filter()
        hfFilter.objectType = "patch_unit"
        hfFilter.expression = '(patch_unit_platform_id = %s)' % platformRef.id
        if opts.begin_date:
            hfFilter.expression = "%s & (PatchVO.createdDate GREATER_THAN_OR_EQUAL_TO %d)" % (
            hfFilter.expression, convertToEpoch(opts.begin_date))
        if opts.end_date:
            hfFilter.expression = "%s & (PatchVO.createdDate LESS_THAN_OR_EQUAL_TO %d)" % (
            hfFilter.expression, convertToEpoch(opts.end_date))

        platformObject["hotfix"] = GetPatchRefsByFilter(type="hotfix",
                                                        filter=hfFilter,
                                                        whitelist=patchWhiteList,
                                                        blacklist=patchBlackList)

        platformObject["update_rollup"] = GetPatchRefsByFilter(type="update_rollup",
                                                               filter=hfFilter,
                                                               whitelist=patchWhiteList,
                                                               blacklist=patchBlackList)
        platformObject["service_pack"] = GetPatchRefsByFilter(type="service_pack",
                                                              filter=hfFilter,
                                                              whitelist=patchWhiteList,
                                                              blacklist=patchBlackList)

        platformObject["policyName"] = nameTemplate.substitute({"name": platformRef.name})
        policyDict[platformRef.name] = platformObject
    if opts.report:
        PrintReport(policyDict, file=opts.report_file)
    if not opts.dry_run:
        for platformName, options in policyDict.iteritems():
            platformRef = options["platform"]
            patchRefs = []
            for type in ["hotfix", "update_rollup", "service_pack"]:
                if len(options[type]) != 0:
                    logger.debug("loading %d %s for %s" % (len(options[type]), type, platformRef.name))
                    for p in options[type]:
                        patchRefs.append(p.ref)
            if len(patchRefs)>0:
                policyRef = CreateWindowsPatchPolicy(options['policyName'], options['platform'])
                if opts.remove_existing_patches:
                    logger.info("Removing all existing patches from %s" % policyRef.name)
                    wpps.removeAllPatches([policyRef])
                for p in patchRefs:
                    logger.debug("Adding %s to %s" % (p.name, policyRef.name))
                    wpps.addPatches([policyRef], patchRefs)
                if opts.attach_platform_group:
                    platformDeviceGroup = platform_service.getPlatformDeviceGroup(platformRef)
                    logger.info("attaching Policy:%s to DeviceGroup: %s (%s)" % (policyRef.name, platformDeviceGroup.name, platformDeviceGroup.id))
                    wpps.attachToPolicies([policyRef],[platformDeviceGroup])
                else:
                    logger.warn("policy is not being attached to anything: %s)" % (policyRef.name))
                policyDescription = GeneratePolicyDescription(policyRef, baseDescription="Associated:")
                policyRef = CreateWindowsPatchPolicy(options['policyName'], options['platform'], policyDescription)
            else:
                logger.info("No Patches to be added for %s" % platformRef.name)

