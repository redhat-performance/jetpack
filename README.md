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

* Fedora 25,26,27
* RHEL 7.3,7.4,7.5,7.6,7.7


# Requirements

* Ansible >= 2.8
* Python 3.6+ 
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


*nvme* need to be configured to pass overcloud compute node's non-volatile memory express device directly to overcloud VM. Read [1] for details. ```flavor``` is used to create openstack flavor after the deployment in Jetpack's post module. We can get the nvme device details with the below script
cat ./get_nvme_address.sh
sudo yum install pciutils -y
nvme_exist=`lspci -nn | grep "Non-Volatile memory controller"`
if [[ $? == 0 ]]
then
   address=`lspci -nn | grep "Non-Volatile memory controller" | awk '{ print $1 }'`
   vendor=`lspci -nn | grep "Non-Volatile memory controller" | awk '{ print $NF }' | tr -d [] | cut -d: -f1`
   product=`lspci -nn | grep "Non-Volatile memory controller" | awk '{ print $NF }' | tr -d [] | cut -d: -f2`
   echo "nvme supported"
   echo "address: $address"
   echo "vendor_id: $vendor"
   echo "product_id: $product"
else
  echo "nvme not supported"
fi

Set the parameters in group_vars like below
nvme:
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
