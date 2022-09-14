import matplotlib.pyplot as plt
import mplhep
plt.style.use(mplhep.style.ROOT)

from uphpstr import hpstrHistFile

def main() :
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('hist_file', help='ROOT file containing histograms to plot')
    parser.add_argument('--out-dir', help='Directory to put plots (default: CWD)', default=os.getcwd())

    arg = parser.parse_args()

    f = hpstrHistFile(arg.hist_file,'tpt',
        ['pre_fiducial_cut','pre_min_esum_cut','pos_tag','el0_tag','el1_tag'])

    f.plot_bar('cluster_selection_cutflow', 'Clusters after Cut', 
        title = 'TPT Cluster Cut Flow',
        out_dir = arg.out_dir)

    f.plot_1d({'electrons' : 'n_electron_candidates',
               'positrons' : 'n_positron_candidates'},
               'N Candidates', title = 'Only after cluster cuts, no event cuts',
               out_dir = arg.out_dir)

    f.plot_bar('event_selection_cutflow', 'Events after Cut', 
        title = 'TPT Event Cut Flow',
        out_dir = arg.out_dir)

    cluster_vars = [
        ('cluster_E_sum','Cluster E Sum [GeV]'),
        ('electron0_cluster_E','High Energy e- Cluster [GeV]'),
        ('electron1_cluster_E','Low Energy e- Cluster [GeV]'),
        ('positron_cluster_E','e+ Cluster [GeV]'),
        ]
    for hist_name, xlabel in cluster_vars :
        f.plot_1d(hist_name, xlabel, selections  = True, out_dir = arg.out_dir)

if __name__ == '__main__' :
    main()
