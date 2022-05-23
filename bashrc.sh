# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# don't put duplicate lines in the history. See bash(1) for more options
# ... or force ignoredups and ignorespace
export HISTCONTROL=ignoreboth:erasedups

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
export HISTSIZE=
export HISTFILESIZE=

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# some more ls aliases
alias ll='ls -larth'
alias l='ls -lrth'
alias la='ls -A'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
    . /etc/bash_completion
fi
shopt -s direxpand

export EDITOR=vim

#Setup Env
source $HOME/sdf/src/LCIO/setup.sh
#scl enable devtoolset-6 bash
source $HOME/sdf/src/root/buildV62202/bin/thisroot.sh
export JAVA_HOME=/sdf/group/hps/users/bravo/src/jdk-15.0.1
export PATH=/sdf/group/hps/users/bravo/.local/bin:/sdf/home/b/bravo/.local/bin:/sdf/group/hps/users/bravo/src/jdk-15.0.1/bin:/sdf/group/hps/users/bravo/src/apache-maven-3.6.3/bin:$PATH
export LD_LIBRARY_PATH=/sdf/group/hps/users/bravo/.local/lib:$LD_LIBRARY_PATH

#Alias to make things easier
alias c='clear'
alias v='vim'
alias r='root -l'
alias mvnclbd='mvn clean install -DskipTests=true -Dcheckstyle.skip'

alias cmakeconf='cmake -DCMAKE_INSTALL_PREFIX=$HOME/local ..'

alias sshlxplus='ssh -XtY -C lxplus.cern.ch'
alias sshsvtdaq='ssh -XtY -C rdsrv117'
alias sshhpsprod='ssh -XtY -C hpsprod@rhel6-64'
alias sshhpsprodcent='ssh -XtY -C hpsprod@centos7'
alias sshrhel='ssh -XtY -C rhel6-64'

source ~/sdf/src/hps-mc/install/bin/hps-mc-env.sh
source ~/sdf/src/hpstr/install/bin/setup.sh

if [ $HOSTNAME == "rdusr219.slac.stanford.edu" ]
then
    echo "You are on rdusr219"
    source /afs/slac.stanford.edu/g/cci/volumes/vol1/sdimages/sdk/V3.3.0/i86-linux-64/tools/envs-sdk.sh
    #source $HOME/src/root/bin/thisroot.sh
fi

if [ $HOSTNAME == "rdsrv117" ]
then
    echo "You are on rdsrv117"
    source /afs/slac.stanford.edu/g/cci/volumes/vol1/sdimages/sdk/V3.3.0/i86-linux-64/tools/envs-sdk.sh
    #source $HOME/src/root/bin/thisroot.sh
fi

if [[ $HOSTNAME == rhel6-64*  ]]
then
    echo "You are on rhel6-64"
    #export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/u/ea/bravo/local/lib
    export PATH=/u/ea/bravo/local/bin:$PATH
    export JAVAVER=1.8
    export JAVA_HOME=/afs/slac/package/java/@sys/jdk1.8
    #source /nfs/slac/g/hps3/software/setup.sh
fi

if [[ $HOSTNAME == cent7*  ]]
then
    echo "You are on centos7"
    #source /nfs/slac/g/hps3/users/bravo/src/root/buildV61204/bin/thisroot.sh
fi

if [[ $HOSTNAME == rdsrv3**  ]]
then
    echo "You are on ${HOSTNAME}"
    source /u1/root/buildV61204/bin/thisroot.sh
    source /u1/hps/src/LCIO/setup.sh
    source /u1/hps/nfs/hps3/users/bravo/sw/hpstr/install/bin/setup.sh
fi

