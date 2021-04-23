# Paper Pi Handheld
This is the Raspberry Pi E-Ink Handheld, an art project with a few goals in mind:
* Implement a reliable battry power and charging system
* Custom thumb Keyboard with the Miryoku layout that I wanted more experience with.  Also an opportunity to hand-wire a Keyboard.
* Put this eink dispiay to use.  It's console centric, and seemed like a good opportunity to get better with console tools.  E.G. becoming proficient with "screen".  And the Keyboard layout caters to emacs, so I might spend some time there instead of vi.
* Further develop my 3D design skills.

<img src="/images/1.jpg" alt="Profile Photo" width="600"/>

<img src="/images/2.jpg" alt="Profile Photo" width="200"/><img src="/images/3.jpg" alt="Profile Photo" width="200"/><img src="/images/4.jpg" alt="Profile Photo" width="200"/><img src="/images/5.jpg" alt="Profile Photo" width="200"/><img src="/images/6.jpg" alt="Profile Photo" width="200"/>

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

See:
* **kb**

General process to build the firmware for this keyboard:
* Install qmk
* cd ~/qmk_firmware
* git remote add manna-harbour git@github.com:manna-harbour/qmk_firmware.git
* git fetch manna-harbour
* git checkout --track manna-harbour/miryoku
* cp **this_repo/kb** ~/qmk_firmware/keyboards/handwired/kb
* And then build and flash the firmware:
    * make handwired/kb:manna-harbour_miryoku:flash
* Or with querty layout:
    * make handwired/kb:manna-harbour_miryoku:flash MIRYOKU_ALPHAS=QWERTY

## Construction
### Keyboard
It's a verry standard 5x3_3 layout, with total 10 columns and 4 rows.  I tested a few button types to find something that felt nice and reluctantiy settled on these surface mount buttons.  

<img src="/images/buttons.jpg" alt="kb" width="300"/>

They worked out much better than I expected.  It turned out to be pretty easy to solder them in between the pins, and the pins were perfect for soldering the diodes and wires to.

<img src="/images/kb0.jpg" alt="kb" width="200"/><img src="/images/kb1.jpg" alt="kb" width="200"/>
<img src="/images/kb2.jpg" alt="kb" width="200"/><img src="/images/kb3.jpg" alt="kb" width="200"/>
<img src="/images/kb4.jpg" alt="kb" width="200"/><img src="/images/kb5.jpg" alt="kb" width="200"/>
<img src="/images/kb6.jpg" alt="kb" width="200"/><img src="/images/kb_usb.jpg" alt="kb" width="200"/>

### Battery
Nothing exciting.  I took 4 cells with similar capacity and internal resistance, paired them with a bms to protect against over-discharge and over-charge.

<img src="/images/ba0.jpg" alt="ba" width="200"/><img src="/images/ba1.jpg" alt="ba" width="200"/>
<img src="/images/ba2.jpg" alt="ba" width="200"/><img src="/images/ba3.jpg" alt="ba" width="200"/>

The batteries with bms are put in parallel and connected to the RetroPSU.  I don't have a good photo of the RetroPSU...  

<img src="/images/charging.jpg" alt="Charging" width="300"/>

### GPIO buttons
The GPIO buttons are wired with a 10k pullup resistor to the 3.3v pin on the pi.  When the button is pushed, the pin is grounded.  I've tried GPIO buttons on a previous project using only the PIs internal pullup, but it seemed succeptable to noise and would trigger when plugging in power or other interference.  So the external pullup is a good idea.  I have another project where I'll probably solder the resistors right to the bottom of the pi rather than on a breakout board.  Should simplify the breakout and keeps the 3.3v at the pi.

<img src="/images/gp0.jpg" alt="gp" width="200"/><img src="/images/gp1.jpg" alt="gp" width="200"/><img src="/images/gp2.jpg" alt="gp" width="200"/>

### Case
The standard design process for stutt like this, afaik, is sketch, extrude, sketch, extrude, repeat.
I really like designing in onshape. The model for this project is visible here:
https://cad.onshape.com/documents/13dcc4cd36db3b0ea3155a7a/w/e8b5185664b2f77b660e3fdd/e/d6a897af7acc9e3dde9fd0a4

I think if you create an (free) account, you can copy it and modify or export it.

<img src="/images/os0.png" alt="os" width="300"/>

The initial sketch is extruded many times to make a shell:

<img src="/images/os1.png" alt="os" width="300"/><img src="/images/os5.png" alt="os" width="300"/>

And then details are added.  Example slot for the RetroPSU and spot to screw in the usbc charge port.  I couldn't use the port built into the PSU because of its orientation and lack of planning for it in this design.

<img src="/images/os2.png" alt="os" width="300"/>

Example of a sketch on a surface and subsequent extrude to add openings for the pi HDMI and audio ports:

<img src="/images/os3.png" alt="os" width="300"/><img src="/images/os4.png" alt="os" width="300"/>


