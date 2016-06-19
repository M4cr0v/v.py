#!/usr/bin/env python
# encoding: utf-8

import libvirt
import sys
import commands
import os
from functools import partial
try:
    from tabulate import tabulate
except ImportError, e:
    print e
    print 'Please install tabulate first, command: "pip install tabulate".'
    raise ImportError

def createConnection():
    """Create connection to the libvirt
    :returns: TODO

    """
    conn = libvirt.open(None)
    if not conn:
        print 'Failed to open connection to libvirt'
        sys.exit(1)
    else:
        return conn

def closeConnection(conn):
    """Close connection to the libvirt

    :conn: TODO
    :returns: TODO

    """
    try:
        conn.close()
    except Exception, e:
        print 'Failed to close the connection', e
        return 1
    else:
        return 0

def getDomainDisplayPort(dom_name, display_type):
    """TODO: Docstring for getDomainDisplayPort.

    :dom_name: TODO
    :display_type: TODO
    :returns: TODO

    """
    cmd_str = 'virsh domdisplay %s --type %s' % (dom_name, display_type)
    status, output = commands.getstatusoutput(cmd_str)
    if status:
        port = -1
    else:
        port = int(output.split(':')[-1].split('/')[0])
    return port

def virDomainList(*args):
    """List all domain info in this host
    
    :returns: TODO

    """
    virDomainState = {
        0: 'NOSTATE',     #/* no state */
        1: 'RUNNING',     #/* the domain is running */
        2: 'BLOCKED',     #/* the domain is blocked on resource */
        3: 'PAUSED',      #/* the domain is paused by user */
        4: 'SHUTDOWN',    #/* the domain is being shut down */
        5: 'SHUTOFF',     #/* the domain is shut off */
        6: 'CRASHED',     #/* the domain is crashed */
        7: 'PMSUSPENDED'  #/* the domain is suspended by guest power management */
    }
    headers=['Id', 'Name', 'VNC', 'SPICE', 'UUID', 'State', 'MaxMemory', 'MEMORY', 'VCPUS', 'CpuTime']
    conn = createConnection()
    doms = conn.listAllDomains()
    info_table = list()
    for dom in doms:
        dom_info = list()
        dom_info.append(dom.ID())
        dom_info.append(dom.name())
        vnc_port = getDomainDisplayPort(dom.name(), 'vnc')
        spice_port = getDomainDisplayPort(dom.name(), 'spice')
        dom_info.append(vnc_port)
        dom_info.append(spice_port)
        dom_info.append(dom.UUIDString())
        info = dom.info()
        dom_info.append(virDomainState[info[0]])
        dom_info.extend(info[1:])
        info_table.append(dom_info)
    closeConnection(conn)
    info_table.sort()
    sorted_info_table = [x for x in info_table if x[0] >= 0] + [x for x in info_table if x[0] < 0]
    output = tabulate(sorted_info_table, headers=headers)
    status = 0
    return (status, output)

def virDomainEditXML(*args):
    """TODO: Docstring for virDomainEditXML.

    :dom_name: TODO
    :returns: TODO

    """
    status = 1
    output = 'v command doest not support editing XML of domain, use "virsh edit" directly'
    return (status, output)

modified_cmds={
    "list"   : virDomainList,
    "edit"   : virDomainEditXML,
}

def get_virsh_cmds():
    """TODO: Docstring for get_virsh_cmds.
    :returns: TODO

    """
    cmd_str = 'virsh help'
    status, help_str = commands.getstatusoutput(cmd_str)
    virsh_cmds = {}
    for x in help_str.split('\n')[1:]:
        if "help keyword" not in x and x.strip(" "):
            key = x[:35].strip(" ")
            value = x[35:].strip(" ")
            virsh_cmds[key] = value
    return virsh_cmds

def lookup_full_cmd(short_cmd):
    """lookup full command with short command

    :short_cmd: TODO
    :returns: a dictionary of matched commands

    """
    virsh_cmds = get_virsh_cmds()
    if short_cmd in virsh_cmds.keys():
        return {short_cmd: virsh_cmds.get(short_cmd)}
    else:
        #return {k:v for k,v in virsh_cmds.items() if k.startswith(short_cmd)}  #python 2.7 or 3.0
        return dict((k, v) for k,v in virsh_cmds.items() if k.startswith(short_cmd))  #python 2.6

def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    args = sys.argv[:]
    argc = len(args)
    if argc < 2:
        cmd_str = 'virsh help'
        func = partial(commands.getstatusoutput, cmd_str)
    else:
        full_cmds = lookup_full_cmd(args[1])
        if len(full_cmds) > 1:
            print "Do you mean the following commands?"
            print tabulate([[k, v] for k, v in full_cmds.items()])
#            for cmd, help_str in full_cmds.items():
#                print "%s    : %s" % (cmd, help_str)
            sys.exit(1)
        elif len(full_cmds) == 1:
            args[1] = full_cmds.keys()[0]
            if args[1] in modified_cmds:
                func = partial(modified_cmds[args[1]], args[2:] if argc > 2 else list())
            else:
                cmd_str = 'virsh %s' % (' '.join(args[1:]))
                func = partial(commands.getstatusoutput, cmd_str)
        else:
            print "Unknown command '%s', try '%s help'" % (args[1], os.path.basename(sys.argv[0]))
            sys.exit(1)
    try:
        status, output = func()
        print output
    except Exception, e:
        print "Execute command failed,", e

if __name__ == '__main__':
    main()
