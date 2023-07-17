if [ -d /export/scratch ]; then
  export TMPDIR=/export/scratch
fi

if [ -d $HOME/.local ]; then
  export PATH=$HOME/.local/bin:${PATH}
  export LD_LIBRARY_PATH=$HOME/.local/lib:${LD_LIBRARY_PATH}
  export MANPATH=$HOME/.local/share/man:${MANPATH}
fi

if [ -d $HOME/.cargo ]; then
  export PATH=${PATH}:$HOME/.cargo/bin
fi

if [ -z $HPSMC_DIR ]; then
  . ${HOME}/.local/bin/hps-mc-env.sh
fi

if [ -z $HPSTR_BASE ]; then
  . ${HOME}/.local/bin/hpstr-env.sh
fi

# print collection names in slcio file
print_collections() {
  dumpevent "$1" 1 | grep 'collection name' | cut -f2 -d: | sed -e 's|[[:space:]]||g'
}
