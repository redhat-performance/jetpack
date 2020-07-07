#/bin/bash

ansible_dir=/jetpack

# build jetpack container
podman build -t jetpack .

# run jetpack container
podman run -it \
      -v ./group_vars/all.yml:$ansible_dir/group_vars/all.yml:Z \
      -t localhost/jetpack
