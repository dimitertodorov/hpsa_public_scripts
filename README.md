ITS - Public HPSA Scripts
=========================

A collection of some scripts I have made for HPSA (HP Server Automation)

## Development and Testing
Most of my development is done on a Windows server that is running the HPSA agent.

In order to execute the scripts, you need to setup the following environment to bring the python binary into your path.

```
setlocal
set PATH=%SystemDrive%\Program Files\Opsware\agent\lcpython15;%SystemDrive%\Program Files\Opsware\agent\bin;%PATH%
set PYTHONPATH=%SystemDrive%\Program Files\Opsware\agent\pylibs
```

---

### Authentication
Authentication while running these scripts is done one of the following ways.
* Specify as options to the program. Using -u and -p
* Use the environment variables **SA_USER** and **SA_PWD**
* Inherit permissions from the Global Shell under which the user is running. 

Most scripts here use the following code to perform the authentication.
```python
if opts.username and opts.password:
    ts.authenticate(opts.username,opts.password)
elif os.environ.has_key('SA_USER') and os.environ.has_key('SA_PWD'):
    ts.authenticate(os.environ['SA_USER'],os.environ['SA_PWD'])
else:
    print "Username and Password not provided. Script may fail unless running in OGSH. \n Specify with -u username -p password"
```    


#### License and Legal
All scripts are provided under the MIT License, unless otherwise noted, and are provided without warranty express or implied. 
I make no claim for the effectiveness, safety, security or quality of the scripts contained within.

