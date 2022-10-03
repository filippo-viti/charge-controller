# charge-controller

## Supported devices

Any rooted Android device with a suitable control file should work. This was tested on a Oneplus 6T running stock
Android 10.

### Note on control files

For my smartphone, the control file is `/sys/class/power_supply/battery/charging_enabled`.  
This may change from device to device. Common control file names (there may be more):

- `charging_enabled`
- `battery_charging_enabled`
- `input_suspend`  
  You may have to test what works for you. A way to test this is by running `su` and then `echo 0 > control_file` either
  through adb or directly on your device.  
  You also may have to change the file that stores the current battery percentage which in my case
  is `/sys/class/power_supply/battery/capacity`. To test this just check if there's a file which shows your current
  percentage.

## Requirements

IMPORTANT: this software requires a rooted device to work. You also need to have USB debugging enabled and the USB
drivers for your device installed.  
This program requires the [adb_shell](https://github.com/JeffLIrion/adb_shell) python package by JeffLIrion to control
your android device via ADB.  
To install:

```
pip install adb-shell[usb]
```

## Usage

Simply run `main.py`. The phone will now only charge when it is between 20 and 80%  
[WIP] you can provide arguments to change the charging thresholds and the refresh timer.
