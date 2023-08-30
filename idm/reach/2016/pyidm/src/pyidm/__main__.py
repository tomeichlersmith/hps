import pickle
from itertools import chain, islice
from pathlib import Path

from . import histogram
from . import mfsa

def listdata(filelimit=None, include_bkgd=False):
    signal_data = [
        Path('/local/cms/user/eichl008/hps/idm/umn-signal/merged-with-Vc'),
        Path('/local/cms/user/eichl008/hps/idm/umn-signal-dense/merged-with-Vc'),
    ]
    bkgd_data = [
        Path('/local/cms/user/eichl008/hps/idm/bkgd/wab/tuples'),
        Path('/local/cms/user/eichl008/hps/idm/bkgd/tritrig/tuples')
    ]

    data = signal_data
    if include_bkgd:
        data += bkgd_data
    
    dir_to_files = lambda fp: fp.iterdir()
    if filelimit is not None:
        dir_to_files = lambda fp: islice(fp.iterdir(), filelimit)

    return [f for f in chain(*list(map(dir_to_files, data))) if f.suffix == '.root' and not f.stem.startswith('sim_')]


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--file-limit',type=int,default=None,help='Maximum number of files from each sample directory')
    parser.add_argument('output',type=Path,help='output file to write pickle of results to')
    
    args = parser.parse_args()

    out = mfsa.run(
        histogram.process,
        listdata(filelimit=args.file_limit, include_bkgd=False),
        preprocess=histogram.load,
        postprocess=histogram.groupby_signal_params
    )

    with open(args.output, 'wb') as outf:
        pickle.dump(out, outf)


if __name__ == '__main__':
    main()
