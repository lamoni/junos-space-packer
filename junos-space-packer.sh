#!/bin/sh
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
cwd=$(pwd)

if [ ! -d "$GOPATH/src/github.com/mitchellh/packer" ]; then
    go get github.com/mitchellh/packer
fi

if [ ! -f "$GOPATH/src/github.com/mitchellh/junos-space-packer.flag" ]; then
    echo "true" >> $GOPATH/src/github.com/mitchellh/junos-space-packer.flag
    cd $GOPATH/src/github.com/mitchellh/
    sudo -E rm -rf ./packer/
    git clone https://github.com/lamoni/packer packer
    cd packer/
    git fetch
    git checkout issue2972-ssh_host-virtualbox
    git pull
    sudo -E make
fi



cd $cwd
mkdir -p http
if [ ! "$(ls -A http/jsnap.rpm)" ]; then

    # Download JSNAP
    python ./lib/juniper-support-scraper/juniper-support-scraper.py --output-name "http/jsnap.rpm" https://webdownload.juniper.net/swdl/dl/secure/site/1/record/12595.html $1 $2

fi

if [ ! "$(ls -A http/servicenow.img)" ]; then

    # Download Service Now
    python ./lib/juniper-support-scraper/juniper-support-scraper.py --output-name "http/servicenow.img" https://webdownload.juniper.net/swdl/dl/anon/site/1/record/60879.html $1 $2

fi

if [ ! "$(ls -A http/space.ova)" ]; then

    # Download Junos Space
    python ./lib/juniper-support-scraper/juniper-support-scraper.py --output-name "http/space.ova" https://webdownload.juniper.net/swdl/dl/secure/site/1/record/62382.html $1 $2

fi

$GOPATH/src/github.com/mitchellh/packer/bin/packer build -var-file=variables.json space-packer.json

