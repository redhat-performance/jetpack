#!/bin/bash
HOST=$1
TOPOLOGY_NODES=undercloud:1,controller:1,compute:1
BASEDIR="/root/infrared-deploy"
VENVDIR="$BASEDIR/venv"
SSH_DIR=~/.ssh
SSHKEY="$SSH_DIR/id_rsa"
VERSION=16.1
BUILD=passed_phase2
LOGFILE="$BASEDIR/run.log"
PACKAGES=(git gcc libffi-devel openssl-devel python3-virtualenv libselinux-python3 ansible)
IMAGE_URL=http://download.eng.pek2.redhat.com/released/RHEL-8/8.2.0/BaseOS/x86_64/images/rhel-guest-image-8.2-290.x86_64.qcow2
NETWORK_BACKEND='geneve,vlan'
set -ex

if [ "$#" -ne 2 ]; then
    echo "Pass host and action as parameters" 2>&1
    echo "./$0 $1 cleanup|vms|uc|oc|full" 2>&1
    exit 1
fi


# cleanup previous vms
function cleanup_host() {

  if [ -f $VENVDIR/bin/activate ]; then

    source $VENVDIR/bin/activate

    infrared virsh --host-address ${HOST} \
      --host-key ${SSHKEY} \
      --topology-nodes ${TOPOLOGY_NODES} \
      --host-memory-overcommit True \
      --cleanup yes

      rm -rf $BASEDIR
  fi

}

# installs the required packages and generates a ssh key
function prep_env() {
  for PACKAGE in ${PACKAGES[@]}
  do
    yum install -y $PACKAGE
  done

  if [ -f "$SSHKEY" ]; then
    echo "ssh key exist"
  else
    ssh-keygen -q -N "" -f ${SSH_DIR}/id_rsa
    cat "$SSH_DIR/id_rsa.pub" >> "$SSH_DIR/authorized_keys"
  fi
}


# [provision new vms - same command without '--cleanup']
function create_vms() {

  mkdir -p $BASEDIR
  cd $BASEDIR

  git clone https://github.com/redhat-openstack/infrared.git

  virtualenv $VENVDIR

  source $VENVDIR/bin/activate
  pip install --upgrade pip
  pip install --upgrade setuptools
  cd $BASEDIR/infrared
  pip install .  2>&1 | tee $LOGFILE

  infrared virsh --host-address ${HOST} \
    --host-key ${SSHKEY} \
    --topology-nodes ${TOPOLOGY_NODES} \
    --host-memory-overcommit True \
    --image-url $IMAGE_URL
}


# installs undercloud
function undercloud_install() {

  source $VENVDIR/bin/activate
  cd $BASEDIR/infrared


  infrared tripleo-undercloud \
    --version ${VERSION} \
    --build ${BUILD} \
    --images-task rpm \
    --images-update no

}

# deploys overcloud
function overcloud_deploy() {
  source $VENVDIR/bin/activate
  cd $BASEDIR/infrared

  infrared tripleo-overcloud -v \
    --introspect yes \
    --tagging yes \
    --deploy  yes \
    --version $VERSION \
    --deployment-files virt \
    --network-protocol ipv4 \
    --network-backend $NETWORK_BACKEND \
    --network-ovn true

}

#installs browbeat and generates host file
function browbeat_install() {
  yum install -y ansible
  source $VENVDIR/bin/activate
  cd $BASEDIR/infrared
ssh -T -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa stack@undercloud-0 <<'EOSSH'
  source ~/stackrc
  git clone https://github.com/cloud-bulldozer/browbeat.git
  pushd ~/browbeat/ansible
  grep "8.8.8.8" ~/browbeat/ansible/install/group_vars/all.yml | sed 's/8.8.8.8/10.11.5.19/'
  ./generate_tripleo_hostfile.sh -l
  popd
EOSSH


#run browbeat
# need separate SSH session since Jenkins job seems to exit after running ansible host generation
ssh -T -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa root@undercloud-0 <<EOSSH
pwd
su - stack
pushd ~/browbeat/ansible
install browbeat
ansible-playbook -i hosts install/browbeat.yml
popd
EOSSH
}

case $2 in
cleanup)
        cleanup_host
;;
vms)
        cleanup_host
        prep_env
        create_vms
;;
uc)
        undercloud_install
;;
oc)
        overcloud_deploy
;;
full)
        cleanup_host
        prep_env
        create_vms
        undercloud_install
        overcloud_deploy
        browbeat_install
;;
*)
        echo "please choose between cleanup|vms|uc|oc|full"
;;
esac
