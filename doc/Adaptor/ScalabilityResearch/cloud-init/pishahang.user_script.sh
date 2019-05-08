#!/bin/bash
# Script to install Pishahang 
# output: {all: '| tee -a /var/log/cloud-init-output.log'}

getMyIP() {
    local _ip _myip _line _nl=$'\n'
    while IFS=$': \t' read -a _line ;do
        [ -z "${_line%inet}" ] &&
           _ip=${_line[${#_line[1]}>4?1:2]} &&
           [ "${_ip#127.0.0.1}" ] && _myip=$_ip
      done< <(LANG=C /sbin/ifconfig)
    printf ${1+-v} $1 "%s${_nl:0:$[${#1}>0?0:1]}" $_myip
}

getMyIP varHostIP
echo "Host IP = $varHostIP"

$different_user=$(uname -n)

echo "userdata running on hostname: $(uname -n)"
echo "Using sudo to install Git, Ansible"

sudo apt-get install -y software-properties-common
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get install -y git ansible

echo "Cloning Pishahang..."
mkdir -p /manosetup

git clone https://github.com/CN-UPB/Pishahang.git /manosetup/Pishahang

pushd /manosetup/Pishahang/son-install

mkdir ~/.ssh

echo sonata | tee ~/.ssh/.vault_pass

getMyIP varHostIP
echo "Host IP = $varHostIP"
echo "Host IP = $varHostIP" >> /manosetup/ip

ansible-playbook utils/deploy/sp.yml -e  "target=localhost public_ip=$varHostIP" -v