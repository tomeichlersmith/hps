# pyidm
Tools needed for HPS iDM Analysis

This is a `pip`-installable python package; however, it will never be published to PyPI
because all of its users are expected to be its developers as well.

## Dependencies
Using `pip` to install this package will handle the python packages.
An indirect dependency of this analysis toolchain is a specific method
for tuplization of HPS data. This tuplization method is done on
[my fork of hpstr](https://github.com/tomeichlersmith/hpstr/tree/ptrless).

## Install
Install an "editable" version of this package so
it is both (a) accessible by Python form wherever
and (b) will refer back to your source code so 
you can make changes without having to re-install.
```
python3 -m pip install -e .
```
Usually, this module will also be used with jupyter notebooks
for event inspection and plotting so it is also suggested to
install jupyter lab and plotting tools in the same python venv.
```
pip install jupyterlab matplotlib hist[plot]
```

## Usage
Now that this package is "installed", you can run it from anywhere!
```
pyidm --help
```

## Profiling
I've used [memory-profiler](https://github.com/pythonprofilers/memory_profiler) to profile
the memory which is the most limiting factor of this analysis style.
```
pip install -U memory_profiler
```
Then run by linking the `pyidm` executable with a `.py` extension so `mprof` will run
it as a python script.
```
ln -s $(which pyidm) prof.py
mprof run --multiprocess --python prof.py <args>
mprof plot -o mem-usage-by-child-process.png
mprof run --python prof.py -j 1 <args>
mprof plot -o mem-usage-by-py-function.png
```
