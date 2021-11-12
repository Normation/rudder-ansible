# -*- mode: ruby -*-
# vi: set ft=ruby :

# Copyright: (c) 2021, Normation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

VAGRANTFILE_API_VERSION = "2"

# All nodes with root server
stack = {
  "rudder-awx-root" => { 
    :cpus => 2, 
    :mem => 2048, 
    :vm_type => "root", 
    :ip_address => "10.0.0.10", 
    :box_base => "ubuntu/focal64" 
  },
  "rudder-awx-node1" => { 
    :cpus => 1, 
    :mem => 4096, 
    :vm_type => "node", 
    :ip_address => "10.0.0.11", 
    :box_base => "ubuntu/focal64" 
  },
  "rudder-awx-node2" => { 
    :cpus => 1, 
    :mem => 1024, 
    :vm_type => "node", 
    :ip_address => "10.0.0.12", 
    :box_base => "ubuntu/focal64" 
  },
}

# Check plugins
unless Vagrant.has_plugin?("vagrant-vbguest")
  puts 'Installing vagrant-vbguest Plugin...'
  system('vagrant plugin install vagrant-vbguest')
end

unless Vagrant.has_plugin?("vagrant-hostsupdater")
  puts 'Installing vagrant-hostsupdater Plugin...'
  system('vagrant plugin install vagrant-hostsupdater')
end

unless Vagrant.has_plugin?("vagrant-reload")
  puts 'Installing vagrant-reload Plugin...'
  system('vagrant plugin install vagrant-reload')
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  stack.each_with_index do |(hostname, info), index|
    
    config.vm.define hostname do |cfg|
      cfg.vm.provider :virtualbox do |vb, override|
        config.vm.box = info[:box_base]
        override.vm.network :private_network, ip: info[:ip_address]
        override.vm.hostname = hostname
        vb.name = hostname
        vb.customize ["modifyvm", :id, "--memory", info[:mem], "--cpus", info[:cpus], "--hwvirtex", "on"]
      end # end 'provider'
      
      # Don't check box update
      cfg.vm.box_check_update = "false"

      config.vm.synced_folder "./", "/root/dev/"
      config.vbguest.auto_update = true

      if info[:vm_type] == "root"
        cfg.vm.provision :shell, :path => "https://repository.rudder.io/tools/rudder-setup", :args => ["setup-server", "latest"]
      elsif info[:vm_type] == "node"
        cfg.vm.provision :shell, :path => "https://repository.rudder.io/tools/rudder-setup", :args => ["setup-agent", "latest", "10.0.0.10"]
      end
    end # end 'cfg'
  end # end 'stack'
end # end 'config'