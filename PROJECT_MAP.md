# Bridge — Project Map

Snapshot: 2026-11-20, branch `master`, 78 commits, clean tree.
Goal (README): automatically play bridge and collect stats on strategies.

## 0. Update: legacy half ported to Python 3 (2026-11-20)

The legacy modules (Bid, Bidding, BeginningBidder, Table, Trick, Round) were ported onto the modern
string-based core; `stats.py` was deleted (the notebook supersedes it). Everything in sections 2-4
below is the *pre-port* analysis, kept for history; the tables in §1 are current.

Decisions taken: fix rules as we go; `Position` everywhere with lower-case seats (`'north'`, and a
`Position` compares equal to its string); string cards in tests; `Bid` strain is a string ordered
clubs < diamonds < hearts < spades < notrump; pytest-style tests; a hand opens at **14+ HCP**.

What changed:
- `Card`/`Suit` `!=` bug fixed; `Suit`, `Value`, `Card`, `Position`, `Bid` are hashable; `Value.rank`.
- `Deck.cut()` never picks a no-op cut.
- `Position` gained `index2pos`, `pos2index`, `side`; `Table.index2pos/pos2index` moved there. `Table.position` became `Table.Seat`.
- `Hand` gained `hcp()`, `longest()`, `strongest()`, `balanced()` (the old `hc`/properties are gone).
- `Bid`: level then strain, `Bid('pass')` needs no suit, total ordering (pass is lowest).
- `Bidding`: a pass after a bid no longer crashes on comparison; the auction ends after **3 passes following a bid** (4 only when nobody opened, which raises `Redeal`); further bids raise `ValueError`.
- `BeginningBidder`: opens at 14+ HCP; strongest-and-longest suit, else strongest suit if 5+ long, else the longest suit (replaces a `NotImplementedError`). Ties go to the higher-ranking suit.
- `Trick`: `getCard`/`north`... index by seat not trick order; `leadSuit`, `currentWinner()` added.
- `Round`: leader is respected (cards were removed and played by trick index before), `play()` plays 13 tricks, `simpleHigh` rewritten on `Hand.get_suit`, handles `notrump`.

Findings.txt (2012) does **not** reproduce, and it should not: the 2012 `Card` compare ignored suit and
`play_trick` always let seat 0 lead. With real trick rules (2000 deals, spades trump, `simpleHigh`,
seeded): rotating leader gives 6.5 / 6.5 tricks per side; north always leading the first trick gives N-S 6.3
vs E-W 6.7, i.e. leading your highest card is slightly a handicap.

### TODO: larger cleanup (not done)
- **`Card.trump` is mutable state on the card** (set by `Trick.nextCard` and stamped by `HandLogic.__init__`). It makes cards unequal in meaning across contexts and `nextCard` mutates the caller's card. Replace with trump passed as context, e.g. `Trick`/`Round` own the comparison (`beats(card, other, lead, trump)`) and `Card.__lt__/__gt__` become plain same-suit value comparisons. Touches `Card`, `Trick`, `Round`, `test_Card`, `test_trick`.
- Inject an `np.random.Generator` into `Deck` instead of global `np.random` state (tests seed with `np.random.seed`).
- `raiseBid` / `jumpBid` are stubs; `Bid` has no double/redouble.
- README/roadmap, `setup.py` classifier, `.gitignore`, a `requirements-notebooks.txt`, CI.
- Port the balanced-hand histogram that `stats.py` produced into the notebook, using `Hand.balanced()`.

## 1. Health at a glance

| Item | State |
|---|---|
| Python | 3.13 (setup.py says `>=3.6`; code uses f-strings, so 3.6+ is right) |
| Deps | numpy, pytest, pytest-cov (requirements.txt). The notebook also needs pandas, scipy, seaborn, matplotlib (undeclared) |
| `pytest` | **119 passed, 0 errors**, also clean under `-W error` |
| Coverage | 99% total; every module 94-100% |

(Before the port: 39 passed, 7 collection errors, 43% coverage; the repo was two halves, a tested modern core and a legacy Python 2 half broken at import. Sections 2-5 describe that state.)

## 2. Module map

### Modern half (works)
| Module | Role | Notes |
|---|---|---|
| `Suit.py` | `Suit` class, valid suits, letter→suit | Bug: `__ne__` uses `~` (see §3) |
| `Value.py` | `Value` class; `'0'` = ten; ordering `2..A` | No `__hash__`; `__eq__` fails vs non-Value |
| `Card.py` | `Card(value, suit, trump=False)`; trump-aware `<`/`>`; `toCode`/`fromCode` | Bug: `__ne__` uses `~`. No `__hash__`. Cross-suit compare returns False for both `<` and `>` |
| `Hand.py` | `Hand(list)` of exactly 13 cards; `get_suit`, `clubs()/hearts()/...`, `highCard`, `lowCard`, `distro` | `balanced` commented out. No `hc`/`strongest`/`longest` (legacy code expects them) |
| `Deck.py` | `Deck(list)` of 52; `shuffle`, `cut`, `deal`, `toCode`/`fromCode` | Uses `np.random` global state; `cut()` randint(1,53) |
| `Position.py` | `Position` (lowercase north/east/south/west), `cycle(dealer)` | Not used by anything else yet |
| `Scorers.py` | `SimpleHighCardValue` (J1 Q2 K3 A4) via deck or hands | Only consumer: notebook |

### Legacy half (broken at import)
| Module | Role | Why broken |
|---|---|---|
| `Bid.py` | `Bid(value, suit)`; `'pass'`; ordering | `from . import suits` — no such name in `__init__.py` (empty). Tests expect `suits` dict mapping suit name → int (`notrump`, `clubs`..). `__gt__/__lt__` logic wrong (bid ordering is rank-then-suit, not either/or) |
| `Bidding.py` | `Bidding(list)` auction mechanics, `Redeal`, `Bidding_logic` ABC | Imports nothing broken itself, but depends on Bid; Capitalised seats ('North') conflict with `Position`'s lowercase; ABC uses py2 `__metaclass__` (does nothing in py3) |
| `BeginningBidder.py` | Opening-bid logic: pass <15 HCP, else bid strongest/longest suit | Needs Bid; needs `Hand.hc`, `.strongest`, `.longest` which don't exist; `Card.Card(14,1)` int style in tests |
| `Table.py` | `position` (seat+score), `Table`, `index2pos`, `pos2index` | `from . import positions` missing. Duplicates `Position.py` |
| `Trick.py` | `Trick(list)`: `nextCard`, `winner`, N/E/S/W accessors | Depends on Table/`positions`; `__str__` returns `'Trick'`; tests use int cards |
| `Round.py` | `HandLogic` ABC, `simpleHigh` player, `Round.play_trick`; `__main__` stats loop | Imports Trick (broken); py2 `st.next()`, `zip(*stats)[0]`; `simpleHigh` uses `hand.highCard` as attribute and `__getattribute__(suit)` |
| `stats.py` | HCP/balanced histograms | `from . import deck` (lowercase, gone); `import matplotlib` not in requirements; `1/0` debugging stops; `normed=` removed in matplotlib; uses `h.balanced`, `h.hc_points` that don't exist. Effectively superseded by the notebook |

### Non-code
| File | Role |
|---|---|
| `README` | Roadmap (no `.md` extension, but `setup.py` declares markdown) |
| `Findings.txt` | 2012 result: simpleHigh averages 6.5 tricks/side rotating deal; 7/6 with fixed dealer |
| `Notebooks/HCP stats.ipynb` | Modern: HCP distribution over 100k deals, normal fit, partner correlation. Works against `Deck` + `Scorers` |
| `setup.py`, `.coveragerc`, `.gitignore`, `License.txt` (BSD-3) | Packaging/config. `.gitignore` lacks `.pytest_cache`, `__pycache__` dirs (has `*.pyc`), `.ipynb_checkpoints`, `venv` |

### Dependency graph
```
Suit   Value
  \     /
   Card ── Hand ── Deck ── Scorers ── (notebook)
                    
Position (isolated)

[legacy]  Bid ──┬─ Bidding ── BeginningBidder
                └─(needs `suits`)
          Table(needs `positions`) ── Trick ── Round
          stats (needs `deck`, matplotlib)
```

## 3. Findings (bugs and inconsistencies)

Confirmed by running:
1. **`!=` is wrong for `Card` and `Suit`.** `~(self == other)` on a bool gives `-1`/`-2`, both truthy. `Card('4','spades') != Card('4','spades')` returns `-2` (True). Existing tests only test the unequal case so they pass. Also emits DeprecationWarning (removed in Python 3.16). Fix: `return not (self == other)`.
2. **`test_Hand.py` fails at collection**: it builds `Card(5, 'spades')` with ints, but `Value` only accepts strings. Fix the test data (`'5'`), not `Value`.
3. **Plain `pytest` collects nothing** because of the 6 legacy import failures, so any regression in the healthy half is invisible.
4. **`test_cut` is not deterministic**: `np.random.default_rng(8675309)` is created and discarded (does nothing). `Deck.cut()` is random, so the `d1[0] != d2[0]` check can fail about 1 time in 52 (`randint(1, 53)` can return 52, a no-op cut).
5. **`test_Scorers`** asserts `[10,10,10,10]` for an unshuffled deck — passes, but only proves the deal is suit-striped.

Reasoned from reading (not run):
6. Two competing position/seat models: `Position` (lowercase, class) vs `Table.position` / strings `'North'` (capitalised) in Bidding/Trick/Round.
7. Two competing card models: legacy tests use `Card(14, 1)` (int rank/suit); the modern `Card` uses strings. Legacy tests encode an older API.
8. `Bid` comparison is incorrect for real bridge (a 2♣ should beat 1♠; `__gt__` returns True if suit is higher even when level is lower).
9. Hand-evaluation concepts the legacy code expects (`hc`, `strongest`, `longest`, `balanced`) were never ported; `Scorers` was the start of that.
10. `Value`/`Card`/`Suit` define `__eq__` without `__hash__` → unhashable, can't go in sets/dicts. `Value.__eq__` raises AttributeError against non-Value.
11. `Bidding_logic` and `HandLogic` use `__metaclass__ = ABCMeta` (Python 2 syntax): abstract methods are not enforced.
12. `Trick.nextCard` mutates the caller's `card.trump`.
13. `setup.py`: `long_description_content_type` says markdown but the README is plain/unnamed; classifier `License :: OSI Approved :: BSD-3-Clause` is not a valid trove classifier (should be `License :: OSI Approved :: BSD License`).
14. Roadmap is stale vs. reality (Position, Scorers, notebook not mentioned).

## 4. Recommendations (in order)

### Phase 0 — Stop the bleeding (small, mechanical, ~1 commit each)
1. Fix `__ne__` in `Card` and `Suit` (`not (self == other)`), and add equal-case `!=` tests. This is a real correctness bug.
2. Fix `test_Hand.py` data to string values; deterministic `test_cut` (use `np.random.seed` or pass `place`; drop the dead `default_rng` line).
3. Quarantine the legacy half so `pytest` runs green on the healthy half. Recommended mechanism: move legacy modules + their tests to `legacy/` (outside the package, e.g. `legacy/Bid.py`, `legacy/tests/`) with a README note. This keeps history/intent but removes import errors. Alternative: `collect_ignore` in a `conftest.py` (cheaper, but leaves the broken files in the package).
4. Add `pytest.ini`/`pyproject` `[tool.pytest]` config, extend `.gitignore` (`.pytest_cache`, `__pycache__`, `.ipynb_checkpoints`, `venv`), add notebook deps to a `requirements-notebooks.txt` (pandas, scipy, seaborn, matplotlib, jupyter).
5. Target state: `pytest` = green, 0 errors, no warnings.

### Phase 1 — Settle the core model (decisions needed, see §5)
6. One seat model: use `Position` everywhere; add `partner`, `next`, `side` (NS/EW) helpers; delete `Table.position` duplication.
7. Add `__hash__` to `Suit`/`Value`/`Card`; make `__eq__` return `NotImplemented` for foreign types; use `functools.total_ordering` or `@dataclass(frozen=True)`.
8. Port hand evaluation onto `Hand`/`Scorers`: HCP, distribution, `balanced`, longest/strongest suit. Replaces legacy `hc/strongest/longest/balanced` and `stats.py`.

### Phase 2 — Rebuild the legacy features on the new core (TDD, one at a time)
9. `Bid` (level 1-7 × strain C<D<H<S<NT, pass/double/redouble) with correct ordering. Rewrite tests; port the existing ones whose intent is still valid.
10. `Bidding` auction mechanics on `Position`; Python-3 ABC for pluggable bidder logic.
11. `Trick` + `Round` + `simpleHigh` player; reproduce the 2012 `Findings.txt` result (≈6.5 tricks/side) as an acceptance test with a seeded RNG.
12. `BeginningBidder` last (depends on 8 and 9).

### Phase 3 — Hygiene
13. Rename `README` → `README.md`, update roadmap, fix setup.py classifier, pin Python version, add a CI workflow (GitHub Actions: pytest on 3.10-3.13).
14. Inject RNG (`np.random.Generator`) into `Deck` instead of global state, so simulations are reproducible.

"Ready to start again" = Phase 0 complete + decisions in §5 made.

## 5. Open questions for Brian
1. Legacy half: **quarantine to `legacy/`**, delete, or leave in place with a `conftest.py` ignore?
2. Seat representation: standardise on `Position` objects (my recommendation), or plain lowercase strings?
3. Bid/auction: do you want full bridge bidding rules (double/redouble, contracts, vulnerability) or stay minimal?
4. Notebook/stats: keep `stats.py` or delete it since the notebook replaced it?
5. Next feature after cleanup: playing a full hand (Trick/Round) or bidding first? (README lists playing first.)
