# Junos Space Packer
This project houses a Packer (http://packer.io) template for building and provisioning a Junos Space virtual appliance.

# Currently Supported Builders
- VirtualBox

# Planned Support
- VMWare

# Usage
#1 - Modify variables.json with your desired values
    - NOTE: You *MUST* choose an admin_password that meets Junos Space's requirements for the admin account.  The default value in variables.json meets those requirements.

#2 - Build Junos Space image with:
```
packer build -var-file=variables.json space-packer.json
```

#3 - Import outputted .ova file into VirtualBox
```
After running through the instantiation and provisioning process, Packer will output a .ova file you can then import into VirtualBox
```
