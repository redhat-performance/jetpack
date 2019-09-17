# Description

This tool will install OSP using infrared on scale/alias lab machines.
User can run playbooks in this tool inside their laptop or a ansible jump host.
Once the user gets allocation mail from lab team, he has to set below bare minimum variables from the mail
```
cloud_name: cloud05
lab_type: scale
osp_release: 13
hammer_host: <FQDN/IP of host with hammer cli>
ansible_ssh_pass: default password of servers

```
# Requirements

Ansible >= 2.8
Python 3.5+ 
Passwordless sudo for user running the playbook on localhost (host where the playbooks are being run from)  
A host for hammer cli operations referenced by the variable *hammer_host*

```
echo "username ALL=(root) NOPASSWD:ALL" | tee -a /etc/sudoers.d/username
chmod 0440 /etc/sudoers.d/username
```

Below are the sequence of steps these playbooks run before deploying overcloud
1) Clone and setup infrared environment
2) Download instackenv file from scalelab (playbboks assume that undercloud is the first node in this instackenv file)
3) Prepare internal variables from this file i.e
   undercloud_host: first node in instackenv
   ctlplane_interface: will get the interface name from the mac provided in instackenv
4) Tasks prepare eligible physical interfaces on the hosts to be used for nic-configs
5) We use nic-configs based on number of interfaces present in nodes.
   We use 'virt' if we have 3 eligible free interfaces ( prepared from stemp 4)
   or 'virt_4nics' if more than 3 interfaces.
   Interface names in these default template files are replaced with physical nic names which we got from step 4 above.
6) Prepare undercloud_instackenv.json which will be used for tripleo undercloud install from instackenv file download from the scalelab.
   Tasks will remove undercloud node from the download file and generate new undercloud_instackenv.json file.
7) Run infrared plugins
   a) undercloud to install the undercloud
   b) overcloud plugin to install overcloud

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
  - NeutronOVSFirewallDriver: openvswitch`
```

*extra_templates* is a list of extra template files that you want to deploy the overcloud with. Jetpack searches the undercloud for these files when absolute path on undercloud is provided, and if the environment file does not exist on the undercloud then jetpack/files/ is searched on the ansible controller machine for the custom environment file user wants to deploy with and if it exists, copies it over to the undercloud from where it is used for deployment.

*parameter_defaults* is a list of key value pairs for customizing the deployment like ```NeutronOVSFirewallDriver: openvswitch```.
