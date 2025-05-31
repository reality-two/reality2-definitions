## Setup

**Presently, it is recommended to use the `bash` startup methodology.**

### Set up the OS
- Install the default debian Raspberry PI OS on a Raspberry PI, ideally using Raspberry Pi Imager.
- Set the user to `reality2` and password to something, eg `reality2`.
- Set up the automatic login to boot to the `reality2` user.

### Start the Raspberry PI
- Insert the SDCard and boot up.  You should now be in the default screen for the Raspberry PI.

### Set up Reality2
- Download and extract the latest version of `reality2-node-core-elixir` from `releases` on the github repository as per the instructions there.
- Move the now decompresed `reality2` folder to the home folder.
  - ie, there should now be a folder `/home/reality2/reality2` that contains the Reality2 runtime.

### Set the autostart script
- Perform the following
```bash
cp ~/reality2/client-SBC/raspberry_pi/bash/reality2.desktop ~/.config/autostart
```

### Reboot
- Reboot the Raspberry PI and watch the autostart magic...

### What should happen
- When you reboot the Raspberry PI:
  - the desktop should open up
  - a terminal window should start showing that Reality2 is starting
  - a browser window should open up showing the map