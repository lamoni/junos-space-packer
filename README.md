# Junos Space Packer
This project houses a Packer (http://packer.io) template for building and provisioning a Junos Space virtual appliance.

#Currently Supported Builders
- VirtualBox

#Planned Support
- VMWare

#Important Note

As of June 13, 2016, the mainline Packer binary does not support customizing the IP used to verify SSH connectivity
on the machine it is spinning up (for VirtualBox builders).  This was problematic because Space is a little different
than your normal Linux box, thus the SSH port forwarding that Packer usually does wasn't working, and the builds were
 failing.  To get around this, I forked Packer and added the capability.  A Pull Request (https://github.com/mitchellh/packer/pull/3617)
 has been submitted to Packer, but no guarantees on if/when it'll be accepted.  For now, if you want to use this, you
 MUST compile and use the following fork and branch of Packer to run space-packer.json: https://github.com/lamoni/packer/tree/issue2972-ssh_host-virtualbox

# Setup Prerequisites

- Ensure GoLang is installed
```
Explained here: https://github.com/mitchellh/packer/blob/master/CONTRIBUTING.md
```

- Set $GOPATH and ensure it's in your $PATH
```
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
```

- Install mitchellh/packer with "go get"
```
go get github.com/mitchellh/packer
```

- Remove packer folder and clone lamoni/packer into the directory, then switch to branch with ssh_host fix
```
cd ~/go/src/github.com/mitchellh/
rm -rf ./packer/
git clone https://github.com/lamoni/packer packer
cd packer/
git fetch
git checkout issue2972-ssh_host-virtualbox
```

- Compile lamoni/packer
```
cd ~/go/src/github.com/mitchellh/packer/
sudo -E make
```


# Usage
#1 - Modify variables.json with your desired values
    - NOTE: You *MUST* choose an admin_password that meets Junos Space's requirements for the admin account.  The default value in variables.json meets those requirements.

#2 - Build Junos Space image with:
```
$GOPATH/src/github.com/mitchellh/packer/bin/packer build -var-file=variables.json space-packer.json
```

#3 - Import outputted .ova file into VirtualBox
```
After running through the instantiation and provisioning process, Packer will output a .ova file you can then import into VirtualBox
```