#cloud-config
apt_update: true
packages:
  - nginx

write_files:
  - path: /var/www/html/index.nginx-debian.html
    content: |
      Hello from cloud-init-server-1
      