import numpy as np
import pytest

from .. import FastRound
from ..Harness import HarnessError, concatenate, run_batches


# tasks must live at module level so that the worker processes can import them by name
def draw(rng, count):
    return rng.random(count)


def sizes(rng, count):
    return np.full(count, count)


def scaled(rng, count, scale=1.0, offset=0.0):
    return rng.random(count) * scale + offset


def boom(rng, count):
    raise ValueError('boom')


def total(rng, count):
    return rng.integers(0, 100, count).sum()


def rounds(rng, count):
    return FastRound.simulate(rng, count, 'spades')


def test_batches_are_cut_correctly():
    out = run_batches(sizes, 25, batch_size=10, workers=1)
    assert out.tolist() == [10] * 20 + [5] * 5
    assert run_batches(sizes, 20, batch_size=10, workers=1).tolist() == [10] * 20
    assert run_batches(sizes, 3, batch_size=10, workers=1).tolist() == [3] * 3
    assert len(run_batches(sizes, 0, workers=1)) == 0


def test_reproducible_and_seed_dependent():
    a = run_batches(draw, 5000, seed=1, batch_size=1000, workers=1)
    assert np.array_equal(a, run_batches(draw, 5000, seed=1, batch_size=1000, workers=1))
    assert not np.array_equal(a, run_batches(draw, 5000, seed=2, batch_size=1000, workers=1))


def test_batch_size_is_part_of_the_contract():
    """different batches, different streams: same statistics, not the same numbers"""
    a = run_batches(draw, 4000, seed=1, batch_size=1000, workers=1)
    b = run_batches(draw, 4000, seed=1, batch_size=2000, workers=1)
    assert not np.array_equal(a, b)
    assert a.mean() == pytest.approx(0.5, abs=0.03) and b.mean() == pytest.approx(0.5, abs=0.03)
    # but the first batch is the same stream either way
    assert np.array_equal(a[:1000], run_batches(draw, 1000, seed=1, batch_size=1000, workers=1))


def test_seed_sequence_accepted():
    seq = np.random.SeedSequence(7)
    a = run_batches(draw, 2000, seed=seq, batch_size=500, workers=1)
    assert np.array_equal(a, run_batches(draw, 2000, seed=7, batch_size=500, workers=1))


def test_config_reaches_the_task():
    a = run_batches(scaled, 100, seed=3, batch_size=40, workers=1, scale=10.0, offset=5.0)
    assert a.min() >= 5.0 and a.max() < 15.0
    assert np.array_equal(a, run_batches(draw, 100, seed=3, batch_size=40, workers=1) * 10.0 + 5.0)


def test_custom_reducer():
    assert run_batches(total, 3000, seed=5, batch_size=1000, workers=1, reduce=sum) == \
        sum(run_batches(total, 3000, seed=5, batch_size=1000, workers=1, reduce=list))
    assert run_batches(sizes, 25, batch_size=10, workers=1, reduce=lambda r: [len(x) for x in r]) == [10, 10, 5]
    assert concatenate([]).shape == (0,)


def test_bad_arguments():
    with pytest.raises(ValueError):
        run_batches(draw, -1)
    with pytest.raises(ValueError):
        run_batches(draw, 10, batch_size=0)
    with pytest.raises(ValueError):
        run_batches(draw, 10, workers=0)
    with pytest.raises(ValueError):
        run_batches(draw, 10, seed=-1)


def test_failure_names_the_batch_in_process():
    with pytest.raises(HarnessError, match='batch 0 of 3') as info:
        run_batches(boom, 30, batch_size=10, workers=1)
    assert isinstance(info.value.__cause__, ValueError)


def test_workers_do_not_change_the_answer():
    """the point of the harness: real worker processes give exactly the in-process answer"""
    serial = run_batches(draw, 6000, seed=11, batch_size=1000, workers=1)
    assert np.array_equal(serial, run_batches(draw, 6000, seed=11, batch_size=1000, workers=2))
    assert np.array_equal(serial, run_batches(draw, 6000, seed=11, batch_size=1000, workers=3))


def test_default_workers_and_single_batch():
    serial = run_batches(draw, 3000, seed=4, batch_size=1000, workers=1)
    assert np.array_equal(serial, run_batches(draw, 3000, seed=4, batch_size=1000))  # one worker per CPU
    # one batch: nothing to spread, runs in this process whatever `workers` says
    assert np.array_equal(run_batches(draw, 500, seed=4, batch_size=1000, workers=1),
                          run_batches(draw, 500, seed=4, batch_size=1000, workers=4))


def test_failure_names_the_batch_across_processes():
    with pytest.raises(HarnessError, match='batch 0 of 2') as info:
        run_batches(boom, 20, batch_size=10, workers=2)
    assert 'boom' in str(info.value)


def test_rounds_of_bridge_across_processes():
    """the first real customer: rounds of simpleHigh against simpleHigh"""
    serial = run_batches(rounds, 4000, seed=3, batch_size=1000, workers=1)
    assert serial.shape == (4000, 2) and (serial.sum(axis=1) == 13).all()
    assert np.array_equal(serial, run_batches(rounds, 4000, seed=3, batch_size=1000, workers=2))
