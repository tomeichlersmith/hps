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
        ['no cuts', '$E_{cluster}/E_{beam} < 0.87$', '$E_{cluster} > 0.1$ GeV', 
          '$e^-$ (x < 0mm)', '$e^+$ (x > 100mm)'],
        title = 'TPT Cluster Cut Flow',
        out_dir = arg.out_dir)

    f.plot_1d({'electrons' : 'n_electron_candidates',
               'positrons' : 'n_positron_candidates'},
               'N Candidates', title = 'Only after cluster cuts, no event cuts',
               file_name = 'n_cluster_candidates',
               out_dir = arg.out_dir)

    f.plot_bar('event_selection_cutflow', 'Events after Cut', 
        ['no cuts', '$N_{e^+} >= 1$', '$N_{e^{-}} >= 2$', 
          '$N_{e^+} <= 1$', '$N_{e^-} <= 2$', 'Fiducial',
          '$E_{tot} > 2.2$ GeV'],
        title = 'TPT Event Cut Flow',
        ticks_rotation = 25,
        out_dir = arg.out_dir)

    cluster_vars = [
        ('cluster_E_sum','Cluster E Sum [GeV]'),
        ('electron0_cluster_E','High Energy e- Cluster [GeV]'),
        ('electron1_cluster_E','Low Energy e- Cluster [GeV]'),
        ('positron_cluster_E','e+ Cluster [GeV]'),
        ]
    for hist_name, xlabel in cluster_vars :
        f.plot_1d(hist_name, xlabel, selections  = True, out_dir = arg.out_dir)

    particle = [
        ('electron0', 'high E electron'),
        ('electron1', 'low E electron'),
        ('positron','positron')
        ]
    for part, title in particle :
        f.plot_1d(f'{part}_track_N','Track Match Found',
            title = title,
            selections = True,
            out_dir = arg.out_dir)

    track_vars = [
        ('d0','$d_0$ [mm]'),
        ('Z0','$z_0$ [mm]'),
        ('TanLambda','$\tan(\lambda)$'),
        ('chi2','$\chi^2$'),
        ('Omega','\Omega'),
        ('Phi','\phi')
        ]
    for name, title in track_vars :
        f.plot_1d({p : f'{p}_{name}_h' for p in ['positron','electron0','electron1']},
                  f'Track {title}', title = 'Track Found, Cluster Fiducial, Min Cluster E Sum',
                  out_dir = arg.out_dir, file_name = f'track_found_{name}')

if __name__ == '__main__' :
    main()

