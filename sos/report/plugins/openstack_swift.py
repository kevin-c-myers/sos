# Copyright (C) 2013 Red Hat, Inc., Flavio Percoco <fpercoco@redhat.com>
# Copyright (C) 2012 Rackspace US, Inc.,
#               Justin Shepherd <jshepher@rackspace.com>
# Copyright (C) 2009 Red Hat, Inc., Joey Boggs <jboggs@redhat.com>

# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

from sos.report.plugins import Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin


class OpenStackSwift(Plugin):

    short_desc = 'OpenStack Swift'
    plugin_name = "openstack_swift"
    profiles = ('openstack', 'openstack_controller')

    var_puppet_gen = "/var/lib/config-data/puppet-generated"

    def setup(self):
        if self.get_option("all_logs"):
            self.add_copy_spec([
                "/var/log/swift/",
            ])
        else:
            self.add_copy_spec([
                "/var/log/swift/*.log",
            ])

        self.add_copy_spec([
            "/etc/swift/",
            self.var_puppet_gen + "/swift/etc/*",
            self.var_puppet_gen + "/swift/etc/swift/*",
            self.var_puppet_gen + "/swift/etc/xinetd.d/*",
            self.var_puppet_gen + "/memcached/etc/sysconfig/memcached"
        ])

        self.add_file_tags({
            "/etc/swift/swift.conf": "swift_conf",
            "/var/log/swift/swift.log": "swift_log"
        })

    def apply_regex_sub(self, regexp, subst):
        self.do_path_regex_sub(r"/etc/swift/.*\.conf.*", regexp, subst)
        self.do_path_regex_sub(
            self.var_puppet_gen + r"/swift/etc/swift/.*\.conf.*",
            regexp, subst
        )

    def postproc(self):
        protect_keys = [
            "ldap_dns_password", "neutron_admin_password", "rabbit_password",
            "qpid_password", "powervm_mgr_passwd", "virtual_power_host_pass",
            "xenapi_connection_password", "password", "host_password",
            "vnc_password", "admin_password", "transport_url"
        ]
        connection_keys = ["connection", "sql_connection"]

        self.apply_regex_sub(
            r"((?m)^\s*(%s)\s*=\s*)(.*)" % "|".join(protect_keys),
            r"\1*********"
        )
        self.apply_regex_sub(
            r"((?m)^\s*(%s)\s*=\s*(.*)://(\w*):)(.*)(@(.*))" %
            "|".join(connection_keys),
            r"\1*********\6"
        )


class DebianSwift(OpenStackSwift, DebianPlugin, UbuntuPlugin):

    packages = (
        'swift',
        'swift-account',
        'swift-container',
        'swift-object',
        'swift-proxy',
        'swauth',
        'python-swift',
        'python-swauth'
    )


class RedHatSwift(OpenStackSwift, RedHatPlugin):

    packages = ('openstack-selinux',)

# vim: set et ts=4 sw=4 :
