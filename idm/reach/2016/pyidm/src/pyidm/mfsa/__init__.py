"""Multiple File, Single Analysis"""

from multiprocessing import Pool
from typing import Callable, Iterable, Optional

from .accumulator import accumulate


def _quiet_wrapper(pool_iter, **kwargs):
    return pool_iter


def _pretty_wrapper(pool_iter, total=None, **kwargs):
    import tqdm
    return tqdm.tqdm(pool_iter, total=total)


def run(
    processor: Callable,
    work_items: Iterable,
    *,
    loader: Optional[Callable] = None,
    ncores: Optional[int] = None,
    quiet: Optional[bool] = False,
):
    """run an analysis on each of the work items
    over the input number of cores

    Parameters
    ----------
    processor: Callable
        function that processes in-memory data into analysis
        result objects that are accumulatble
    work_items: Iterable
        iterable that contains items to include in the analysis
    loader: Optional[Callable]
        function that loads data from a single work item into
        in-memory data that can be handled by processor
        default is no loading function, expecting the work items
        to be prepared as the processor expects
    ncores: Optional[int]
        number of cores to use, defaults to number of cores of
        the current machine
    quiet: Optional[bool]
        whether to print a progress bar, default False
    """

    work_function = processor
    if loader is not None:
        work_function = lambda item: processor(loader(item))

    wrapper = _quiet_wrapper if quiet else _pretty_wrapper

    with Pool(ncores) as p:
        ana_result = accumulate(
            wrapper(
                p.map(
                    work_function, work_items, 
                    chunksize=1
                ), 
                total=len(work_items)
            )
        )
    return ana_result
