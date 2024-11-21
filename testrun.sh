#!/bin/bash

export ANSIBLE_PYTHON_INTERPRETER=$(which python3)
echo 'Copy role to default ansible path'
sudo rm -r ~/.ansible/roles/host_inspector/*
sudo cp -r ../$(basename $(pwd))/* ~/.ansible/roles/host_inspector
echo
ansible-playbook -i tests/inventory tests/test.yml