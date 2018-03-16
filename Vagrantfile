# -*- mode: ruby -*-
# vi: set ft=ruby :

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'

Vagrant.configure("2") do |config|
  config.vm.provider "docker" do |d|
    d.build_dir = "."
    d.has_ssh = true
    d.name = 'billing-container'
    d.create_args = ['--name=billing-container']
    d.remains_running = true
  end

  config.ssh.username   = 'root'
  config.ssh.password = 'root'
  config.vm.hostname = "billing"
  config.vm.define "billing"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "public_network"
  config.ssh.forward_agent = true
  config.vm.synced_folder ".", "/var/www/billing"
  config.vm.provision :ansible do |ansible|
    ansible.playbook      = ".ansible/run.yml"
    ansible.become = true
  end
end
