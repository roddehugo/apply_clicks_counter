# Apply Clicks Counter @ Work4

## ArchLinux
ArchLinux is installed on the Raspberry Pi. You can find all you want [on ArchLinux Website](http://archlinuxarm.org/platforms/armv6/raspberry-pi)

## Connect to the RPi
You can plug a HDMI screen and a keyboard to the RPi. Useful when it's the first time you boot your system frechly installed on SD card.

You can also ssh to the RPi if you're connected to the same local network (Currently only Ethernet wiring is working).

Find the RPi local IP address using tools like [LanScan](https://itunes.apple.com/us/app/lanscan/id472226235?mt=12)
Here are the RPi info :
- Local IP: `10.12.2.238`
- MAC Address: `b8:27:eb:7d:77:d6`
- Vendor Name: `Raspberry Pi Foundation`

Ssh to the RPi :

```bash
ssh root@10.12.2.238
```

## Code

The code is pulled from the Github repo into `/root/apply_clicks_counter`.
There is a `systemd` [timer](https://wiki.archlinux.org/index.php/Systemd/Timers) which automatically start (or restart) the application on device boot and every day.

The timer is configured in `ac-counter.timer` located into `/etc/systemd/system/` directory.
