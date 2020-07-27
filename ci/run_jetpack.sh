#!/bin/bash

cp ci/all_osp13.yml group_vars/all.yml
cp ~/instackenv.json .
ansible-playbook -vvv main.yml
