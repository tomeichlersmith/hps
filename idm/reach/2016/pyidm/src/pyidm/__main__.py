import pickle
from itertools import chain, islice
from pathlib import Path

from . import histogram
from . import mfsa


def main():
    out = mfsa.run(
        histogram.process,
        [
            f
            for f in chain(
                islice(Path('/local/cms/user/eichl008/hps/idm/umn-signal/merged').iterdir(), 1),
                islice(
                    Path('/local/cms/user/eichl008/hps/idm/umn-signal-dense/merged').iterdir(),
                    1
                ),
                islice(
                    Path('/local/cms/user/eichl008/hps/idm/bkgd/wab/tuples').iterdir(),
                    1
                ),
                islice(
                    Path('/local/cms/user/eichl008/hps/idm/bkgd/tritrig/tuples').iterdir(),
                    1
                )
            )
            if f.suffix == '.root' and not f.stem.startswith('sim_')
        ],
        preprocess=histogram.load,
        postprocess=histogram.groupby_signal_params
    )

    with open('results.pkl', 'wb') as outf:
        pickle.dump(out, outf)


if __name__ == '__main__':
    main()
