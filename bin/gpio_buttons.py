#!/usr/bin/env python3

import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from gpiozero import Button
from signal import pause
import subprocess as sp

toggle = '''cd /tmp
            test -f papertty.smol \
                    && rm papertty.smol \
                    ||touch papertty.smol;
            systemctl restart papertty'''
CONFIG = {  26: '/usr/games/cowsay 26|wall',
            19: toggle,
            21: 'touch /tmp/gpio.21',
            20: 'touch /tmp/gpio.20',
            16: 'sync; sudo halt' }

def getFunc(cmd, btn):
    command  = cmd
    button = btn

    def runCommand():
        print(f"Button {button} Pressed! Running command: '{command}'")
        process = sp.Popen(command,
                            shell=True,
                            stdin=None,
                            stdout=open("/dev/null", "w"),
                            stderr=None,
                            executable="/bin/bash")
        process.wait()

    return runCommand


if __name__ == '__main__':
    buttons = []
    for num, cmd in CONFIG.items():
        func = getFunc(cmd, num)
        button = Button(num, hold_time=2)
        button.when_held = func
        buttons.append(button)
    
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1015(i2c)
    chan = AnalogIn(ads, ADS.P0)

    while True:
        battery_v = str(chan.voltage)[:4]
        with open('/tmp/battery_voltage', 'w') as f:
            f.write(battery_v)
        time.sleep(60)

    #pause()
