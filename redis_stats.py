#!/usr/bin/python
"""
    @author : koushik R
    Redis health checks
    30/10/2013
    """
import socket
import sys, time, os
import yaml
from optparse import OptionParser
from daemon import Daemon

EXIT_OK = 0
EXIT_WARN = 1
EXIT_CRITICAL = 2
server = '127.0.0.1'
port = 6379
redis_timeout = 2000
file_path = "/var/log/fk-redis.yml"
daemon_path = "/tmp/fk-redis.pid"

class RedisDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(2)
            main()

def get_info(host, port, timeout):
    socket.setdefaulttimeout(timeout or None)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    sent = s.send("\r\ninfo\r\n")
    total = int(s.recv(5)[1:5])
    start = 5
    buf = ""
    while start < total:
        buf += s.recv(start)
        total = total - start
    if total > 0: buf += s.recv(start)
    s.close()
    return dict(x.split(':', 1) for x in buf.split('\r\n') if ':' in x)

def get_key_count(info):
    keycount = 0
    try:
        keys = info.get('db0')
        keys = keys.split(',')
        keys = keys[0]
        keys = keys.split('=')
        keycount = keys[1]
    except:
        pass
    return keycount

def get_uptime(info):
    uptime = int(info['uptime_in_seconds'])
    ret = {}
    ret['d'] = uptime / 86400
    ret['h'] = (uptime % 86400) / 3600
    ret['m'] = (uptime % 3600) / 60
    ret['s'] = uptime
    return ret

def get_db_info(info):
    data = {}
    values = {}
    uptime = get_uptime(info)
    days = 'days'
    if uptime['d'] == 1:
        days = 'day'
    values['uptime'] = "%s %s, %s:%s h" % (uptime['d'], days, uptime['h'],uptime['m'])
    memory = int(info.get("used_memory_rss") or info["used_memory"]) / (1024*1024)
    values['memory_usage'] = "%dMB" % memory
    values['expired_keys'] = info.get('expired_keys')
    values['rejected_connections'] = info.get('rejected_connections')
    values['mem_fragmentation_ratio'] = info.get('mem_fragmentation_ratio')
    values['keycount'] = get_key_count(info)
    if info.get("role") == "slave":
        values['last_io_from_master'] = int(info.get("master_last_io_seconds_ago"))
        values['sync_in_progress'] = int(info.get("master_sync_in_progress"))
        data['slave'] = values
    else:
        data['master'] = values
    return data

def main():
    info = get_info(server, port, timeout=redis_timeout / 1000.0)
    data = get_db_info(info)
    with open(file_path, "w+") as redis_yml:
        redis_yml.truncate()
        redis_yml.write(yaml.dump(data, allow_unicode=True, default_flow_style=False))

if __name__ == "__main__":
    DEVNULL = "/dev/null"
    if (hasattr(os, '/dev/null')):
        DEVNULL = os.devnull

    daemon = RedisDaemon(daemon_path, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    if len(sys.argv) == 2:
        if "start" == sys.argv[1]:
            print "Starting the Daemon process"
            daemon.start()
        elif "stop" == sys.argv[1]:
            print "Stopping the Daemon process"
            daemon.stop()
        elif "restart" == sys.argv[1]:
            print "Restarting the daemon process"
            daemon.restart()
        else:
            print "Unknown command. Please use one of start/stop/restart"
            sys.exit(EXIT_CRITICAL)
        sys.exit(EXIT_OK)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(EXIT_CRITICAL)
