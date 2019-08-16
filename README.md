# infrared_perf
These playbooks install OSP using infrared on scale/alias lab machines. User can run these playbooks inside a ansible jump host.
Once the user gets allocation mail from lab team, he has to set below variables from the mail
cloud_name: cloud05
lab_type: alias
osp_release: 13
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
