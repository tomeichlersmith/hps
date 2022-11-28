"""Hold the two files we are comparing together in one class"""

import uproot
import matplotlib.pyplot as plt
import os
import math
from scipy.stats import norm

class Differ :
    """Differ allowing easy comparison of "similar" files

    The basic requirement of all files passed is that the columns
    of data in the 'LDMX_Events' TTree are named exactly the same.
    This is an easy requirement if the files are generated using
    the same configuration script and/or the same installation of
    ldmx-sw.

    Parameters
    ----------
    grp_name : str
        Name to include in legend title to differentiate
        this group of plots from another
    args : list of 2- or 3- tuples
        Each entry is a tuple (file_path, name, style) where file_path
        specifies the file to open, name is what should appear
        in plot legends, and style (which can be omitted) are style
        options to pass to the drawing of that file's object. This
        is helpful if you want to tweak the colors of a file or have
        files separated by line style rather than color.

    Example
    -------
    Opening a differ is pretty quick and lightweight.
    We do open the files with `uproot` to make sure they exist and have the ROOT format.

        d = Differ('v3.2.0-alpha',('path/to/v12.root','v12'),('path/to/v14.root','v14'))

    Without any output file options, the plotting will show the plot as if
    we are in an interactive notebook.

        d.plot1d('LDMX_Events/EcalSimHits_valid/EcalSimHits_valid.edep_',
                 'Energy Dep [MeV]')
    """

    def __init__(self, grp_name, *args) :
        self.grp_name = grp_name
        self.files = [
                (uproot.open(pack[0]), pack[1], pack[2] if len(pack)>2 else dict()) for pack in args
                ]

    def __plt_hist(ax, uproot_obj, **kwargs) :
        """Plot the input uproot object as a histogram on the input axes

        If the uproot_obj is already a histogram we import its values and use
        them directly. If the uproot_obj is a TBranch, then we pull its values
        into memory and fill the histogram.
        """

        if issubclass(type(uproot_obj), uproot.behaviors.TH1.Histogram) :
            edges = uproot_obj.axis('x').edges()
            dim = len(edges.shape)
            if dim > 1 :
                raise KeyError(f'Attempted to do a 1D plot of a {dim} dimension histogram.')
            return ax.hist((edges[1:]+edges[:-1])/2, bins=edges, weights=uproot_obj.values(), **kwargs)
        else :
            return ax.hist(uproot_obj.array(library='pd').values, **kwargs)
    
    def __calc_mean(values, weights) :
        """Calculate the mean and standard deviation of the input values with the input weights
        
        This is the default method for including the means in the legend labels if no
        callable is provided.
        """
        mean = (weights*values).sum()/(weights.sum())
        stdd = math.sqrt((weights*(values-mean)**2).sum()/(weights.sum()))
        return mean, stdd
        
    def keys(self, *args, **kwargs) :
        """Call keys on the first file provided
        
        Just helpful for exploring, still assumes that all files
        have the same data storage meta-format for accessing
        """
        return self.files[0][0].keys(*args, **kwargs)

    def plot1d(self, column, xlabel, 
               ylabel = None,
                yscale = 'log',
                ylim = (None,None),
                out_dir = None, file_name = None,
                legend_kw = dict(),
                include_mean = None, draw_mean = False,
               **hist_kwargs) :
        fig = plt.figure('differ',figsize=(11,8))
        ax = fig.subplots()
        
        if 'histtype' not in hist_kwargs :
            hist_kwargs['histtype'] = 'step'
        if 'linewidth' not in hist_kwargs :
            hist_kwargs['linewidth'] = 2

        legend_labels = []
        for f, name, style in self.files :
            weights, bins, p = Differ.__plt_hist(ax, f[column], **style, **hist_kwargs)
            if include_mean is not None :
                values = (bins[1:]+bins[:-1])/2
                if callable(include_mean) :
                    mean, stdd = include_mean(values, weights)
                else :
                    mean, stdd = Differ.__calc_mean(values, weights)
                legend_labels.append(f'{name} $\mu = {mean*1000:.1f}\mu m$\n$\sigma = {stdd*1000:.1f}\mu m$')
                if draw_mean :
                    plt.plot(values, norm.pdf(values, mean, stdd), **style, label='_nolegend_')
            else :
                legend_labels.append(name)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_yscale(yscale)
        ax.set_ylim(*ylim)
        if 'title' not in legend_kw :
            legend_kw['title'] = self.grp_name
        ax.legend(labels = legend_labels, **legend_kw)

        if out_dir is None :
            plt.show()
        else :
            fn = column
            if file_name is not None :
                fn = file_name
            full_name = os.path.join(out_dir, fn)
            os.makedirs(os.path.dirname(full_name), exist_ok=True)
            fig.savefig(full_name+'.pdf', bbox_inches='tight')
            fig.clf()
