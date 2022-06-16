# Support scripts

This folder contains some usefull scripts which are used to deploy or debug OSP or OCP using Jetpack

### get_nvme_details.sh

this script can be used to find whether the machine supports nvme or not. if supports, it provides the nvme informations. like, address, product id, vendor id.

### infrared_osp16_1.sh

this script is used for deploying all-in-one OSP16.1 environment

Example:
  ./infrared_osp16_1.sh <hostname> full

### generate_ansible_inventory.py

This script generates an ansible inventory file from overcloud-node-deployed.yaml. This script can be run after overcloud node provisioning or after overcloud deployment.

Usage:
  python3 generate_ansible_inventory.py -i (hosts group, Eg.: controller) -f (path to overcloud node deployed file) -o (path to directory to store ansible inventory file)
