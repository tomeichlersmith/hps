"""Multiple File, Single Analysis"""

from multiprocessing import Pool
from typing import Callable, Iterable, Optional

from .accumulator import accumulate


def _quiet_wrapper(pool_iter, **kwargs):
    return pool_iter


def _pretty_wrapper(pool_iter, total=None, **kwargs):
    from tqdm.autonotebook import tqdm
    return tqdm(pool_iter, total=total)


def run(
    processor: Callable,
    work_items: Iterable,
    *,
    preprocess: Optional[Callable] = None,
    postprocess: Optional[Callable] = None,
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
    preprocess: Optional[Callable]
        function that is called *on each work item* and whose
        return value is passed into process. This can be used to
        prepatory tasks that are shared across many analyses like
        loading the data from disk into memory.
    postprocess: Optional[Callable]
        function that is called on the resulting accumulated analysis
        result before returning it from this function. This can be
        helpful for doing common post-analysis tasks like unpacking
        accumulator objects into their wrapped values. It should
        operate on the passed object *in place* since its return value
        is ignored.
    ncores: Optional[int]
        number of cores to use, defaults to number of cores of
        the current machine
    quiet: Optional[bool]
        whether to print a progress bar, default False
    """

    work_function = processor
    if preprocess is not None:
        work_function = lambda item: processor(preprocess(item))

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
    
    if postprocess is not None:
        postprocess(ana_result)
    
    return ana_result
