# set up the default terminal
ENV["TERM"]="linux"
default_box = "opensuse/Leap-15.2.x86_64"
box_version = "15.2.31.247"

Vagrant.configure("2") do |config|
  
  # set the image for the vagrant box
 config.vm.define "master" do |master|
     master.vm.box = default_box
     master.vm.box_version = box_version
     master.vm.hostname = "master"
     master.vm.network 'private_network', ip: "192.168.63.255",  virtualbox__intnet: true
     #master.vm.network "forwarded_port", guest: 22, host: 2222, id: "ssh", disabled: true
     #master.vm.network "forwarded_port", guest: 22, host: 2000 # Master Node SSH
     master.vm.network "forwarded_port", guest: 80, host: 8080
     master.vm.network "forwarded_port", guest: 9090, host: 9090
     master.vm.network "forwarded_port", guest: 8080, host: 8080
     master.vm.network "forwarded_port", guest: 8081, host: 8081
     master.vm.network "forwarded_port", guest: 8082, host: 8082
     #config.vm.network "forwarded_port", guest: 8888, host: 8080
     master.vm.network "forwarded_port", guest: 9090, host: 8888
     master.vm.network "forwarded_port", guest: 3000, host: 3000
     master.vm.network "forwarded_port", guest: 3030, host: 3030
     master.vm.network "forwarded_port", guest: 8080, host: 8080
     master.vm.network "forwarded_port", guest: 16686, host: 8088
     #master.vm.network "forwarded_port", guest: 8000, host: 8888
     master.vm.network "forwarded_port", guest: 8888, host: 8888
     master.vm.network "forwarded_port", guest: 8000, host: 8000
     config.vm.network "forwarded_port", guest: 6443, host: 6443

     master.vm.provider "virtualbox" do |vb|
       vb.memory = "4096"
       vb.name = "k3s"
       vb.gui = true
       vb.customize ["modifyvm", :id, "--ioapic", "on"]
     end
    end

     # Enable provisioning with a shell script. Additional provisioners such as
     # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
     # documentation for more information about their specific syntax and use.
     config.vm.provision "shell", inline: <<-SHELL
         sudo zypper --non-interactive install apparmor-parser
     SHELL

     args = []
         config.vm.provision "k3s shell script", type: "shell",
             path: "k3s.sh",
             args: args

end
