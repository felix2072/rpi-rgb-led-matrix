# Installation

`sudo apt-get install build-essential`

`systemctl show -p WantedBy network-online.target`

`sudo apt purge cloud-config`
`sudo systemctl disable iscsid.service`
`sudo systemctl disable open-iscsi.service`

`make -C examples-api-use`

# venv
install venv
`sudo apt install python3.12-venv`
create venv
`python3 -m venv /home/felix/rpi-rgb-led-matrix/venv`
activate venv
`source venv/bin/activate`
inistall pip3
`python3 -m pip install --upgrade pip`
check pip3 version
`python3 -m pip freeze`
install pillow (PIL)
`pip3 install pillow`
check pillow version
`python3 pillow --version`

# autologin
`sudo mkdir /etc/systemd/system/getty@tty1.service.d/`
`sudo nano /etc/systemd/system/getty@tty1.service.d/override.conf`

`[Service]
ExecStart=
ExecStart=-/sbin/agetty --noissue --autologin felix %I $TERM
Type=idle`

`sudo nano ~/.bashrc`
`if [ "$(tty)" = "/dev/tty1" ]; then
  /usr/bin/python3 /home/felix/rpi-rgb-led-matrix/bindings/python/daemon/levelselector.py
fi`

# Crontab - for autostart
`crontab -e`

add to the end of the file

`@reboot /usr/bin/python3 /home/felix/rpi-rgb-led-matrix/bindings/python/daemon/mpu_daemon.py &`
`@reboot cd /home/felix/rpi-rgb-led-matrix/bindings/python/samples && sudo /home/felix/rpi-rgb-led-matrix/venv/bin/python3 ./clock.py -r 16 --led-cols 32 --led-no-hardware-pulse LED_NO_HARDWARE_PULS>`

sudo needs credentials at start or grant execution without.
`sudo visudo`
`felix ALL=(ALL) NOPASSWD: /home/felix/rpi-rgb-led-matrix/venv/bin/python3`

save and reboot

check if the two processes are running
`ps -fC python3`
kill a process pid
`sudo kill -9 3331`

# Problems

felix@ledpi:~$ `sudo apt-get install build-essential`
[sudo] password for felix:
E: Could not get lock /var/lib/dpkg/lock-frontend. It is held by process 1939 (unattended-upgr)
N: Be aware that removing the lock file is not a solution and may break your system.
E: Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), is another process using it?

felix@ledpi:~$ `ps aux | grep unattended`
root         913  0.1  2.3 107840 21632 ?        Ssl  12:34   0:00 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
root        1939 68.0 12.2 352432 113280 ?       Sl   12:40   4:21 /usr/bin/python3 /usr/bin/unattended-upgrade
felix       2153  0.2  0.1   3688  1536 pts/0    S+   12:47   0:00 grep --color=auto unattended

felix@ledpi:~$ `sudo lsof /var/lib/dpkg/lock-frontend`
COMMAND    PID USER   FD   TYPE DEVICE SIZE/OFF  NODE NAME
unattende 1939 root    8uW  REG  179,2        0 60230 /var/lib/dpkg/lock-frontend

felix@ledpi:~$ `tail -f /var/log/unattended-upgrades/unattended-upgrades.log`
2025-04-09 12:40:50,558 INFO Starting unattended upgrades script
2025-04-09 12:40:50,562 INFO Allowed origins are: o=Ubuntu,a=noble, o=Ubuntu,a=noble-security, o=UbuntuESMApps,a=noble-apps-security, o=UbuntuESM,a=noble-infra-security
2025-04-09 12:40:50,564 INFO Initial blacklist:
2025-04-09 12:40:50,564 INFO Initial whitelist (not strict):
2025-04-09 12:48:18,957 INFO Packages that will be upgraded: binutils binutils-aarch64-linux-gnu binutils-common dirmngr dpkg gcc-14-base gnupg gnupg-l10n gnupg-utils gpg gpg-agent gpg-wks-client gpgconf gpgsm gpgv keyboxd krb5-locales libbinutils libcap2 libcap2-bin libctf-nobfd0 libctf0 libdw1t64 libelf1t64 libexpat1 libgcc-s1 libgnutls30t64 libgprofng0 libgssapi-krb5-2 libiniparser1 libk5crypto3 libkrb5-3 libkrb5support0 liblzma5 libpam-cap libpython3.12-minimal libpython3.12-stdlib libpython3.12t64 libsframe1 libssl3t64 libstdc++6 libtasn1-6 libxml2 libxslt1.1 linux-firmware linux-image-raspi openssh-client openssh-server openssh-sftp-server openssl python3-jinja2 python3.12 python3.12-minimal tzdata vim vim-common vim-runtime vim-tiny wpasupplicant xxd xz-utils
2025-04-09 12:48:18,959 INFO Writing dpkg log to /var/log/unattended-upgrades/unattended-upgrades-dpkg.log


🧠 What’s Happening:
It started at 12:40:50

At 12:48:18, it decided what packages to upgrade — a pretty hefty list (includes gcc, openssl, vim, openssh, even kernel stuff like linux-firmware)
It’s now likely running dpkg in the background to install those packages
So it's not stuck, just doing a big batch of updates — and that can take a while.

🧪 Want to monitor live progress?
You can watch what's happening with the actual package installs:
`tail -f /var/log/unattended-upgrades/unattended-upgrades.log`


# Display
`sudo /home/felix/rpi-rgb-led-matrix/venv/bin/python3 ./clock.py  -r 16 --led-cols 32 --led-no-hardware-pulse LED_NO_HARDWARE_PULSE --led-row-addr-type 2 --led-brightness 30 --led-multiplexing 13`

`sudo /home/felix/rpi-rgb-led-matrix/venv/bin/python3 ./demo -D0 --led-no-hardware-pulse --led-cols=32 --led-rows=16 --led-row-addr-type=2 --led-multiplexing=3 --led-brightness=50 --led-show-refresh`