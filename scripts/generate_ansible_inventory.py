# This script generates an ansible inventory files from
# overcloud-node-deployed.yaml.
# This script can be run after overcloud node provisioning
# or after overcloud deployment.
#
# Usage :
# python3 generate_ansible_inventory.py -i <hosts group, Eg.: controller> \
# -f <path to overcloud node deployed file> \
# -o <path to directory to store ansible inventory file>

import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--hosts_group",
    help="Group of hosts to generate inventory file(Eg.: controller)",
    nargs="?",
    required=True,
    dest="hostsgroup")
parser.add_argument(
    "-f",
    "--overcloud-node-deployed-file-path",
    help="Path to overcloud-node-deployed.yaml file",
    nargs="?",
    required=True,
    dest="overcloudnodedeployedfilepath",
)
parser.add_argument(
    "-o",
    "--hostsfiledir",
    help="Directory to write hosts file",
    nargs="?",
    required=True,
    dest="hostsfiledir",
)

with open(parser.parse_args().overcloudnodedeployedfilepath, "r") as f:
    dict = yaml.load(f)

hostsgroup = parser.parse_args().hostsgroup
ips = []
if hostsgroup == "overcloud":
    for i in dict["parameter_defaults"]["DeployedServerPortMap"]:
        ips.append(
            dict["parameter_defaults"]["DeployedServerPortMap"][i][
                "fixed_ips"][0]["ip_address"])
else:
    for i in dict["parameter_defaults"]["DeployedServerPortMap"]:
        if hostsgroup in i:
            ips.append(
                dict["parameter_defaults"]["DeployedServerPortMap"][i][
                    "fixed_ips"][0]["ip_address"])

with open("{}/{}_hosts_ips".format(parser.parse_args().hostsfiledir,
                                   hostsgroup), "w") as f2:
    print("[{}]".format(hostsgroup), file=f2)
    for i in ips:
        print(i, file=f2)
    print("\n", file=f2, end="")
    print("[all:vars]", "ansible_connection=ssh", "ansible_user=heat-admin",
          "ansible_ssh_common_args='-o StrictHostKeyChecking=no'", sep="\n",
          file=f2)
