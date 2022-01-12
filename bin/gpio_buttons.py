#!/usr/bin/env python3

import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from gpiozero import Button
from signal import pause
import subprocess as sp

toggle_font_size = '''cd /tmp
            if test -f papertty.smol; then
                rm papertty.smol
                rm papertty.normal
                touch papertty.large
            elif test -f papertty.large; then
                rm papertty.smol
                rm papertty.large
                touch papertty.normal
            else
                rm papertty.normal
                rm papertty.large
                touch papertty.smol
            fi
            systemctl restart papertty'''

reboot_cmd = '''
                rm /tmp/papertty.smol
                rm /tmp/papertty.large
                sync
                halt '''
hdmi = '''
            /usr/games/cowsay hdmi |wall
            touch /tmp/hdmi.out
        '''
doc = '''doc | font | sw
cs 21 | hdmi | halt'''

CONFIG = {  26: f'echo "{doc}" | /usr/games/cowsay -n |wall',
            19: toggle_font_size,
            21: '/usr/games/cowsay 21|wall',
            20: hdmi,
            16: reboot_cmd }

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
        battery_voltage = chan.voltage
        battery_str = str(battery_voltage)[:4]
        if battery_voltage < 3.2:
            sp.call(f'/usr/games/cowsay "Voltage Warning: {battery_str}" | wall', shell=True)
        with open('/tmp/battery_voltage', 'w') as f:
            f.write(battery_str)
        time.sleep(120)

    #pause()
