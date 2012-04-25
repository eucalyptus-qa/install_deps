#!/usr/bin/python

import os
import sys 
import euca_qa
 
sys.excepthook = euca_qa.euca_except_hook(False, True)
config = euca_qa.read_test_config()
ret = 0
 
for host in config['hosts']:
    pkgs = []
    boto_path = ''
    if host.has_role('clc'):
        if host.build_type == "REPO" and config['esxhosts']:
            pkgs.append('eucalyptus-broker')
        if host.dist in ['fedora', 'centos', 'rhel']:
            pkgs.append('mysql')
            if host.getVersion().startswith('2.0'):
                pkgs.extend(["euca2ools", "python26-boto", "vblade"])
                # No need to patch boto, so don't set boto_path
            elif host.getVersion().startswith('eee-2.0'):
                pkgs.extend(["python-boto-eee", "patch", "python-M2Crypto", "vblade"])
                boto_path = '/usr/lib/python2.5/site-packages/'
        elif host.dist in ['debian', 'ubuntu']:
            if host.getVersion().startswith('2.0') or host.getVersion().startswith('eee-2.0'):
                pkgs.extend(["python-boto=1.9b*", "patch", "euca2ools"])
                boto_path = '/usr/share/pyshared/'
        elif host.dist == 'opensuse':
            continue
        elif host.dist in ['vmware', 'windows']:
            continue
        else:
            print "Unknown distro.  Giving up."
            print "Line was: %s" % line
            sys.exit(1)

        if pkgs:
            ret |= host.install_pkgs(pkgs)
        if boto_path:
            ret |= host.putfile('addusergrant.patch', 'addusergrant.patch')
            ret |= host.run_command("patch -N -p1 -r- -d %s < addusergrant.patch 2>&1 | grep -v -q FAILED" % boto_path)

if ret > 0:
    print "[TEST_REPORT] FAILED installing manual dependencies"
else:
    print "[TEST_REPORT] SUCCESS"
