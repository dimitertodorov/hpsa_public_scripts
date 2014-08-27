# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
"""
Dimiter Todorov - 2014
SA Utilities for Remediation
"""
from itertools import islice, chain

from pytwist import *
from pytwist.com.opsware.search import Filter
from pytwist.com.opsware.fido import OperationConstants
from pytwist.com.opsware.job import JobNotification


def map_by_platform_facility(facility_filter, platform_filter, server_filter, chunk=50):
    result_map_array = []
    fac_filter = Filter()
    fac_filter.expression = facility_filter
    fac_filter.objectType = 'facility'
    plat_filter = Filter()
    plat_filter.expression = platform_filter
    plat_filter.objectType = 'platform'
    srv_filter = Filter()
    srv_filter.expression = server_filter
    srv_filter.objectType = 'server'
    target_facilities = ts.locality.FacilityService.findFacilityRefs(fac_filter)
    target_platforms = ts.device.PlatformService.findPlatformRefs(plat_filter)
    print target_facilities
    print target_platforms
    for facility in target_facilities:
        for platform in target_platforms:
            combined_filter = Filter()
            combined_filter.expression = "(%s)&(device_facility_id EQUAL_TO %s)&(device_platform_id EQUAL_TO %s)" % (
            server_filter, facility.id, platform.id)
            servers = ts.server.ServerService.findServerRefs(combined_filter)
            i = 0
            print '%s results for: %s' % (len(servers), combined_filter.expression)
            if len(servers) > 0:
                for batch_iter in batch(servers, chunk):
                    result_dict = {}
                    result_dict['facility'] = facility
                    result_dict['platform'] = platform
                    result_dict['chunk'] = i
                    server_array = []
                    for srv in batch_iter:
                        server_array.append(srv)
                    result_dict['target_servers'] = server_array
                    result_map_array.append(result_dict)
                    i = i + 1

    return result_map_array


def get_policies(platform, sw_policy_filter=None, patch_policy_filter=None):
    policies = {}
    policies['sw'] = None
    policies['patch'] = None
    swps = ts.swmgmt.SoftwarePolicyService
    wpps = ts.swmgmt.WindowsPatchPolicyService
    if sw_policy_filter:
        swpf = Filter()
        swpf.expression = "(software_policy_platform_id EQUAL_TO %s) & (%s)" % (platform.id, sw_policy_filter)
        swpf.objectType = 'software_policy'
        sw_policies = swps.findSoftwarePolicyRefs(swpf)
        if len(sw_policies) > 0:
            policies['sw'] = sw_policies
    if patch_policy_filter:
        wppf = Filter()
        wppf.expression = "(patch_policy_platform_id EQUAL_TO %s) & (%s)" % (platform.id, patch_policy_filter)
        wppf.objectType = 'patch_policy'
        patch_policies = wpps.findWindowsPatchPolicyRefs(wppf)
        if len(patch_policies) > 0:
            policies['patch'] = patch_policies
    return policies


def filter_servers_and_policies(servers, policies):
    filtered_result = {}
    filtered_result['servers'] = None
    filtered_result['sw'] = None
    filtered_result['patch'] = None
    auth_service = ts.fido.AuthorizationService
    filtered_servers = auth_service.filterSingleTypeResourceList(OperationConstants.REMEDIATE_SOFTWARE_POLICY, servers)
    filtered_servers = auth_service.filterSingleTypeResourceList(OperationConstants.INSTALL_PATCH_POLICY,
                                                                 filtered_servers)
    if len(filtered_servers) > 0:
        filtered_result['servers'] = filtered_servers
    if policies['sw']:
        filtered_sw_policies = auth_service.filterSingleTypeResourceList(OperationConstants.REMEDIATE_SOFTWARE_POLICY,
                                                                         policies['sw'])
        filtered_result['sw'] = filtered_sw_policies
    if policies['patch']:
        filtered_patch_policies = auth_service.filterSingleTypeResourceList(OperationConstants.INSTALL_PATCH_POLICY,
                                                                            policies['patch'])
        filtered_result['patch'] = filtered_patch_policies
    return filtered_result


def batch(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.next()], batchiter)


def default_notify(email):
    jobNotify = JobNotification()
    jobNotify.onSuccessOwner = email
    jobNotify.onFailureOwner = email
    jobNotify.onFailureRecipients = [email]
    jobNotify.onSuccessRecipients = [email]
    jobNotify.onCancelRecipients = [email]
    return jobNotify


