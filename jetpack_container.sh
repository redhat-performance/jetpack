#/bin/bash

ansible_dir=/jetpack

# build jetpack container
sudo podman build -t jetpack .

# run jetpack container
sudo podman run --privileged -it \
      -v ./group_vars/all.yml:$ansible_dir/group_vars/all.yml:Z \
      -t localhost/jetpack
