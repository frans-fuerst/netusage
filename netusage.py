#!/bin/python

import logging
import psutil
import time
import socket

class process_info:
    def __init__(self, name):
        self.active = False
        self.name = name
        self.connections = {}

class connection_info:
    def __init__(self):
        self.valid = False
        self.established = False
        self.socket = "none"
        self.remote = "unknown"

def main():

    process_list = {}
    while True:
        for pid in process_list:
            process_list[pid].active = False

        for pid in psutil.get_pid_list():
    
            try:
                process = psutil.Process(pid)
                io_counters = process.get_io_counters()
                connections = process.get_connections()
#                print io_counters
                
            except Exception, ex:
                print ex
                continue

            if not pid in process_list:
                process_list[pid] = process_info(process.name)

            process_list[pid].active = True

            for c in process_list[pid].connections:
                process_list[pid].connections[c].valid = False

            for c in connections:
                if not c in process_list[pid].connections:
                    process_list[pid].connections[c] = connection_info()

                process_list[pid].connections[c].valid = True

                process_list[pid].connections[c].remote = "listening"
                if c.status == 'ESTABLISHED':
                    #continue

                    process_list[pid].connections[c].established = True

                    _host = c.remote_address[0]
                    
                    try:
                        _host = socket.gethostbyaddr( c.remote_address[0] )
                    except:
                        pass

                    process_list[pid].connections[c].remote = "%s:%d" % (_host, c.remote_address[1])

                    try:
                        s = socket.fromfd(c.fd, c.family, c.type)
                        process_list[pid].connections[c].socket = s
                    except Exception, ex:
                        #print ex
                        process_list[pid].connections[c].socket = "bad"


        print "========================="
        for pid, pinfo in process_list.iteritems():
            if not pinfo.active: continue

            connections = [c for c in pinfo.connections if pinfo.connections[c].valid]
            if connections == []: continue

            print pid, pinfo.name
            for c in connections:
                if not pinfo.connections[c].established: continue
                print "    ", pinfo.connections[c].remote, pinfo.connections[c].socket
                

        time.sleep( 1 )

if __name__ == "__main__":

    logging.addLevelName( logging.CRITICAL, '(CRITICAL)' )
    logging.addLevelName( logging.ERROR,    '(EE)' )
    logging.addLevelName( logging.WARNING,  '(WW)' )
    logging.addLevelName( logging.INFO,     '(II)' )
    logging.addLevelName( logging.DEBUG,    '(DD)' )
    logging.addLevelName( logging.NOTSET,   '(NA)' )

    log = logging.getLogger( "test" )
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s","%y%m%d-%H%M%S")

    ch.setFormatter(formatter)

    log.addHandler(ch)

    log.warning("info")

    main()
