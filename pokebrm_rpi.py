#!/usr/bin/python
#
# Connect 5V,GND,RX,TX,RTS,CTS to the rpi.  For RTS,CTS you will need
# to solder an extra pin header on the rpi, but no worries, it's easy.
#
# Use some tool to enable hardware flow control on the serial, we used
# rtscts...something.
#
# Idea: We are setting up some GATT characteristics and they should
# trigger notifies in the App, which should continue in the handshake
# protocol and write something to the CENTRAL_TO_SFIDA_CHAR.
# Reality: Nothing gets written.

import serial
import time

UUID_FW_UPDATE_SERVICE = "0000fef5-0000-1000-8000-00805f9b34fb";
UUID_DEVICE_CONTROL_SERVICE = "21c50462-67cb-63a3-5c4c-82b5b9939aeb";
UUID_LED_VIBRATE_CTRL_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939aec";
UUID_BUTTON_NOTIF_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939aed";
UUID_FW_UPDATE_REQUEST_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939aef";
UUID_FW_VERSION_CHAR = "21c50462-67cb-63a3-5c4c-82b5b9939af0";
UUID_CERTIFICATE_SERVICE = "bbe87709-5b89-4433-ab7f-8b8eef0d8e37";
UUID_CENTRAL_TO_SFIDA_CHAR = "bbe87709-5b89-4433-ab7f-8b8eef0d8e38";
UUID_SFIDA_COMMANDS_CHAR = "bbe87709-5b89-4433-ab7f-8b8eef0d8e39";
UUID_SFIDA_TO_CENTRAL_CHAR = "bbe87709-5b89-4433-ab7f-8b8eef0d8e3a";
UUID_BATTERY_SERVICE = "0000180F-0000-1000-8000-00805f9b34fb";
UUID_BATTERY_LEVEL_CHAR = "00002A19-0000-1000-8000-00805f9b34fb";
UUID_CLIENT_CHARACTERISTIC_CONFIG = "00002902-0000-1000-8000-00805f9b34fb";


def uuid_bytes(uuid):
    uuid = uuid.replace('-', '')
    return '-'.join([uuid[i:i+2] for i in range(0, len(uuid), 2)])


class BLEUART(object):
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyAMA0', 9600, rtscts=1)
        print(self.ser.name)

    def cmd_ok(self, cmd):
        time.sleep(0.05)
        self.ser.write(b'%s\r\n' % (cmd,))
        reply = self.ser.readline().strip()
        print('%s: %s' % (cmd, reply))

    def cmd_ret(self, cmd):
        time.sleep(0.05)
        self.ser.write(b'%s\r\n' % (cmd,))
        ret = self.ser.readline().strip()
        reply = self.ser.readline().strip()
        print('%s: %s | %s' % (cmd, ret, reply))
        return ret

    def reset(self):
        self.cmd_ok('ATE=0')
        self.cmd_ok('ATZ')
        time.sleep(1)
        self.cmd_ok('AT+FACTORYRESET')
        time.sleep(1)
        self.cmd_ret('ATE=0')  # read echo of this command

    def __del__(self):
        self.ser.close()


if __name__ == "__main__":
    ble = BLEUART()
    ble.reset()
    ble.cmd_ok('AT+GAPDEVNAME=Pokemon GO Plus')
    ble.cmd_ret('AT+GATTADDSERVICE=UUID128=%s' % (uuid_bytes(UUID_CERTIFICATE_SERVICE),))
    sfida_commands = int(ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_SFIDA_COMMANDS_CHAR),)))
    sfida_to_central = int(ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_SFIDA_TO_CENTRAL_CHAR),)))
    central_to_sfida = int(ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_CENTRAL_TO_SFIDA_CHAR),)))
    ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_CLIENT_CHARACTERISTIC_CONFIG),))
    ble.cmd_ret('AT+GATTADDSERVICE=UUID128=%s' % (uuid_bytes(UUID_FW_UPDATE_SERVICE),))
    ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_FW_UPDATE_REQUEST_CHAR),))
    ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_FW_VERSION_CHAR),))
    ble.cmd_ret('AT+GATTADDSERVICE=UUID128=%s' % (uuid_bytes(UUID_DEVICE_CONTROL_SERVICE),))
    ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_LED_VIBRATE_CTRL_CHAR),))
    ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_BUTTON_NOTIF_CHAR),))
    ble.cmd_ret('AT+GATTADDSERVICE=UUID128=%s' % (uuid_bytes(UUID_BATTERY_SERVICE),))
    ble.cmd_ret('AT+GATTADDCHAR=UUID128=%s,PROPERTIES=0x1A,MIN_LEN=1,MAX_LEN=8,DATATYPE=bytearray' % (uuid_bytes(UUID_BATTERY_LEVEL_CHAR),))
    ble.cmd_ok('AT+EVENTENABLE=0x0')
    ble.cmd_ok('AT+EVENTENABLE=0x1')
    ble.cmd_ok('AT+EVENTENABLE=0x2')
    for i in range(1, 10):
        ble.cmd_ok('AT+EVENTENABLE=0x0,0x%x' % (1<<i,))
    #ble.cmd_ok('AT+GATTCHAR=1,30-00')
    #ble.cmd_ok('AT+GATTCHAR=2,30-00')
    time.sleep(1)

    while True:
        a, b = [int(x, 0) for x in ble.cmd_ret('AT+EVENTSTATUS').split(',')]
        if a == 1:  # connect
            ble.cmd_ok('AT+GATTCHAR=%d,03-00-00-00' % (sfida_commands,))
            ble.cmd_ok('AT+GATTCHAR=%d,03-00-00-00' % (sfida_to_central,))
        elif b != 0:
            if b == 3:
                ble.cmd_ret('AT+GATTCHAR=%d' % (sfida_to_central,))
        time.sleep(0.5)
