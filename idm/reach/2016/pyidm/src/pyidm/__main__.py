import pickle
from itertools import chain, islice
from pathlib import Path

from .load import load
from . import signal, vtx
from . import mfsa


def listdata(filelimit=None, include_bkgd=False):
    signal_data = [
        Path('/local/cms/user/eichl008/hps/idm/umn-signal/merged-with-Vc'),
        Path('/local/cms/user/eichl008/hps/idm/umn-signal-dense/merged-with-Vc'),
    ]
    bkgd_data = [
        Path('/local/cms/user/eichl008/hps/idm/bkgd/wab/tuples-with-Vc'),
#        Path('/local/cms/user/eichl008/hps/idm/bkgd/tritrig/tuples')
    ]

    data = signal_data
    if include_bkgd:
        data += bkgd_data
    
    dir_to_files = lambda fp: fp.iterdir()
    if filelimit is not None:
        dir_to_files = lambda fp: islice(fp.iterdir(), filelimit)

    return [f for f in chain(*list(map(dir_to_files, data))) if f.suffix == '.root' and not f.stem.startswith('sim_')]


try:
    if profile:
        #able to call profile function so we are all good
        pass
except NameError:
    # no profile decorator, define a identity wrapper
    def profile(f):
        return f


@profile
def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-j','--n-cores',type=int,default=None,help='Number of cores to use for processing')
    parser.add_argument('--file-limit',type=int,default=None,help='Maximum number of files from each sample directory')
    parser.add_argument('ana',type=str,choices=['signal','vtx'],help='analysis to run')
    parser.add_argument('output',type=Path,help='output file to write pickle of results to')
    
    args = parser.parse_args()


    proc, post = None, None
    if args.ana == 'signal':
        proc = signal.process
        post = signal.groupby_signal_params
    elif args.ana == 'vtx':
        proc = vtx.process

    out = mfsa.run(
        proc,
        listdata(filelimit=args.file_limit, include_bkgd=(args.ana=='vtx')),
        preprocess=load,
        postprocess=post,
        ncores = args.n_cores
    )

    with open(args.output, 'wb') as outf:
        pickle.dump(out, outf)


if __name__ == '__main__':
    main()
