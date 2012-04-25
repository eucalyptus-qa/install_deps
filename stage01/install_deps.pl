#!/usr/bin/perl

do 'config.pl';

my $exitcode= 0;

sub install_pkg {
    my ($ip, $distro, $pkg) = @_;
    my $result;
    $distro =~ tr/[A-Z]/[a-z]/;
    if ($distro =~ /(centos|rhel|fedora)/i) {
        $result = ssh($ip, "yum -y install $pkg --nogpgcheck");
    } elsif ($distro =~ /opensuse/i) {
        $result = ssh($ip, "zypper -y install $pkg");
    } else {
        $result = ssh($ip, "apt-get install -y $pkg");
    }
    if ($result != 0) {
        print "[TEST REPORT] FAILED to install $pkg on $ip\n";
        $exitcode = 1;
    } else {
        print "[TEST REPORT] Successfully installed $pkg on $ip\n";
    }
}

foreach my $specp (@all) { 
    my %spec = %$specp; # dereference the pointer for readability
    if ($spec{distro} =~ /VMWARE/i)  {
        next;
    }
    if ($spec{distro} =~ /(centos|rhel)/i) {
        install_pkg($spec{ip}, $spec{distro}, "mysql");
    }
    if (scalar keys %esx_hosts > 0) {
        foreach my $role (@{$spec{role}}) {
            if (($role =~ /CLC\d*/) and ($spec{source} eq "REPO")) {
                install_pkg($spec{ip}, $spec{distro}, "eucalyptus-broker");
            }
        }
    }
}

exit($exitcode);
