"""Multiple File, Single Analysis"""

from multiprocessing import Pool
from typing import Callable, Iterable, Optional

from .accumulator import accumulate


def _quiet_wrapper(pool_iter, **kwargs):
    return pool_iter


def _pretty_wrapper(pool_iter, total=None, **kwargs):
    import tdqm
    return tdqm.tdqm(pool_iter, total=total)


def run(
    loader: Callable,
    processor: Callable,
    work_items: Iterable,
    ncores: Optional[int] = None,
    quiet: Optional[bool] = False,
):
    """run a load+process analysis on each of the work items
    over the input number of cores

    Parameters
    ----------
    loader: Callable
        function that loads data from a single work item into
        in-memory data that can be handled by processor
    processor: Callable
        function that processes in-memory data into analysis
        result objects that are accumulatble
    work_items: Iterable
        iterable that contains items to include in the analysis
    ncores: Optional[int]
        number of cores to use, defaults to number of cores of
        the current machine
    quiet: Optional[bool]
        whether to print a progress bar, default False
    """

    def work_function(item):
        return processor(loader(item))

    wrapper = _quiet_wrapper if quiet else _pretty_wrapper

    p = Pool(ncores)
    ana_result = accumulate(wrapper(p.imap_unordered(work_function, work_items, chunksize=1), total=len(work_items)))
    p.close()
    p.join()
    return ana_result
