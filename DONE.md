# Bridge — Done

Completed work, newest first. The live map and open items are in [PROJECT_MAP.md](PROJECT_MAP.md).

## 2026-11-20 — cleanup pass (the six cleanup items from the map; not yet committed)

139 -> **143 tests**, **100% statement and branch coverage** of `Bridge/` (tests excluded from the measure), HTML report in `htmlcov/` (git-ignored).

1. **`Card.trump` removed.** A card is now only a suit and a value. Which card wins is decided by `Trick.beats(card, other, trump)`, a pure function: same suit compares by value, otherwise only a trump wins. `Trick.nextCard` no longer mutates the card it is given, `HandLogic` no longer stamps the cards in a hand, `Trick.wouldWin(card)` was added and `simpleHigh.follow` uses it. `Card(..., trump=...)` is now a `TypeError`. `Card` `<`/`>` are same-suit only (still not a total order, still an open design question).
2. **`Deck` takes an RNG.** `Deck(indeck=None, shuffle=None, rng=None)`: `None` uses one shared `np.random.default_rng()`, an int seed or a `Generator` makes runs reproducible (`Deck.fromCode(code, rng=...)` too). `cut()` uses the same generator. Tests no longer touch the global `np.random` state; `test_round.py` passes a seeded `Generator` through every deal.
3. **`Findings.txt`** keeps the 2012 text and has a dated addendum: result 1 reproduces, result 2 does not. Re-run on 20000 deals per experiment (standard error about 0.014 tricks): rotating leader 6.50 / 6.50; north always leading 6.31 N-S vs 6.69 E-W.
4. **CI:** `.github/workflows/ci.yml` runs pytest with coverage on Python 3.12, 3.13 and 3.14 using uv, installing only the `dev` group (no notebook stack). The `UV_PYTHON` job variable overrides the `.python-version` pin. The exact commands were run locally in a separate dev-only environment on Python 3.12 (143 pass); the workflow itself has not run on GitHub yet.
5. **Notebook:** new "Balanced hands" section (what `stats.py` used to plot) using `Hand.balanced()`: fraction of balanced hands and north/south partner crosstab. The whole notebook was executed headlessly against the new packages (59 s, no errors); 20000 deals gave 47.7% balanced, matching the known 47.6%. `nbstripout` is in the `notebooks` group and the README documents the one-time, opt-in `--install --keep-output --extra-keys` command (not run, since it edits `.git/config`).
6. **Coverage gaps closed:** tests for `Card` built from `Suit`/`Value`, `Deck` shuffle on creation, `Trick.__str__`, `Bid` comparison with other types, `Scorers` with hands and no deck, and abstract-method bodies replaced by docstrings. `.coveragerc` now sets `source = Bridge`, `branch = True`, and omits the tests so the number is not inflated by test code.

## 2026-11-20 — packaging moved to uv and Python 3.14 (`5271b77`)

- `pyproject.toml` (hatchling) replaces `setup.py` and `requirements.txt`; `uv.lock` committed; `.python-version` is 3.14; `requires-python >=3.12`.
- Dependency groups: `dev` (pytest, pytest-cov) and `notebooks` (notebook, pandas, scipy, seaborn, matplotlib). Both install by default with `uv sync`.
- pytest config lives in `pyproject.toml` (`testpaths = ["Bridge"]`, `filterwarnings = ["error"]`, so any warning fails the suite).
- Locked versions at the time: numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, seaborn 0.13.2, matplotlib 3.11.2, pytest 9.2.0, pytest-cov 7.1.0, notebook 7.6.5.
- `README` renamed to `README.md` and rewritten (uv setup, current roadmap). `.gitignore` now covers venv, caches, checkpoints, build output.
- License field is now the SPDX `BSD-3-Clause` (the old classifier was not a valid trove classifier).

## 2026-11-20 — legacy half ported to Python 3 (`a6d9939`)

Before: 39 tests passed, 7 modules failed at collection, so plain `pytest` ran nothing; 43% coverage.
After: **119 tests pass**, clean under `-W error`, 99% coverage.

The repo had been two halves: a tested modern core (string-valued `Suit`/`Value`/`Card`/`Hand`/`Deck`/`Position`/`Scorers`) and a 2012 half (`Bid`, `Bidding`, `BeginningBidder`, `Table`, `Trick`, `Round`, `stats`) that was never ported. The legacy half was mostly not Python 2 *syntax* (commit `6b0b275` had done that); it was written against an API that no longer existed (package-level `suits`/`positions` dicts, int-valued cards, `Hand` properties like `hc`). The old `__init__.py` and `Hand.py` were recovered from history (`7ef9e31^`, `18a4843^`) to confirm that.

### Decisions taken
1. Fix rules as we go (not behavior-preserving ports).
2. `Position` everywhere, lower-case seats; a `Position` compares equal to its string.
3. Legacy tests rewritten with string cards; no int-card compatibility.
4. `Bid` strain is a string, ordered clubs < diamonds < hearts < spades < notrump.
5. Keep the mutable `Card.trump` flag for now (cleanup is a TODO in the map).
6. `stats.py` deleted; the notebook supersedes it.
7. Tests are pytest-style.
8. A hand opens at **14+ HCP**.

### What changed
- **Core bugs fixed:** `!=` on `Card`/`Suit` returned `-2` (truthy) for equal objects; `Value`/`Suit`/`Card`/`Position`/`Bid` now hashable; `Value.__eq__` returns `NotImplemented` for foreign types; `Value.rank` added; `Deck.cut()` could pick a no-op cut (flaky test).
- **Position:** `index2pos`, `pos2index`, `side`; `cycle` no longer needs numpy; accepts a `Position` or string. `Table.index2pos/pos2index` moved here, `Table.position` became `Table.Seat`, and `Table` no longer subclasses `list`.
- **Hand:** `hcp()`, `longest()`, `strongest()`, `balanced()` (the old properties `hc`, `strongest`, `longest` were buggy and are not recovered). Hand error message typo fixed.
- **Bid:** ordering by (level, strain) with `functools.total_ordering`; `Bid('pass')` needs no suit (a suit passed to a pass is ignored); pass orders lowest; `isPass`; prints as `1 hearts` / `pass`. (The old ordering compared suit *names* alphabetically and the tests passed by accident.)
- **Bidding:** a pass after a bid no longer raises (`'pass' > 2` is a `TypeError` in py3); the auction ends after **3 passes following a bid** (the old code used 4), or 4 passes with no bid (`Redeal`); bidding after the end raises `ValueError`; seats validated through `Position`; `complete` property; ABC base class actually enforced.
- **BeginningBidder:** 14+ HCP opens; strongest suit if also longest; else strongest suit if 5+ long; else the longest suit (replaces a `NotImplementedError`); ties go to the higher-ranking suit.
- **Trick:** `getCard`/`north`/... index by seat (they used trick order); `leadSuit`, `currentWinner()`; printable when seats are empty.
- **Round:** the leader is honoured (the old code always let seat 0 play first and removed cards by trick index); `Round.play()`, `tricks` and `winners` recorded; `simpleHigh` rewritten on `Hand.get_suit`, compares against the current trick winner, handles `notrump`.
- **Removed:** `Bridge/stats.py`.
- **Tests:** all six legacy test files rewritten in pytest style with explicit fixed hands (the old `random.seed` deals could not be reproduced under `np.random`); tests added for the new behavior and for equal-object `!=`; `test_Hand` fixed (it passed ints to `Value`); `test_cut` made deterministic.

### Findings
- **Findings.txt (2012) does not reproduce, and should not.** The 2012 `Card` comparison ignored suit (only trump mattered) and `play_trick` always let seat 0 lead, so its "7 vs 6 for the leader" came from a game that did not follow suit properly.
- With real trick rules (2000 deals, spades trump, `simpleHigh`, seeded): rotating leader gives 6.5 / 6.5 tricks per side; north always leading the first trick gives N-S 6.3 vs E-W 6.7, i.e. leading your highest card is slightly a handicap (aces get ruffed). Both are locked in by `test_stats` and `test_fixed_leader_is_not_an_advantage` in `test_round.py`.

### Other
- The Jupyter server was run from a scratch venv and the HCP notebook opened in Firefox; the notebook itself is unchanged (a Jupyter metadata bump to the kernel version was discarded).

## 2026-11-20 — first pass: study and map

- Read the whole repo, ran the tests, wrote the first `PROJECT_MAP.md` (module map, dependency graph, bug list, recommendations).
- Baseline before any change (`258d795`): 39 passed, 7 collection errors, 43% coverage.
