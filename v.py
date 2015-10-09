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

virsh_cmds={
    "attach-device"                : "attach device from an XML file",
    "attach-disk"                  : "attach disk device",
    "attach-interface"             : "attach network interface",
    "autostart"                    : "autostart a domain",
    "blkdeviotune"                 : "Set or query a block device I/O tuning parameters.",
    "blkiotune"                    : "Get or set blkio parameters",
    "blockcommit"                  : "Start a block commit operation.",
    "blockcopy"                    : "Start a block copy operation.",
    "blockjob"                     : "Manage active block operations",
    "blockpull"                    : "Populate a disk from its backing image.",
    "blockresize"                  : "Resize block device of domain.",
    "change-media"                 : "Change media of CD or floppy drive",
    "console"                      : "connect to the guest console",
    "cpu-baseline"                 : "compute baseline CPU",
    "cpu-compare"                  : "compare host CPU with a CPU described by an XML file",
    "cpu-stats"                    : "show domain cpu statistics",
    "create"                       : "create a domain from an XML file",
    "define"                       : "define (but don't start) a domain from an XML file",
    "desc"                         : "show or set domain's description or title",
    "destroy"                      : "destroy (stop) a domain",
    "detach-device"                : "detach device from an XML file",
    "detach-disk"                  : "detach disk device",
    "detach-interface"             : "detach network interface",
    "domdisplay"                   : "domain display connection URI",
    "domfsfreeze"                  : "Freeze domain's mounted filesystems.",
    "domfsthaw"                    : "Thaw domain's mounted filesystems.",
    "domfstrim"                    : "Invoke fstrim on domain's mounted filesystems.",
    "domhostname"                  : "print the domain's hostname",
    "domid"                        : "convert a domain name or UUID to domain id",
    "domif-setlink"                : "set link state of a virtual interface",
    "domiftune"                    : "get/set parameters of a virtual interface",
    "domjobabort"                  : "abort active domain job",
    "domjobinfo"                   : "domain job information",
    "domname"                      : "convert a domain id or UUID to domain name",
    "dompmsuspend"                 : "suspend a domain gracefully using power management functions",
    "dompmwakeup"                  : "wakeup a domain from pmsuspended state",
    "domuuid"                      : "convert a domain name or id to domain UUID",
    "domxml-from-native"           : "Convert native config to domain XML",
    "domxml-to-native"             : "Convert domain XML to native config",
    "dump"                         : "dump the core of a domain to a file for analysis",
    "dumpxml"                      : "domain information in XML",
    "edit"                         : "edit XML configuration for a domain",
    "event"                        : "Domain Events",
    "inject-nmi"                   : "Inject NMI to the guest",
    "send-key"                     : "Send keycodes to the guest",
    "send-process-signal"          : "Send signals to processes",
    "lxc-enter-namespace"          : "LXC Guest Enter Namespace",
    "managedsave"                  : "managed save of a domain state",
    "managedsave-remove"           : "Remove managed save of a domain",
    "memtune"                      : "Get or set memory parameters",
    "metadata"                     : "show or set domain's custom XML metadata",
    "migrate"                      : "migrate domain to another host",
    "migrate-setmaxdowntime"       : "set maximum tolerable downtime",
    "migrate-compcache"            : "get/set compression cache size",
    "migrate-setspeed"             : "Set the maximum migration bandwidth",
    "migrate-getspeed"             : "Get the maximum migration bandwidth",
    "numatune"                     : "Get or set numa parameters",
    "qemu-attach"                  : "QEMU Attach",
    "qemu-monitor-command"         : "QEMU Monitor Command",
    "qemu-monitor-event"           : "QEMU Monitor Events",
    "qemu-agent-command"           : "QEMU Guest Agent Command",
    "reboot"                       : "reboot a domain",
    "reset"                        : "reset a domain",
    "restore"                      : "restore a domain from a saved state in a file",
    "resume"                       : "resume a domain",
    "save"                         : "save a domain state to a file",
    "save-image-define"            : "redefine the XML for a domain's saved state file",
    "save-image-dumpxml"           : "saved state domain information in XML",
    "save-image-edit"              : "edit XML for a domain's saved state file",
    "schedinfo"                    : "show/set scheduler parameters",
    "screenshot"                   : "take a screenshot of a current domain console and store it into a file",
    "setmaxmem"                    : "change maximum memory limit",
    "setmem"                       : "change memory allocation",
    "setvcpus"                     : "change number of virtual CPUs",
    "shutdown"                     : "gracefully shutdown a domain",
    "start"                        : "start a (previously defined) inactive domain",
    "suspend"                      : "suspend a domain",
    "ttyconsole"                   : "tty console",
    "undefine"                     : "undefine a domain",
    "update-device"                : "update device from an XML file",
    "vcpucount"                    : "domain vcpu counts",
    "vcpuinfo"                     : "detailed domain vcpu information",
    "vcpupin"                      : "control or query domain vcpu affinity",
    "emulatorpin"                  : "control or query domain emulator affinity",
    "vncdisplay"                   : "vnc display",
    "domblkerror"                  : "Show errors on block devices",
    "domblkinfo"                   : "domain block device size information",
    "domblklist"                   : "list all domain blocks",
    "domblkstat"                   : "get device block stats for a domain",
    "domcontrol"                   : "domain control interface state",
    "domif-getlink"                : "get link state of a virtual interface",
    "domiflist"                    : "list all domain virtual interfaces",
    "domifstat"                    : "get network interface stats for a domain",
    "dominfo"                      : "domain information",
    "dommemstat"                   : "get memory statistics for a domain",
    "domstate"                     : "domain state",
    "domstats"                     : "get statistics about one or multiple domains",
    "domtime"                      : "domain time",
    "list"                         : "list domains",
    "capabilities"                 : "capabilities",
    "cpu-models"                   : "CPU models",
    "domcapabilities"              : "domain capabilities",
    "freecell"                     : "NUMA free memory",
    "freepages"                    : "NUMA free pages",
    "hostname"                     : "print the hypervisor hostname",
    "maxvcpus"                     : "connection vcpu maximum",
    "node-memory-tune"             : "Get or set node memory parameters",
    "nodecpumap"                   : "node cpu map",
    "nodecpustats"                 : "Prints cpu stats of the node.",
    "nodeinfo"                     : "node information",
    "nodememstats"                 : "Prints memory stats of the node.",
    "nodesuspend"                  : "suspend the host node for a given time duration",
    "sysinfo"                      : "print the hypervisor sysinfo",
    "uri"                          : "print the hypervisor canonical URI",
    "version"                      : "show version",
    "iface-begin"                  : "create a snapshot of current interfaces settings, which can be later committed (iface-commit) or restored (iface-rollback)",
    "iface-bridge"                 : "create a bridge device and attach an existing network device to it",
    "iface-commit"                 : "commit changes made since iface-begin and free restore point",
    "iface-define"                 : "define (but don't start) a physical host interface from an XML file",
    "iface-destroy"                : "destroy a physical host interface (disable it / 'if-down')",
    "iface-dumpxml"                : "interface information in XML",
    "iface-edit"                   : "edit XML configuration for a physical host interface",
    "iface-list"                   : "list physical host interfaces",
    "iface-mac"                    : "convert an interface name to interface MAC address",
    "iface-name"                   : "convert an interface MAC address to interface name",
    "iface-rollback"               : "rollback to previous saved configuration created via iface-begin",
    "iface-start"                  : "start a physical host interface (enable it / 'if-up')",
    "iface-unbridge"               : "undefine a bridge device after detaching its slave device",
    "iface-undefine"               : "undefine a physical host interface (remove it from configuration)",
    "nwfilter-define"              : "define or update a network filter from an XML file",
    "nwfilter-dumpxml"             : "network filter information in XML",
    "nwfilter-edit"                : "edit XML configuration for a network filter",
    "nwfilter-list"                : "list network filters",
    "nwfilter-undefine"            : "undefine a network filter",
    "net-autostart"                : "autostart a network",
    "net-create"                   : "create a network from an XML file",
    "net-define"                   : "define (but don't start) a network from an XML file",
    "net-destroy"                  : "destroy (stop) a network",
    "net-dhcp-leases"              : "print lease info for a given network",
    "net-dumpxml"                  : "network information in XML",
    "net-edit"                     : "edit XML configuration for a network",
    "net-event"                    : "Network Events",
    "net-info"                     : "network information",
    "net-list"                     : "list networks",
    "net-name"                     : "convert a network UUID to network name",
    "net-start"                    : "start a (previously defined) inactive network",
    "net-undefine"                 : "undefine a persistent network",
    "net-update"                   : "update parts of an existing network's configuration",
    "net-uuid"                     : "convert a network name to network UUID",
    "nodedev-create"               : "create a device defined by an XML file on the node",
    "nodedev-destroy"              : "destroy (stop) a device on the node",
    "nodedev-detach"               : "detach node device from its device driver",
    "nodedev-dumpxml"              : "node device details in XML",
    "nodedev-list"                 : "enumerate devices on this host",
    "nodedev-reattach"             : "reattach node device to its device driver",
    "nodedev-reset"                : "reset node device",
    "secret-define"                : "define or modify a secret from an XML file",
    "secret-dumpxml"               : "secret attributes in XML",
    "secret-get-value"             : "Output a secret value",
    "secret-list"                  : "list secrets",
    "secret-set-value"             : "set a secret value",
    "secret-undefine"              : "undefine a secret",
    "snapshot-create"              : "Create a snapshot from XML",
    "snapshot-create-as"           : "Create a snapshot from a set of args",
    "snapshot-current"             : "Get or set the current snapshot",
    "snapshot-delete"              : "Delete a domain snapshot",
    "snapshot-dumpxml"             : "Dump XML for a domain snapshot",
    "snapshot-edit"                : "edit XML for a snapshot",
    "snapshot-info"                : "snapshot information",
    "snapshot-list"                : "List snapshots for a domain",
    "snapshot-parent"              : "Get the name of the parent of a snapshot",
    "snapshot-revert"              : "Revert a domain to a snapshot",
    "find-storage-pool-sources-as" : "find potential storage pool sources",
    "find-storage-pool-sources"    : "discover potential storage pool sources",
    "pool-autostart"               : "autostart a pool",
    "pool-build"                   : "build a pool",
    "pool-create-as"               : "create a pool from a set of args",
    "pool-create"                  : "create a pool from an XML file",
    "pool-define-as"               : "define a pool from a set of args",
    "pool-define"                  : "define (but don't start) a pool from an XML file",
    "pool-delete"                  : "delete a pool",
    "pool-destroy"                 : "destroy (stop) a pool",
    "pool-dumpxml"                 : "pool information in XML",
    "pool-edit"                    : "edit XML configuration for a storage pool",
    "pool-info"                    : "storage pool information",
    "pool-list"                    : "list pools",
    "pool-name"                    : "convert a pool UUID to pool name",
    "pool-refresh"                 : "refresh a pool",
    "pool-start"                   : "start a (previously defined) inactive pool",
    "pool-undefine"                : "undefine an inactive pool",
    "pool-uuid"                    : "convert a pool name to pool UUID",
    "vol-clone"                    : "clone a volume.",
    "vol-create-as"                : "create a volume from a set of args",
    "vol-create"                   : "create a vol from an XML file",
    "vol-create-from"              : "create a vol, using another volume as input",
    "vol-delete"                   : "delete a vol",
    "vol-download"                 : "download volume contents to a file",
    "vol-dumpxml"                  : "vol information in XML",
    "vol-info"                     : "storage vol information",
    "vol-key"                      : "returns the volume key for a given volume name or path",
    "vol-list"                     : "list vols",
    "vol-name"                     : "returns the volume name for a given volume key or path",
    "vol-path"                     : "returns the volume path for a given volume name or key",
    "vol-pool"                     : "returns the storage pool for a given volume key or path",
    "vol-resize"                   : "resize a vol",
    "vol-upload"                   : "upload file contents to a volume",
    "vol-wipe"                     : "wipe a vol",
    "cd"                           : "change the current directory",
    "connect"                      : "(re)connect to hypervisor",
    "echo"                         : "echo arguments",
    "exit"                         : "quit this interactive terminal",
    "help"                         : "print help",
    "pwd"                          : "print the current directory",
    "quit"                         : "quit this interactive terminal"
}

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

def getDomainVNCPort(dom_name):
    """TODO: Docstring for getDomainVNCPort.

    :dom_name: TODO
    :returns: TODO

    """
    status, output = commands.getstatusoutput('virsh vncdisplay %s' % (dom_name))
    if status:
        port = -1
    else:
        port = int(output[1:])
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
    headers=['Id', 'Name', 'VNC', 'UUID', 'State', 'MaxMemory', 'MEMORY', 'VCPUS', 'CpuTime']
    conn = createConnection()
    doms = conn.listAllDomains()
    info_table = list()
    for dom in doms:
        dom_info = list()
        dom_info.append(dom.ID())
        dom_info.append(dom.name())
        dom_info.append(getDomainVNCPort(dom.name()))
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


def lookup_full_cmd(short_cmd):
    """lookup full command with short command

    :short_cmd: TODO
    :returns: a dictionary of matched commands

    """
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
