sudo apt-get install -y software-properties-common
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get install -y ansible
sudo apt-get install -y git
git clone --single-branch --branch scramble-pishahang https://github.com/CN-UPB/pg-scrambLe.git
cd pg-scrambLe/phishahang/Pishahang-master/son-install

git checkout install-pishahang
# git clone https://github.com/CN-UPB/Pishahang.git
mkdir ~/.ssh
echo sonata | tee ~/.ssh/.vault_pass

ansible-playbook utils/deploy/sp.yml -e "target=localhost public_ip=131.234.29.102" -v


export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
# press enter for all
sudo dpkg-reconfigure locales