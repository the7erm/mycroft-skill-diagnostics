# mycroft-skill-diagnostics


| Intent      | Example Keyphrase                         | Function                                   | Output                                                                                                            |
|-------------|-------------------------------------------|--------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Cpu         | Mycroft, what is the current cpu percent? | Get the current cpu percentage.            | The cpu is currently running at 10%.  I'm working hard on &lt;list of processes&gt;                               |
| Diagnostics | Mycroft, run diagnostics.                 | Run external script                        |  One moment while I run the diagnostics script.  &lt;Whatever is printed to stdout of the diagnostics script.&gt; |
| Drive space | Mycroft, how's my hard drive space?       | List drive partitions & their space        | / has 52.3 Gig free it's used 71.7%<br>/home/erm/disk2 has 758.9 Gig free it's used 58.6%                         |
| Public Ip   | Mycroft, what is my public IP?            | Gets all the ip addresses from all nics    | This computer has the following lan IP addresses 192.168.1.116 and your public IP is [censored]                   |
| Uptime      | Mycroft, what's your uptime?              | Run `uptime -r` and get the output         | I have been up 2 days, 18 hours, 2 minutes                                                                        |

## Install
```
cd /opt/mycroft/skills
git clone https://github.com/the7erm/mycroft-skill-diagnostics.git skill-diagnostics
cd skill-diagnostics
workon mycroft
# if that doesn't work try `source <path to virtualenv/bin/activate>`
pip install -r requirements.txt
# restart the skills service
```

## Diagnostics
The diagnostics script needs to be defined in the `mycroft.conf` file, under the `DiagnosticsSkill` section. You can find more information about configuration files in the official [Mycroft Documentation](https://docs.mycroft.ai/development/configuration).  The script can be the output to any program you'd like.  Whatever the stdout is, will be what mycroft says.  Remember to restart the mycroft skills service once you add this.


## Example `DiagnosticsSkill` section on a `mycroft.conf` file.
```
...
"DiagnosticsSkill": {
    "script": "~/dummy-script.sh"
}
...
```

##### Example Diagnostics Script
```python
#!/usr/bin/env python3

import sys
import subprocess as sp
from urllib import parse
try:
    from setproctitle import setproctitle
    setproctitle("mc-diagnostics.py")
except:
    pass

urls = [
    "https://the-erm.com",
    "https://music.the-erm.com",
    "https://blog.the-erm.com"
]

servers = [
    'music.the-erm.com',
    'do.the-erm.com',
    'se.the-erm.com',
    'blog.the-erm.com',
    'www.the-erm.com',
    "mx1.the-erm.com"
]


def _print(*args):
    print(*args)
    sys.stdout.flush()


def run(cmd):
    child = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    out = ""
    err = ""
    ran_once = False
    while not ran_once or child.returncode is None:
        _out, _err = child.communicate()
        out += _out.decode("utf8")
        err += _err.decode("utf8")
        ran_once = True
    status = child.returncode
    return status, out, err


def wget(url):
    url_data = parse.urlparse(url)
    cmd = ["wget", "-qO-", "--tries=1", "--timeout=5", url]
    status, output, err = run(cmd)
    if status != 0:
        _print("web server " + str(url_data.netloc) + " is DOWN !")
    return status, url_data.netloc


def ping(host):
    # "ping -c1 -w2 " + str(host)
    cmd = ['ping', '-c1', '-w2', host]
    status, output, err = run(cmd)
    if status != 0:
        _print("Server " + str(host) + " is DOWN !")
    if err:
        _print("error:", err)

    return status


no_ping_servers = []

for host in servers:
    if ping(host):
        no_ping_servers.append(host)

if no_ping_servers:
    _print("There is a problem with the following servers %s" %
           ", ".join(no_ping_servers))

no_wget_urls = []
for url in urls:
    status, host = wget(url)
    if status:
        no_wget_urls.append(host)

if no_wget_urls:
    _print("There is a problem with the following web servers %s" %
           ", ".join(no_wget_urls))

if not no_wget_urls and not no_ping_servers:
    _print("All servers are up and responding to pings.")


```
