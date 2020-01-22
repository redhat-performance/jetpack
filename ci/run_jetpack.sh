#!/bin/bash

cp ci/all_osp13.yml group_vars/all.yml
ansible-playbook -vvv main.yml 2>&1 | tee log
