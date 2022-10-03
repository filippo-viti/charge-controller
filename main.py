import os.path
import time

from adb_shell.adb_device import AdbDeviceUsb
from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.exceptions import InvalidTransportError

CHARGE_LOWER_LIMIT = 20
CHARGE_UPPER_LIMIT = 80
REFRESH_TIMER = 60
CONTROL_FILE = '/sys/class/power_supply/battery/charging_enabled'
CAPACITY_FILE = '/sys/class/power_supply/battery/capacity'

device = None


def init_connection():
    global device

    while device is None:
        try:
            print('Attempting to find adb device...')
            device = AdbDeviceUsb()
        except InvalidTransportError:
            print('Device is missing or package is not installed with [usb] extra option')
        time.sleep(5)

    adbkey_path = './keys/adbkey'

    if not os.path.exists(adbkey_path):
        print('No keys were found, generating them')
        keygen(adbkey_path)

    with open(adbkey_path) as f:
        priv = f.read()
    with open(adbkey_path + '.pub') as f:
        pub = f.read()
    signer = PythonRSASigner(pub, priv)

    while not device.available:
        print('Connecting to device...')
        device.connect(rsa_keys=[signer], auth_timeout_s=0.1)
    print('Connection was successful')
    print('Attempting to gain root access')
    device.root()
    print('Root access gained')


def get_battery_percentage():
    return int(device.shell('su -c cat {}'.format(CAPACITY_FILE)))


def set_charging(value):
    device.shell("su -c 'echo {} > {}'".format(value, CONTROL_FILE))


def is_charging():
    return int(device.shell('su -c cat {}'.format(CONTROL_FILE)))


def charge():
    print('Device will start charging')
    set_charging(1)
    charge_percentage = get_battery_percentage()
    while charge_percentage < CHARGE_UPPER_LIMIT:
        charge_percentage = get_battery_percentage()
        time.sleep(REFRESH_TIMER)


if __name__ == '__main__':
    print('Daemon starting. Charging between {}% and {}%. Refreshing every {} seconds'.format(CHARGE_LOWER_LIMIT,
                                                                                              CHARGE_UPPER_LIMIT,
                                                                                              REFRESH_TIMER))
    init_connection()
    try:
        while True:
            current_percentage = get_battery_percentage()
            if current_percentage <= CHARGE_LOWER_LIMIT:
                charge()
            elif is_charging():
                set_charging(0)
                print('Charging stopped')
            time.sleep(REFRESH_TIMER)
    except KeyboardInterrupt:
        print('Exiting program, normal charging behaviour will be restored')
        set_charging(1)
        device.close()
