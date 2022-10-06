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

    f = hpstrHistFile(arg.hist_file,'tpt',['pre_fiducial_cut',
                   'pos_tag','pos_tag_E','pos_tag_E_time',
                   'el0_tag','el0_tag_E','el0_tag_E_time',
                   'el1_tag','el1_tag_E','el1_tag_E_time'
                  ])

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

    f.plot_1d('cluster_energy','Cluster Energy [GeV]', 
              ylabel='Clusters', title='All Clusters',
              out_dir = arg.out_dir)
    
    f.plot_1d('cluster_x','X [mm]',title='Clusters Passing Energy Cuts',
              out_dir = arg.out_dir)
    
    f.plot_bar('event_selection_cutflow', 'Events after Cut', 
        ['no cuts', '$N_{e^+} >= 1$', '$N_{e^{-}} >= 2$', 
          '$N_{e^+} <= 1$', '$N_{e^-} <= 2$', 'Fiducial',
          'noop','noop','noop'],
        title = 'TPT Event Cut Flow',
        ticks_rotation = 25,
        out_dir = arg.out_dir)

    cluster_vars = [
        ('cluster_E_sum','Cluster E Sum [GeV]'),
        ('max_time_diff', 'Max Time Diff [ns]'),
        ('electron0_cluster_E','High Energy e- Cluster [GeV]'),
        ('electron1_cluster_E','Low Energy e- Cluster [GeV]'),
        ('positron_cluster_E','e+ Cluster [GeV]'),
        ('electron0_track_N', 'High Energy Electron Track Match'),
        ('electron1_track_N', 'Low Energy Electron Track Match'),
        ('positron_track_N', 'Positron Track Match'),
        ]
    for hist_name, xlabel in cluster_vars :
        for p in ['pos','el0','el1'] :
            f.plot_1d(hist_name, xlabel, 
                      selections = lambda copies : [c for c in copies if p in c], 
                      file_name = f'{p}_{hist_name}', out_dir = arg.out_dir)

if __name__ == '__main__' :
    main()

