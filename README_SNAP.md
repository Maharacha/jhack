This folder holds snap information for jhack.

Development rebuild oneliner:

    sudo snap remove --purge jhack; snapcraft; sudo snap install --dangerous ./jhack_[version]_amd64.snap


To publish a new snap version and release on edge:

    snapcraft upload ./jhack_[...].snap --release=edge

## Setup:
Jhack snap has a bunch of plugs. This should suffice:

    sudo snap connect jhack:dot-local-share-juju snapd
