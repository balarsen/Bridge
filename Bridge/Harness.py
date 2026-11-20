"""
Run many independent items across processes, with results that do not depend on how many.

    results = run_batches(task, n, seed=0, batch_size=10_000, workers=None, **config)

`task(rng, count, **config)` is a function defined at the top level of a module (so worker processes can
import it by name: no lambdas, no local functions) that processes `count` items using the numpy
`Generator` it is given and returns a small result, an array or a count, never objects like `Deck` or
`Hand`.  The n items are cut into batches of `batch_size` (the last one is shorter), every *batch* gets
its own random stream, a child of `SeedSequence(seed)`, and the batch results are put back in batch
order and combined by `reduce` (by default concatenated).

The contract is that the answer depends only on `(seed, batch_size)`: never on `workers`, on how the
operating system schedules the processes, or on which process ran which batch.  Changing `batch_size`
changes which random numbers each item sees, so it changes the answer (statistically equivalent).

    # Windows (and macOS) start worker processes by importing the main module again, so a script
    # that calls run_batches needs the usual guard:
    if __name__ == "__main__":
        print(run_batches(my_task, 1_000_000, seed=1, batch_size=50_000))

Cost and choosing batch_size (measured on Windows with 6 workers): the pool is started once per call,
which costs about 0.8 s in total, so use workers for runs that take several seconds or more, and
`workers=1` for short ones.  After that, passing a batch is cheap: batches of 2,000 rounds (about 65 ms
of work) ran as fast as batches of 100,000, so choose a size that gives each worker a handful of batches
(for load balancing) and keeps the result arrays small.  Scaling on 6 cores was 4.4x for `FastRound`
and 4.6x for the `Deck`/`Round` objects.

`workers=1`, or a single batch, runs in this process with exactly the same code path and results, which
is also the way to debug a task.  The default is one worker per CPU.  Workers are started with the
"spawn" method on every platform, and each limits numba to one thread so that, say, 6 workers do not
each start 6 numba threads.
"""
import os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

import numpy as np


class HarnessError(RuntimeError):
    """a batch failed; the message gives its number and the original exception is the cause"""


def concatenate(results):
    """the default reducer: join the batch results (arrays) along the first axis"""
    return np.concatenate(results) if results else np.empty(0)


def _init_worker():  # pragma: no cover  (runs only inside the worker processes)
    os.environ['NUMBA_NUM_THREADS'] = '1'


def _run_batch(task, seed_sequence, count, config):
    return task(np.random.default_rng(seed_sequence), count, **config)


def _plan(n, batch_size, seed):
    """the batch sizes and one seed sequence per batch"""
    if n < 0:
        raise ValueError('n must not be negative')
    if batch_size < 1:
        raise ValueError('batch_size must be at least 1')
    sequence = seed if isinstance(seed, np.random.SeedSequence) else np.random.SeedSequence(seed)
    counts = [batch_size] * (n // batch_size)
    if n % batch_size:
        counts.append(n % batch_size)
    return counts, sequence.spawn(len(counts))


def run_batches(task, n, seed=0, batch_size=10_000, workers=None, reduce=concatenate, **config):
    """
    Process n items with `task` in batches, see the module docstring.  Extra keyword arguments are
    passed on to every call of `task`.  `reduce` combines the list of batch results (in batch order).
    """
    if workers is not None and workers < 1:
        raise ValueError('workers must be at least 1')
    counts, seeds = _plan(n, batch_size, seed)
    workers = min(workers or os.cpu_count() or 1, len(counts))

    if workers <= 1:
        results = []
        for i, (child, count) in enumerate(zip(seeds, counts)):
            try:
                results.append(_run_batch(task, child, count, config))
            except Exception as e:
                raise HarnessError(f'batch {i} of {len(counts)} failed: {e!r}') from e
        return reduce(results)

    executor = ProcessPoolExecutor(max_workers=workers, mp_context=get_context('spawn'), initializer=_init_worker)
    try:
        futures = [executor.submit(_run_batch, task, child, count, config) for child, count in zip(seeds, counts)]
        results = []
        for i, future in enumerate(futures):
            try:
                results.append(future.result())
            except Exception as e:
                raise HarnessError(f'batch {i} of {len(counts)} failed: {e!r}') from e
    except BaseException:  # including KeyboardInterrupt: do not leave work running
        executor.shutdown(wait=False, cancel_futures=True)
        raise
    executor.shutdown()
    return reduce(results)
