# Creating Virtual Machines in UTM on MacOS for deploying a K3s cluster

## Prepare the Virtual Machines

* Install UTM.
* Create a virtual machine with 8GB RAM and 40GB disk, name it k3s-test-01.
* Install Ubuntu Server 26.04.1 on the node (add yourself as a user with a password) -- you'll need an arm64 ISO for this.
* Log into the VM.
* Create the /storage directory:
  ```sh
  sudo mkdir /storage
  sudo chmod 755 /storage
  ```
* Add the ansible user with a password:
  ```sh
  sudo adduser ansible
  sudo usermod -a -G sudo ansible
  ```
* Install avahi utilities:
  ```sh
  sudo apt-get install avahi-daemon avahi-utils libnss-mdns
  sudo systemctl enable --now avahi-daemon.service
  sudo systemctl status avahi-daemon.service
  ```
* Edit the avahi configuration:
  ```sh
  sudo vi /etc/avahi/avahi-daemon.conf
  ```
  Add the following line under the commented-out line of the same setting name:
  ```
  allow-interfaces=enp0s1
  ```
  Save the file and exit the editor.
* Restart avahi:
  ```sh
  sudo systemctl restart avahi-daemon
  ```
* On your laptop, create an ssh keypair for the VMs (name the file id-k3s-test):
  ```sh
  cd ~/.ssh
  ssh-keygen -t rsa -b 4096 -m PEM
  ```
* Add the following to your ~/.ssh/config on your laptop, replacing `username` with your username which you created in the VM:
  ```
  # K3s test VMs on my laptop
  Host k3s-test-01.local k3s-test-02.local k3s-test-03.local
      User username
      Identityfile ~/.ssh/id-k3s-test
  ```
* Be sure you can log into the VM before continuing:
  ```sh
  ssh k3s-test-01.local
  ```
* Copy and paste the contents of *~/.ssh/id-k3s-test.pub* into the *~/.ssh/authorized_keys* file on the VM, for both the user you careated for yourself, and the ansible user.
* Halt the VM.
* In UTM, clone the VM twice.  Change the names of the clones to *k3s-test-02* and *k3s-test-03*, respectively.
* For each of the clones, in UTM, right-click, then click Edit -> Network.  Next to MAC Address, click Random.  Click Save.
* Start up all three VMs.
* In the second and third VM, login and run these commands, replacing `hostname` with k3s-test-02 and k3s-test-03, respectively:
  ```sh
  sudo hostnamectl set-hostname hostname
  sudo reboot
  ```
