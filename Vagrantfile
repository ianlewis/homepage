# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # All Vagrant configuration is done here. The most common configuration
    # options are documented and commented below. For a complete reference,
    # please see the online documentation at vagrantup.com.

    # Every Vagrant virtual environment requires a box to build off of.
    config.vm.box = "ubuntu/trusty64"

    # Create a private network, which allows host-only access to the machine
    # using a specific IP.
    config.vm.network "private_network", ip: "192.168.33.10"
     
    # Provision using ansible
    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "provisioning/site.yml"
        # ansible.inventory_path = "provisioning/local"
        ansible.groups = {
            "webservers" => ["default"],
            "appservers" => ["default"],
            "dbservers" => ["default"],
            "cacheservers" => ["default"],
            "local:children" => ["webservers", "appservers", "dbservers", "cacheservers"],
        }
    end
end
