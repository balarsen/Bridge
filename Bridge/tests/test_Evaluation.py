import numpy as np
import pytest

from .. import DoubleDummy as DD
from .. import Evaluation as E
from ..Bid import Bid
from ..Contract import Contract
from ..Harness import run_batches
from ..Position import Position
from ..Scoring import score

needs_dd = pytest.mark.skipif(not DD.AVAILABLE, reason='the endplay package is not installed (Python 3.12/3.13, dd group)')


def row(**values):
    r = np.full(len(E.COLUMNS), -1, dtype=np.int16)
    for k, v in values.items():
        r[E.COL[k]] = v
    return r


# ---------------------------------------------------------------------------------------------- pure helpers
def test_bid_indices_follow_the_order_of_bids():
    assert E.bid_index(0, 0) == 0 and E.bid_index(1, 0) == 1 and E.bid_index(7, 4) == 35
    indices = [E.bid_index(level, s) for level in range(1, 8) for s in range(5)]
    assert indices == list(range(1, 36))
    bids = [E.bid_of_index(i) for i in range(1, 36)]
    assert bids == sorted(bids) and E.bid_of_index(0) is None
    assert E.bid_of_index(E.bid_index(4, Bid.strains.index('hearts'))) == Bid(4, 'hearts')


@pytest.mark.parametrize('level, strain, expected', [
    (0, 'clubs', 0), (1, 'notrump', 1), (2, 'spades', 1), (3, 'notrump', 2), (3, 'hearts', 1), (4, 'hearts', 2),
    (4, 'clubs', 1), (5, 'clubs', 2), (5, 'diamonds', 2), (6, 'clubs', 3), (6, 'notrump', 3), (7, 'spades', 4),
])
def test_categories(level, strain, expected):
    assert E.category(level, Bid.strains.index(strain)) == expected


def test_the_confusion_matrices_from_made_up_rows():
    hearts = Bid.strains.index('hearts')
    rows = np.array([
        row(level=4, strain=hearts, met_level=4, met_strain=hearts),   # correct
        row(level=4, strain=hearts, met_level=2, met_strain=hearts),   # overbid
        row(level=2, strain=hearts, met_level=4, met_strain=hearts),   # underbid
        row(level=-1, met_level=1, met_strain=0),                      # passed out, a contract makes
        row(level=3, strain=4, met_level=-1),                          # bid 3NT, nothing makes
    ])
    m = E.confusion_matrix(rows)
    assert m.shape == (36, 36) and m.sum() == 5
    assert m[E.bid_index(4, hearts), E.bid_index(4, hearts)] == 1
    assert m[E.bid_index(4, hearts), E.bid_index(2, hearts)] == 1
    assert m[E.bid_index(2, hearts), E.bid_index(4, hearts)] == 1
    assert m[0, 1] == 1 and m[E.bid_index(3, 4), 0] == 1
    assert E.over_under(rows) == {'correct': 1, 'overbid': 2, 'underbid': 2}
    c = E.category_matrix(rows)
    assert c.shape == (5, 5) and c.sum() == 5
    assert c[2, 2] == 1 and c[2, 1] == 1 and c[1, 2] == 1 and c[0, 1] == 1 and c[2, 0] == 1


def test_best_dd_score_from_made_up_tables():
    def table(rows):
        t = np.full((5, 4), 6, dtype=np.int8)
        for strain, tricks in rows.items():
            t[Bid.strains.index(strain)] = tricks
        return t

    assert E.best_dd_score(table({}), 'ns') == 0  # nothing makes
    t = table({'hearts': (10, 3, 9, 3), 'notrump': (9, 4, 9, 4)})
    assert E.best_dd_score(t, 'ns') == 420  # 4 hearts makes exactly: 120 + 300; 3NT makes: 400
    assert E.best_dd_score(t, 'ns', vulnerable=True) == 620
    assert E.best_dd_score(t, 'ew') == 0
    assert E.best_dd_score(table({'spades': (6, 12, 6, 12)}), 'ew') == 980  # 6 spades: 180 + 300 + 500
    # the better declarer counts: north takes 9 tricks (3 spades is a part score: 90 + 50), south 10 (4 spades)
    assert E.best_dd_score(table({'spades': (9, 6, 10, 6)}), 'ns') == 420


# ---------------------------------------------------------------------------------------------- the real thing
@needs_dd
def test_evaluate_rows_are_consistent():
    rows = E.evaluate(np.random.default_rng(4), 100)
    assert rows.shape == (100, len(E.COLUMNS)) and rows.dtype == np.int16
    passed = rows[:, E.COL['passed_out']] == 1
    assert 0 < passed.sum() < 30
    for r in rows:
        if r[E.COL['passed_out']] == 1:
            assert r[E.COL['level']] == -1 and r[E.COL['tricks_simple']] == -1 and r[E.COL['side']] == -1
            continue
        contract = Contract(int(r[E.COL['level']]), Bid.strains[r[E.COL['strain']]], Position.positions[r[E.COL['declarer']]])
        assert r[E.COL['side']] == (0 if contract.side == 'ns' else 1)
        for name in ('dd_tricks', 'tricks_simple', 'tricks_counting'):
            assert 0 <= r[E.COL[name]] <= 13
        assert r[E.COL['score_simple']] == score(contract, int(r[E.COL['tricks_simple']]))
        assert r[E.COL['score_counting']] == score(contract, int(r[E.COL['tricks_counting']]))
        assert r[E.COL['score_dd']] == score(contract, int(r[E.COL['dd_tricks']]))
        assert r[E.COL['best_score']] >= max(r[E.COL['score_dd']], 0)  # the best contract is at least as good
        assert 0 <= r[E.COL['ns_hcp']] <= 40
    made = rows[~passed]
    # double-dummy assumes perfect defence; the simple defenders concede tricks, so declarer can beat it, but
    # on average the played tricks stay close to what the cards allow
    gap = made[:, E.COL['tricks_simple']].astype(float) - made[:, E.COL['dd_tricks']]
    assert abs(gap.mean()) < 2 and gap.min() >= -13
    m = E.confusion_matrix(rows)
    assert m.sum() == 100
    assert sum(E.over_under(rows).values()) == 100


@needs_dd
def test_evaluate_is_reproducible_and_does_not_depend_on_workers():
    a = run_batches(E.evaluate, 48, seed=9, batch_size=12, workers=1)
    b = run_batches(E.evaluate, 48, seed=9, batch_size=12, workers=2)
    assert a.shape == (48, len(E.COLUMNS))
    assert np.array_equal(a, b)
    assert not np.array_equal(a, run_batches(E.evaluate, 48, seed=10, batch_size=12, workers=1))


@needs_dd
def test_precomputed_tables_give_the_same_rows():
    deals = E.deal_many(np.random.default_rng(8), 24)
    assert len(deals) == 24 and all(len(h) == 4 for h in deals)
    tables = DD.dd_tables(deals)
    assert np.array_equal(E.evaluate(np.random.default_rng(8), 24, tables=tables),
                          E.evaluate(np.random.default_rng(8), 24))
    other = E.evaluate(np.random.default_rng(8), 24, open_hcp=15, tables=tables)  # same deals, another rule
    assert not np.array_equal(other[:, E.COL['level']], E.evaluate(np.random.default_rng(8), 24, tables=tables)[:, E.COL['level']])
    with pytest.raises(ValueError):
        E.evaluate(np.random.default_rng(8), 24, tables=tables[:5])


@needs_dd
def test_open_threshold_changes_how_often_nobody_opens():
    rng = lambda: np.random.default_rng(5)
    loose = E.evaluate(rng(), 60, open_hcp=11)
    tight = E.evaluate(rng(), 60, open_hcp=15)
    assert tight[:, E.COL['passed_out']].sum() > loose[:, E.COL['passed_out']].sum()


@needs_dd
def test_vulnerability_changes_scores_not_tricks():
    plain = E.evaluate(np.random.default_rng(6), 40)
    vul = E.evaluate(np.random.default_rng(6), 40, vulnerable=True)
    assert np.array_equal(plain[:, E.COL['tricks_simple']], vul[:, E.COL['tricks_simple']])
    assert not np.array_equal(plain[:, E.COL['score_simple']], vul[:, E.COL['score_simple']])
