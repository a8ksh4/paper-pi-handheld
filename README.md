# Paper Pi Handheld
This is the Raspberry Pi E-Ink Handheld, an art project with a few goals in mind:
* Implement a reliable battry power and charging system
* Custom thumb Keyboard with the Miryoku layout that I wanted more experience with.  Also an opportunity to hand-wire a Keyboard.
* Put this eink dispiay to use.  It's console centric, and seemed like a good opportunity to get better with console tools.  E.G. becoming proficient with "screen".  And the Keyboard layout caters to emacs, so I might spend some time there instead of vi.
* Further develop my 3D design skills.

<img src="/images/1.jpg" alt="Profile Photo" width="600"/>

## Parts List
* Raspberry Pi 4 2GB
* Waveshare 4.2" E-Ink Display
* Keyboard
    * Mini Soft Touch Push-button Switches (6mm square) surface mount
    * Small Perfboards
    * Signal diodes
    * 2.54mm pins
    * Supermecro Controller
    * Micro Swiss pins and sockets
* GPIO/Power Controlls
    * Generic 6mm clicky buttons
    * IM232 6-pin Slide Switch
    * 10k ohm (pull up) resistors
* Battery and Power
    * 4 x ~3ah 18650 cells used
    * Retro Psu for charging and 5v
    * Anmbest 5PCS 1S 3.7V 4A 18650 Charger PCB BMS
    * Nickel Strip
    * USB-C breakout
* PLA filament
* Wire
* Polyimide Tape
* #2-28 Thread Size, 1/4" Plastec Screws

## Software
### OS
Using the Server Ubuntu 20.10 build.  This worked out of the box with no customizaton needed aside from network setup and changing the default account name.

### Display
Setting this up in Ubuntu was a bit of a cludge trying to get the needed libraries installed and I didn't document it well.  Will have to capture better notes next time.  Its much more simple to set up on Raspberry PI OS.  However,  Ubuntu seems to better support the variety of terminal sizing used in PaperTTY, so I'm glad to be using it.

Using the fantastec PapirTTY module from here: https://github.com/joukos/PaperTTY

See:
* bin/start.sh 
* service/papertty.service

I added a check in start.sh to look for marker files under /tmp from the gpio service to trigger different font sizes.  And the Block cursor is MUCH easer to follow than the default line.

### GPIO and Power
The GPIO service starts up gpio_buttons.py, which:
* in turn configures five buttons to run specicific commands as root and
    * touch files and restart the PaperTTY service to toggle resolution
    * initiate a shutdown
    * tbd...
* every two minutes checks the voltage from the RetroPSU via I2C and puts it in /tmp/battery_voltage
* if the battery voltage is below 3.2, broadcasts a warning with the 'wall' commad.
The .bashrc sets up PS1 to pull the voltage from the file and puts it on the prompt for reference.

See:
* bin/gpio_buttons.py 
* service/gpio.service
* .bashrc

### Keyboard
The keyboard firmware is built with qmk, with the Miryoku branch checked out and applied to a 3x5_3 layout.

## Construction
### Keyboard
### Battery
### Case

