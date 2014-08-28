ITS - Public HPSA Scripts
=========================

A collection of some scripts I have made for HPSA (HP Server Automation)

## Development and Testing
Most of my development is done on a Windows server that is running the HPSA agent.
I use [Sublime Text](http://www.sublimetext.com/) to work on my code.

In order to execute the scripts, you need to setup the following environment to bring the SA python binary into your path.

#### Windows
```
setlocal
set PATH=%SystemDrive%\Program Files\Opsware\agent\lcpython15;%SystemDrive%\Program Files\Opsware\agent\bin;%PATH%
set PYTHONPATH=%SystemDrive%\Program Files\Opsware\agent\pylibs
```

#### Unix
```
PYTHONPATH=/opt/opsware/agent/pylibs
export PYTHONPATH
PATH=/opt/opsware/agent/bin:${PATH}
export PATH
SRC=/opt/opsware/agent/pylibs/coglib
```

### Important Python Note
Python is a white-space sensitive language.
As such, you need to keep in mind the formatting.

Editing Python files in Notepad/Wordpad will not work most of the time.
You either need to use Sublime, or some other more advanced editor. Even VIM/Emacs works.

All python files I write are created with a tab equalling 4 spaces.

```python
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
```

---

### Authentication
Authentication while running these scripts is done one of the following ways.

* Specify as options to the program. Using -u and -p
* Use the environment variables **SA_USER** and **SA_PWD**
* Inherit permissions from the Global Shell under which the user is running. 
* Inherit the permissions of the Server from which it is running. This usually means you can only edit the server itself.

Most scripts here use the following code to perform the authentication.
```python
if opts.username and opts.password:
    ts.authenticate(opts.username,opts.password)
elif os.environ.has_key('SA_USER') and os.environ.has_key('SA_PWD'):
    ts.authenticate(os.environ['SA_USER'],os.environ['SA_PWD'])
else:
    print "Username and Password not provided. Script may fail unless running in OGSH. \n Specify with -u username -p password"
``` 

---

## Remediation Script Usage
FYI. This one is very complex.Consult the code, do not use without understanding the code.

**NOTE: ALL DATE/TIMES are expected in UTC**
```
options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -u username, --user=username
                        (Optional) User Name Only required if running outside
                        of OGSH context.
  -p password, --password=password
                        (Optional) Password. Only required if running outside
                        of OGSH context.
  -e email, --email=email
                        (Required) E-Mail
  --reboot=reboot       (Optional) Set to 1 if you want to reboot at the end
                        of remediation.
  --server_filter=server_filter
                        (Required) Servers which to Remediate
  --facility_filter=facility_filter
                        (Required) Facilities which to Remediate
  --platform_filter=platform_filter
                        (Required) Platforms which to Remediate
  --sw_policy_filter=sw_policy_filter
                        (Optional) SW Policies Filter to Remediate
  --patch_policy_filter=patch_policy_filter
                        (Optional) Patch Policies Filter to Remediate
  --analyze_time=analyze_time
                        (Optional) Time to start Analyze. Staging follows.
                        Format: '%Y-%m-%dT%H:%M:%S' e.g. 2014-08-29T20:15:15
  --analyze_spread=analyze_spread
                        (Optional) Time for the last job to start in minutes
                        after analyze time. (e.g. 240=4hours) If left blank,
                        analyze stage will be separated by 5 minutes
  --action_time=action_time
                        (Optional) Time to start actual Remediation. Format:
                        '%Y-%m-%dT%H:%M:%S'
  --action_spread=action_spread
                        (Optional) Time for the last job to start in minutes
                        after action time. (e.g. 240=4hours) If left blank,
                        action stage will be separated by 5 minutes
  --chunk=chunk         (Optional) Maximum number of servers per job. Default:
                        50
  --pre_script=pre_script
                        (Optional) Long ID of Script to run before action
                        stage.
  --post_script=post_script
                        (Optional) Long ID of Script to run after action
                        stage.
  --dry_run=dry_run     (Optional) Specify 1 here to skip remediation. Only
                        print what would be done.
```

Example:
The following will do the following:

* Find all Servers in Device Group 97960001
* Filter and group by Facility containing 'GDCPZ' and Platform Containing 'Windows 2008' or 'Windows 2003'
* Find all patch policies containg the name 'Security'
* Find all software policies with name containing "Windows Users"
* Chunk Jobs out into sizes of no more than 22
* Analyze will start at defined time. Rest of the steps will follow.
* Reboot will be at the end.
* Pre and Post scripts are set

```
python batch_remediate.py --server_filter="(device_group_id EQUAL_TO 97960001)" --patch_policy_filter="(PatchPolicyVO.name CONTAINS Security)" --sw_policy_filter="(SoftwarePolicyVO.name CONTAINS \"Windows Users\")" --facility_filter="FacilityVO.name CONTAINS GDCPZ" --platform_filter="((platform_name CONTAINS \"Windows 2008\")|(platform_name CONTAINS \"Windows 2003\")|(platform_name CONTAINS \"Windows 2012\"))" --analyze_time="2014-08-29T01:44:15" --dry_run=1 --chunk 22 --reboot=1 --pre_script=3620001 --post_script=3630001
```

Sample output (Dry Run Only):

```
(<GDCPZSCAFSAT (FacilityRef:120001) instance at 0x3971548>,)
(<Windows Server 2012 R2 x64 (PlatformRef:95000) instance at 0x3971f48>, <Windows Server 2008 (PlatformRef:160076) instance at 0x3971e88>, <Windows Server 2003 x64 (PlatformRef:60100) instance at 0x3971f08>, <Windows Server 2012 x64 (PlatformRef:170099) instance at 0x3971f88>, <Windows Server 2003 (PlatformRef:10007) instance at 0x3971fc8>, <Windows Server 2008 R2 x64 (PlatformRef:170092) instance at 0x3979048>, <Windows Server 2008 x64 (PlatformRef:170076) instance at 0x39790c8>, <Windows Server 2008 R2 IA64 (PlatformRef:100200) instance at 0x3979108>)
MAP Result: 0 results for: ((device_group_id EQUAL_TO 97960001))&(device_facility_id EQUAL_TO 120001)&(device_platform_id EQUAL_TO 95000)
MAP Result: 7 results for: ((device_group_id EQUAL_TO 97960001))&(device_facility_id EQUAL_TO 120001)&(device_platform_id EQUAL_TO 160076)
MAP Result: 2 results for: ((device_group_id EQUAL_TO 97960001))&(device_facility_id EQUAL_TO 120001)&(device_platform_id EQUAL_TO 60100)
MAP Result: 0 results for: ((device_group_id EQUAL_TO 97960001))&(device_facility_id EQUAL_TO 120001)&(device_platform_id EQUAL_TO 170099)
MAP Result: 11 results for: ((device_group_id EQUAL_TO 97960001))&(device_facility_id EQUAL_TO 120001)&(device_platform_id EQUAL_TO 10007)
MAP Result: 199 results for: ((device_group_id EQUAL_TO 97960001))&(device_facility_id EQUAL_TO 120001)&(device_platform_id EQUAL_TO 170092)
MAP Result: 3 results for: ((device_group_id EQUAL_TO 97960001))&(device_facility_id EQUAL_TO 120001)&(device_platform_id EQUAL_TO 170076)
MAP Result: 0 results for: ((device_group_id EQUAL_TO 97960001))&(device_facility_id EQUAL_TO 120001)&(device_platform_id EQUAL_TO 100200)
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008-CHUNK#0-COUNT7,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T01:44:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2003 x64-CHUNK#0-COUNT2,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T01:49:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2003-CHUNK#0-COUNT11,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T01:54:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#0-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T01:59:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#1-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:04:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#2-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:09:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#3-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:14:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#4-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:19:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#5-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:24:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#6-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:29:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#7-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:34:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#8-COUNT22,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:39:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 R2 x64-CHUNK#9-COUNT1,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:44:15,JOB_REF:DRY_RUN
REMEDIATE-PY-GDCPZSCAFSAT-Windows Server 2008 x64-CHUNK#0-COUNT3,PATCH_POLICIES: 13,SW_POLICIES: 1,REBOOT:at_end:WindowsPatchXOR,ANAL_START: 2014-08-29T02:49:15,JOB_REF:DRY_RUN
```

## Running in Production
Most scripts are light-weight and can be run either from a SA-Managed Server or from the Global Shell. (Check the User Guide for details on the Global Shell)

However, the remediation script can take up 30+ minutes to run if you are targeting a large number of servers.

Ensure that the server you are running from has a solid network connection. Or if using the Global Shell, ensure that your VPN does not time out.




#### License and Legal
All scripts are provided under the MIT License, unless otherwise noted, and are provided without warranty express or implied. 
I make no claim for the effectiveness, safety, security or quality of the scripts contained within.

