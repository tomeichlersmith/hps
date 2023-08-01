# pyidm
Tools needed for HPS iDM Analysis

This is a `pip`-installable python package; however, it will never be published to PyPI
because all of its users are expected to be its developers as well.

## Dependencies
Using `pip` to install this package whereever you wish will handle the python packages.

## Install
Install an "editable" version of this package so
it is both (a) accessible by Python form wherever
and (b) will refer back to your source code so 
you can make changes without having to re-install.
```
python3 -m pip install -e .
```

## Usage
Now that this package is "installed", you can run it from anywhere!
In general, I have separated the package into two components following
the `coffea` naming trend.
1. *roast*: this submodule is the first step and contains helper functions
  for loading tuplized HPS data into memory in its awkward form. This is
  helpful to use directly in a jupyter notebook to inspect the events in
  more detail and is used by the second component.
2. *brew*: this submodule contains a coffea processor that can be used
  to make selections and fill analysis histograms. It uses _roast_ to reformat
  the `awkward` data in memory into its more helpful form.
