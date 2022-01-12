#!/bin/sh

export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
## Put your options here - the service unit will run this script, so that
## you don't need to 'daemon-reload' every time you want to change settings.
##
## It's a good idea to allow only root to write to this file: 
##
## sudo chown root:root start.sh; sudo chmod 700 start.sh
##

#VENV="/home/pi/.virtualenvs/papertty/bin/python3"
#${VENV} papertty --driver epd2in13 terminal --autofit

if test -f /tmp/papertty.smol; then
	FONT='--size 8'
elif test -f /tmp/papertty.big; then
	FONT='--size 14 --font /usr/share/fonts/truetype/msttcorefonts/cour.ttf'
else
	FONT='--size 11 --font /usr/share/fonts/truetype/msttcorefonts/cour.ttf'
fi

if test -f /tmp/hdmi.out; then 
    rm /tmp/hdmi.out
else
     papertty --driver EPD4in2 terminal \
            $FONT \
            --autofit \
            --portrait \
            --cursor=block
fi
