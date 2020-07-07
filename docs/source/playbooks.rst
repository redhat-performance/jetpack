Playbooks
=========

In Jetpack all the playbooks are called from `main.yml <https://github.com/redhat-performance/jetpack/blob/master/main.yml>`_. We can skip running specific playbooks using tags.

`bootstrap.yml <https://github.com/redhat-performance/jetpack/blob/master/bootstrap.yml>`_
------------------------------------------------------------------------------------------

It runs only on ansible controller node to prepare it for running the jetpack and infrared ansible tasks.

This playbook imports:

  * install_packages.yml
  * load_instackenv.yml
  * setup_infrared.yml
  * setup_undercloud.yml

`setup_undercloud.yml <https://github.com/redhat-performance/jetpack/blob/master/setup_undercloud.yml>`_
--------------------------------------------------------------------------------------------------------

This playbook will prepare undercloud for installation like installing specific OS on undercloud based on OSP release if needed, copy ansible controller node ssh key on undercloud, create a stack user and add undercloud to inventory.

This playbook imports:

  * prepare_undercloud.yml

`virtual_undercloud.yml <https://github.com/redhat-performance/jetpack/blob/master/virtual_undercloud.yml>`_
------------------------------------------------------------------------------------------------------------

If virtual_uc is set to true in `group_vars/all.yml <https://github.com/redhat-performance/jetpack/blob/master/group_vars/all.yml>`_  you can create a undercloud vm on ansible controller node instead of deploying undercloud in a baremetal. Do not enable this while running from desktop.

In `group_vars/all.yml <https://github.com/redhat-performance/jetpack/blob/master/group_vars/all.yml>`_ verify the following values to create a undercloud vm.

  * ``virtual_uc: true``
  * ``undercloud_host: 172.16.0.2``
  * ``vm_external_interface: eth0``
  * ``undercloud_local_interface: eth0``

`add_undercloud_to_inventory.yml <https://github.com/redhat-performance/jetpack/blob/master/add_undercloud_to_inventory.yml>`_
------------------------------------------------------------------------------------------------------------------------------

Adds undercloud to inventory in ansible controller node.

`prepare_nic_configs.yml <https://github.com/redhat-performance/jetpack/blob/master/prepare_nic_configs.yml>`_
--------------------------------------------------------------------------------------------------------------

This playbook will create nic-configs for the overcloud. In `group_vars/all.yml <https://github.com/redhat-performance/jetpack/blob/master/group_vars/all.yml>`_  we define interface based on the machine type.

For example, if undercloud hostname is f05-1029p.scalelab.com, then machine type is “1029p” and from group_vars/all.yaml

Scale:
  machine_types:
     Supermicro:
          1029p: [enp94s0f0, enp94s0f1, enp94s0f2, enp94s0f3]

Usage of interfaces

  * First interface will be used for external network in nic-configs
  * Second interface will be used for contro plane network (pxe)
  * Remaining interface for other nic-config networks

`undercloud.yml <https://github.com/redhat-performance/jetpack/blob/master/undercloud.yml>`_
--------------------------------------------------------------------------------------------

This playbook will install undercloud on the undercloud node using “infrared tripleo-undercloud” command.

Tasks include

  * Prepare undercloud.conf
  * Get the control plane interface from undercloud through udevadm
  * For OSP14 and above, we need to pass container registry defined in group_vars/all.yaml as undercloud is unable to pull from the default registries provided by infrared 

`introspect.yml <https://github.com/redhat-performance/jetpack/blob/master/intropsect.yml>`_
--------------------------------------------------------------------------------------------

This playbook runs introspection through

``infrared tripleo-overcloud --introspect yes --instackenv-file ~/overcloud_instackenv.json``

Here overcloud_instackenv.json serves a instackenv.json file excluding the undercloud node. If some nodes fail during introspection they are automatically deleted using ``delete_introspection_failed_nodes.yml``

`tag.yml <https://github.com/redhat-performance/jetpack/blob/master/intropsect.yml>`_
-------------------------------------------------------------------------------------

This playbook tags the nodes by calling

``infrared tripleo-overcloud --tagging yes``

`external.yml <https://github.com/redhat-performance/jetpack/blob/master/external.yml>`_
----------------------------------------------------------------------------------------
Playbook to setup external networking and overcloud endpoint access on the undercloud

`overcloud.yml <https://github.com/redhat-performance/jetpack/blob/master/overcloud.yml>`_
------------------------------------------------------------------------------------------

This playbook deploys overcloud through

``infrared tripleo-overcloud -vvv --version {{ osp_release }} --build {{ osp_puddle }}  --deployment-files {{ nic_configs }} --introspect no --tagging no --deploy yes --controller-nodes {{ controller_count }} --compute-nodes {{ compute_count }} --overcloud-templates {{ infrared_dir }}/plugins/tripleo-overcloud/vars/overcloud/templates/extra.yml --network-protocol ipv4 --network-backend {{ network_backend }} --public-network false > {{ log_directory }}/overcloud_deploy.log 2>&1``

In the above command

  * osp_release, osp_puddle, nic_configs, controller_count are specified in `group_vars/all.yml <https://github.com/redhat-performance/jetpack/blob/master/group_vars/all.yml>`_ 
  * compute_count - It is calculated from the no.of introspection successful nodes subtracted by the no.of controller nodes
  * {{ infrared_dir }}/plugins/tripleo-overcloud/vars/overcloud/templates/extra.yml is the extra templates file to deploy overcloud
  * log_directory stores all the jetpack logs on ansible controller node

`browbeat.yml <https://github.com/redhat-performance/jetpack/blob/master/browbeat.yml>`_
----------------------------------------------------------------------------------------

This playbook installs browbeat on undercloud

`cleanup.yml <https://github.com/redhat-performance/jetpack/blob/master/cleanup.yml>`_
--------------------------------------------------------------------------------------

Cleans up the files on the ansible controller node
