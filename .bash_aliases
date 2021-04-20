alias a='alias'


a cs='cowsay'
alias al='vi /home/ubuntu/.bash_aliases'
alias nb='newsboat'
alias ssu='sudo su'
alias q='quit'

# enable color support of ls and also add handy aliases
#alias ls='ls --color=auto'
#alias dir='dir --color=auto'
#alias vdir='vdir --color=auto'
#alias grep='grep --color=auto'
#alias fgrep='fgrep --color=auto'
#alias egrep='egrep --color=auto'

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias v='sudo /home/ubuntu/bin/get_battery_voltage.py'

# Add an "alert" alias for long running commands.  Use like so:
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
