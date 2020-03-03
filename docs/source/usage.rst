Usage
===== 
  * git clone https://github.com/redhat-performance/jetpack 

  * cd ~/work_dir/jetpack 

  * Update the variables in `group_vars/all.yml <https://github.com/redhat-performance/jetpack/blob/master/group_vars/all.yml>`_ 
    Once you have baremetal node allocation ready, and the credentials for the cloud you need to set the following variables in `group_vars/all.yml <https://github.com/redhat-performance/jetpack/blob/master/group_vars/all.yml>`_
     
     * ``cloud_name: <cloud name>``
     * ``lab_type: <lab type>``
     * ``osp_release: <osp release>``
     * ``hammer_host: <FQDN/IP of host with hammer cli>``
     * ``ansible_ssh_pass: <default password of servers>``

    For OSP > 13, set the below variables
     
     * ``registry_mirror: <register_mirror>``
     * ``registry_namespace: <namespace>``
     * ``insecure_registries: <insecure_registry>``
     * ``ansible-playbook -vvv main.yml``

Advanced Usage
==============

User can use tags for running specific playbooks. For example,

  * to skip undercloud setup run ``ansible-playbook main.yml --skip-tags "undercloud"``
  * to run only overcloud ``ansible-playbook main.yml --tags "overcloud"``

Deploying with Overcloud with custom environment files
------------------------------------------------------

To deploy the overcloud with custom environment files, the user needs to add a section similar to below in the `group_vars/all.yml <https://github.com/redhat-performance/jetpack/blob/master/group_vars/all.yml>`_ 

``extra_templates:``
  ``- example.yml``
``parameter_defaults:``
  ``- NeutronOVSFirewallDriver: openvswitch``
