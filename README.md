# Jetpack

JetPack is the easiest way to deploy Director/Tripleo on baremetal. 
JetPack will install OpenStack using infrared on a set of homogeneous servers. User can run JetPack from their laptop or an ansible jump host.
Once the user's baremetal node allocation is ready to use, they need to set below bare minimum variables.

```
cloud_name: cloud05
lab_type: scale
osp_release: 13
hammer_host: <FQDN/IP of host with hammer cli>
ansible_ssh_pass: default password of servers

```

For OSP releases > 13, the below variables also need to be set in [all.yml](group_vars/all.yml)
```
registry_mirror: <register_mirror>
registry_namespace: <namespace>
insecure_registries: <insecure_registry>
```
#Supported distros

Currently supported distros for ansible jump host are:

* > RHEL 7.7


# Requirements

* Ansible >= 2.8
* Python 3.6+
* > RHEL 7.7 for ansible jump host
* A host for running hammer cli/ipmitool/badfish operations referenced by the variable *hammer_host*
* Passwordless sudo for user running the playbook on the ansible control node (host where the playbooks are being run from)

Passwordless sudo can be setup as below:

```
echo "username ALL=(root) NOPASSWD:ALL" | tee -a /etc/sudoers.d/username
chmod 0440 /etc/sudoers.d/username
```

Below is the sequence of steps these playbooks run before deploying overcloud
1) Clone and setup infrared environment
2) Download instackenv file from the lab url (playbooks assume that undercloud is the first node in this instackenv file)
3) Prepare internal variables from this file i.e
   undercloud_host: first node in instackenv
   ctlplane_interface: will get the interface name from the mac provided in instackenv
4) Tasks prepare eligible physical interfaces on the hosts to be used for nic-configs
5) We use nic-configs based on number of interfaces present in nodes.
   We use 'virt' if we have 3 eligible free interfaces ( prepared from stemp 4)
   or 'virt_4nics' if more than 3 interfaces.
   Interface names in these default template files are replaced with physical nic names which we got from step 4 above.
6) Prepare overcloud_instackenv.json which will be used for describing overcloud baremetal nodes from instackenv file downloaded  from the scalelab.
   Tasks will remove undercloud node from the downloaded instackenv file and generate new overcloud_instackenv.json file.
7) Run infrared plugins
   a) tripleo-undercloud to install the undercloud
   b) tripleo-overcloud plugin to install overcloud

# Documentation
https://jetpack-docs.readthedocs.io/en/latest/

# Usage
1) Set required vars in group_vars/all.yml
2) run the playbook  
ansible-playbook main.yml  
**Note:** user shouldn't provide any inventory file as playbooks will internally prepare the inventory.

# Advanced usage

User can use tags for running specific playbooks. For example,
1) to skip undercloud setup run  
   ansible-playbook main.yml --skip-tags "setup_undercloud,undercloud"
2) to run only overcloud  
   ansible-playbook main.yml --tags "overcloud"

## Deploying with custom environment files  

To deploy the overcloud with custom environment files, the user needs to add a section similar to below in the group_vars/all.yml
```
extra_templates:
  - example.yml
  - /usr/share/openstack-tripleo-heat-templates/environments/services/sahara.yaml
parameter_defaults:
  NeutronServicePlugins: qos,ovn-router,trunk,segments
  NeutronTypeDrivers: geneve,flat
resource_registry:
  - OS::TripleO::NodeUserData=/home/stack/firstboot-nvme.yaml
  - OS::TripleO::Services::NeutronL3Agent: OS::Heat::None
```

*extra_templates* is a list of extra template files that you want to deploy the overcloud with. Jetpack searches the undercloud for these files when absolute path on undercloud is provided, and if the environment file does not exist on the undercloud then jetpack/files/ is searched on the ansible controller machine for the custom environment file user wants to deploy with and if it exists, copies it over to the undercloud from where it is used for deployment.
extra_templates:
  - /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ovn-ha.yaml
  - /home/stack/firstboot.yaml
In the above case, jetpack copies firstboot from jetpack/files/firstboot.yaml to undercloud's /home/stack folder, if it doesn't exit in the undercloud at /home/stack/firstboot.yaml.

*parameter_defaults* is a dictionary of key value pairs for customizing the deployment like ```NeutronOVSFirewallDriver: openvswitch```.
Specify them in group_vars/all.yml like below
parameter_defaults:
  NeutronServicePlugins: qos,ovn-router,trunk,segments
  NeutronTypeDrivers: geneve,flat

*resource_registry* is a list of resource type and its template that you want to deploy the overcloud with. Template can be a file path or ```OS::Heat::None```. Jetpack searches the undercloud for the template files when absolute path on undercloud is provided, and if the environment file does not exist on the undercloud then jetpack/files/ is searched on the ansible controller machine for the custom template file user wants to deploy with and if it exists, copies it over to the undercloud from where it is used for deployment.
resource_registry:
  - OS::TripleO::NodeUserData=/home/stack/firstboot-nvme.yaml
  - OS::TripleO::Services::NeutronL3Agent: OS::Heat::None
In the above case, jetpack copies firstboot-nvme.yaml from jetpack/files/firstboot-nvme.yaml to undercloud's /home/stack folder, if it doesn't exit in the undercloud at /home/stack/firstboot-nvme.yaml.


*passthrough_nvme* need to be configured to pass overcloud compute node's non-volatile memory express device directly to overcloud VM. Read [1] for details. ```flavor``` is used to create openstack flavor after the deployment in Jetpack's post module. We can get the nvme device details with the [get_nvme_details.sh](scripts/get_nvme_details.sh) script

Set the parameters in group_vars like below
passthrough_nvme:
    vendor_id: '144d'
    product_id: 'a804'
    address: '01:00.0'
    flavor:
      name: 'nvme'
      ram: 16384
      disk: 40
      vcpus: 4

[1] https://access.redhat.com/documentation/en-us/openshift_container_platform/3.11/html-single/scaling_and_performance_guide/index#providing-storage-to-an-etcd-node-using-pci-passthrough-with-openstack 

## Deploying with external public network

We can request scale lab team for external public network and use this for accessing overcloud VMs from outside LAB environment.

1) To use this public network, set public_external_interface: true in group_vars/all.yml 
2) Scale Lab team will enable public network on 4th interface of the nodes. For example, for 1029p nodes, this will be 'ens2f3' for osp version 14 and above, otherwise 'enp94s0f3'. Set this to external_interface variable i.e
external_interface: ens2f3
3) CIDR details provided by the scale lab team should be defined like below
external_gateway: 10.1.57.1/24
external_net_cidr: 10.1.57.0/24
external_allocation_pools_start: 10.1.57.10
external_allocation_pools_end: 10.1.57.30
external_interface_default_route: 10.1.57.1
Note: external_network_vlan_id shouldn't be defined as scale lab team configures this network with a vlan on external switch. We need to use this interface as access port and shouldn't define any VLANs on it. Also while creating overcloud external network after overcloud deployment, specify --provider:network_type as flat i.e
neutron net-create --router:external=True --provider:network_type flat --provider:physical_network datacentre public

## Containerize Jetpack

To run jetpack inside a container you need to update the group_vars/all.yml in your localhost as it will be consumed by the jetpack_container.sh script and podman should be installed.

Execute jetpack_container.sh script to build and run jetpack container.
   `./jetpack_container.sh`

## scale up compute nodes

To scale up the compute nodes of OSP deployments deployed by Jetpack, you have to follow the below steps.

1) Add the new nodes in new instack file
2) Provide the new instack file location on `new_nodes_instack` variable on group_vars file
3) Run the upscale.yml play to complete the scaleup
     `ansible-playbook upscale.yml`
Note: The udercloud will be fetched from the old `instackenv` file. if the file is not available, it will be downloaded from the server using the `cloud_name` and `lab_name` properties.

##  Usage of Composable roles (Non-uniform set of nodes)
Requirements
1) Undercloud and Controller nodes should be of same machine type
   Example:
   controller_count = 3, then it will consider the first node in instackenv.json as  undercloud and the next three nodes as controllers
2) set composable_roles: true in group_vars/all.yml

## Deployment with Ceph
On homogeneous set of machine type to deploy OSP with Ceph, set the following variables in group_vars/all.yml
   `ceph_node_count - to number ceph nodes`
   `ceph_enabled set to true to enable Ceph based deployment`
   `storage_node_disks- specify the disks for example storage_node_disks: [nvme0n1],
                        if you do not specify it get set based on the introspection
                        data`
   `osd_pool_default_pg_num - user needs to calculate and set it based on storage_node_disks`
   `osd_pool_default_pgp_num - user needs to calculate and set it based on storage_node_disks`
   `osd_objectstore can be set to filestore or bluestore. By default set to filestore`
   `osd_scenario can be set to collocated, non-collocated (for filestore) or lvm for (bluestore)`

For OSP deploy with Ceph using Composable Roles, After setting the above specified vars you need to set two additional vars in group_vars/all.yml i.e ceph_ifaces, ceph_machine_type.
   Example:
   For OSP16.1,
   `ceph_machine_type: '1029p'`
   `ceph_ifaces: [ens2f0, ens2f1, ens2f2, ens2f3]`

Note: User can customize [internal.yml.j2](templates/internal.yml.j2) template for Ceph deployment based on their
      requirement if needed
