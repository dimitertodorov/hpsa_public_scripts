ITS - Public HPSA Scripts
=========================

A collection of some scripts I have made for HPSA (HP Server Automation)

## Development and Testing
Most of my development is done on a Windows server that is running the HPSA agent.
I use [Sublime Text](http://www.sublimetext.com/) to work on my code.

In order to execute the scripts, you need to setup the following environment to bring the SA python binary into your path.

```
setlocal
set PATH=%SystemDrive%\Program Files\Opsware\agent\lcpython15;%SystemDrive%\Program Files\Opsware\agent\bin;%PATH%
set PYTHONPATH=%SystemDrive%\Program Files\Opsware\agent\pylibs
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
  --dry_run=dry_run     (Optional) Specify 1 here to skip remediation. Only
                        print what would be done.
```

Example:
The following will do the following:

* Find all Servers in Device Group 97960001
* Filter and group by Facility containing 'GDCPZ' and Platform Containing 'Windows 2008' or 'Windows 2003'
* Find all patch policies containg the name 'Security'
* Find all software policies with primary keys matching 420001 940001
* Chunk Jobs out into sizes of no more than 22
* Analyze will start after 5 minutes (Default)
* Action Time will start at the defined action time.
```
python batch_remediate.py --server_filter="(device_group_id EQUAL_TO 97960001)" --patch_policy_filter="(PatchPolicyVO.name CONTAINS Security)" --sw_policy_filter="(SoftwarePolicyVO.pK IN 420001 940001)" --facility_filter="FacilityVO.name CONTAINS GDCPZ" --platform_filter="((platform_name CONTAINS \"Windows 2008\")|(platform_name CONTAINS \"Windows 2003\"))" --action_time="2014-08-27T01:44:15" --dry_run=1 --chunk 22
```

## Running in Production
Most scripts are light-weight and can be run either from a SA-Managed Server or from the Global Shell. (Check the User Guide for details on the Global Shell)

However, the remediation script can take up 30+ minutes to run if you are targeting a large number of servers.

Ensure that the server you are running from has a solid network connection. Or if using the Global Shell, ensure that your VPN does not time out.




#### License and Legal
All scripts are provided under the MIT License, unless otherwise noted, and are provided without warranty express or implied. 
I make no claim for the effectiveness, safety, security or quality of the scripts contained within.

