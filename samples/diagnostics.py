#!/usr/bin/env python3

import sys
import subprocess as sp
from urllib import parse
try:
    from setproctitle import setproctitle
    setproctitle("mc-diagnostics.py")
except:
    pass

setproctitle("mc-diagnostics.py")

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
