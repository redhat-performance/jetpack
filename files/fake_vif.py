# special subclass of FakeDriver that also adds OVS controls.
# this file should be copied into the Nova installation in the local
# Python, such as /usr/lib/python2.7/site-packages/nova/virt/fake_vif.py
# It then can be invoked from nova.conf via
# compute_driver=fake_vif.OVSFakeDriver

import netaddr

import nova.conf
from nova import utils
from nova.virt import fake

from oslo_concurrency import processutils
from oslo_log import log as logging


CONF = nova.conf.CONF

LOG = logging.getLogger(__name__)


def execute_wrapper(args, root_helper):
    LOG.info(
        "running command: %s",
        " ".join(str(arg) for arg in args),
    )
    try:
        return processutils.execute(*args, run_as_root=True,
                                    root_helper=root_helper)
    except Exception as e:
        LOG.error(
            "Unable to execute %(cmd)s. Exception: %(exception)s",
            {"cmd": args, "exception": e},
        )
        raise


def add_namespace(ns):
    root_helper = utils.get_root_helper()
    full_args = ["ip", "netns", "add", ns]
    execute_wrapper(full_args, root_helper)
    full_args = ["ip", "netns", "exec", ns, "ip", "link", "set", "lo", "up"]
    execute_wrapper(full_args, root_helper)


def delete_namespace(ns):
    root_helper = utils.get_root_helper()
    # deleting namespace will delete its ports and veth pairs
    full_args = ["ip", "netns", "del", ns]
    execute_wrapper(full_args, root_helper)


def add_port_ip_addresses(ns, ovs_port, ip_addresses):
    root_helper = utils.get_root_helper()
    for address in ip_addresses:
        full_args = ["ip", "netns", "exec", ns,
                     "ip", "addr", "add", address, "dev", ovs_port]
        execute_wrapper(full_args, root_helper)


def add_port(ns, bridge, ovs_port, port_id, mac_address):
    root_helper = utils.get_root_helper()
    full_args = ["ovs-vsctl", "--may-exist", "add-port", bridge, ovs_port,
                 "--", "set", "Interface", ovs_port, "type=internal",
                 "--", "set", "Interface", ovs_port,
                 "external_ids:iface-id=%s" % port_id,
                 "--", "set", "Interface", ovs_port,
                 "external-ids:iface-status=active",
                 "--", "set", "Interface", ovs_port,
                 "external-ids:attached-mac=%s" % mac_address]
    execute_wrapper(full_args, root_helper)
    full_args = ["ip", "link", "set", ovs_port, "netns", ns]
    execute_wrapper(full_args, root_helper)
    namespace = ["ip", "netns", "exec", ns]
    full_args = namespace + ["ip", "link", "set", ovs_port, "up"]
    execute_wrapper(full_args, root_helper)
    namespace = ["ip", "netns", "exec", ns]
    full_args = namespace + ["ip", "link", "set", ovs_port, "address", mac_address]
    execute_wrapper(full_args, root_helper)


def delete_port(ns, bridge, ovs_port):
    root_helper = utils.get_root_helper()
    full_args = ["ovs-vsctl", "--if-exists", "del-port", bridge, ovs_port]
    execute_wrapper(full_args, root_helper)


class OVSFakeDriver(fake.FakeDriver):
    def __init__(self, *arg, **kw):
        LOG.info("Spinning up OVSFakeDriver")
        super(OVSFakeDriver, self).__init__(*arg, **kw)

    def spawn(self, context, instance, image_meta, injected_files,
              admin_password, allocations, network_info=None,
              block_device_info=None):
        self.plug_vifs(instance, network_info)
        ret = super(OVSFakeDriver, self).spawn(context, instance,
            image_meta, injected_files, admin_password, allocations,
            network_info=network_info, block_device_info=block_device_info)
        return ret

    def destroy(self, context, instance, network_info, block_device_info=None,
                destroy_disks=True):
        self.unplug_vifs(instance, network_info)
        return super(OVSFakeDriver, self).destroy(context, instance,
            network_info, block_device_info=block_device_info,
            destroy_disks=destroy_disks)

    def get_ip_addresses(self, vif):
        addresses = []
        network = vif.get("network", {})
        for subnet in network.get("subnets", []):
            if subnet and subnet.get("version", "") == 4:
                cidr = subnet.get("cidr", None)
                for ip in subnet.get("ips", []):
                    ip_address = ip.get("address", None)
                    if cidr and ip_address:
                        prefixlen = netaddr.IPNetwork(cidr).prefixlen
                        ip_address = "%s/%s" % (ip_address, prefixlen)
                        addresses = addresses + [ip_address]
        return addresses

    def plug_vif(self, instance, vif):
        bridge = "br-int"
        dev = vif.get("devname")
        port = vif.get("id")
        mac_address = vif.get("address")
        if not dev or not port or not mac_address:
            return
        ns = "fake-%s" % instance.uuid
        add_port(ns, bridge, dev, port, mac_address)
        ip_addresses = self.get_ip_addresses(vif)
        add_port_ip_addresses(ns, dev, ip_addresses)

    def plug_vifs(self, instance, network_info):
        """Plug VIFs into networks."""
        ns = "fake-%s" % instance.uuid
        add_namespace(ns)
        for vif in network_info:
            self.plug_vif(instance, vif)

    def unplug_vif(self, instance, vif):
        bridge = "br-int"
        dev = vif.get("devname")
        port = vif.get("id")
        if not dev:
            if not port:
                return
            dev = "tap" + str(port[0:11])
        ns = "fake-%s" % instance.uuid
        delete_port(ns, bridge, dev)

    def unplug_vifs(self, instance, network_info):
        """Unplug VIFs from networks."""
        for vif in network_info:
            self.unplug_vif(instance, vif)
        # delete namespace after removing ovs ports
        ns = "fake-%s" % instance.uuid
        delete_namespace(ns)
