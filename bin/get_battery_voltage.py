#!/usr/bin/python3.9
#!/usr/bin/python3.8
#!/usr/bin/env python3

import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
#import Adafruit_ADS1x15.ADS1x15 as ADS
#from Adafruit_ADS1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)
print("{:>5}\t{:>5}".format('raw', 'v'))
print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
