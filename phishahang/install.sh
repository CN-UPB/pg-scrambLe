sudo apt-get install -y software-properties-common
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get install -y ansible
sudo apt-get install -y git
git clone --single-branch --branch scramble-pishahang https://github.com/CN-UPB/pg-scrambLe.git
cd pg-scrambLe/phishahang/Pishahang-master/son-install
mkdir ~/.ssh
echo sonata | tee ~/.ssh/.vault_pass
ansible-playbook utils/deploy/sp.yml -e "target=localhost public_ip=<your_ip4_address>" -v