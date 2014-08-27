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

## Running in Production
Most scripts are light-weight and can be run either from a SA-Managed Server or from the Global Shell. (Check the User Guide for details on the Global Shell)

However, the remediation script can take up 30+ minutes to run if you are targeting a large number of servers.

Ensure that the server you are running from has a solid network connection. Or if using the Global Shell, ensure that your VPN does not time out.




#### License and Legal
All scripts are provided under the MIT License, unless otherwise noted, and are provided without warranty express or implied. 
I make no claim for the effectiveness, safety, security or quality of the scripts contained within.

