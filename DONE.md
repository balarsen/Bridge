# Bridge — Done

Completed work, newest first. The live map and open items are in [PROJECT_MAP.md](PROJECT_MAP.md).

## 2026-11-20 — map cleaned: finished plans and settled decisions moved here

From now on every finished item moves from PROJECT_MAP.md to this file (see the rule at the top of the map). What moved in this first pass:

- **The multiprocessing harness plan** (built as `Bridge/Harness.py`, entry below). Design notes that were in the plan: `task(rng, count, **config)` is a top-level function (picklable by reference) returning a small result (arrays or counts, never `Deck`/`Hand` objects); the default reducer concatenates; a pool is created per call with the `spawn` context and `workers=1` is the in-process path; each worker sets `NUMBA_NUM_THREADS=1`; tasks and strategy classes must be importable at module level (no lambdas or local classes); `joblib`'s loky backend (installed through PyMC) handles closures and stays a notebook tool while the library uses the standard library. The planned steps (in-process batching, the pool path with a real multi-process test, a scaling benchmark, a million-round first customer) were all done.
- **"Integer-array play engine" decision**: done in the pure-Python form as `Bridge/FastRound.py`; the compiled and search-oriented engine (bitboards, DDS) is part of PLAN_PLAYING.md.
- **Decision: `Card` stays as it is** (same-suit comparison only, not a total order): the easiest thing, and trump lives in `Trick.beats`. If a sorted display of a hand is wanted, add a sort-key helper (suit order, then value) rather than changing `Card` comparison.
- **Decision: we go hand by hand for now** (deal, bid, play one hand); whole games and full scoring wait.
- Seed plumbing for parallel runs (one `SeedSequence` child per batch) is in the harness; what remains of the RNG TODO is in the map.

## 2026-11-20 — integer round engine and the multiprocessing harness

195 tests, 100% statement and branch coverage.

- **`Bridge/FastRound.py`**: the fully inlined integer version of a round, as measured on a prototype first. Cards are `suit * 13 + rank` integers, hands are per-suit sorted lists, the trick winner is tracked incrementally; it plays `simpleHigh` at all four seats. Tested against `Round` + `simpleHigh` on 800 combinations of deck, trump (all four suits and notrump) and leader: identical tricks every time. 30,700 rounds/s against 2,110 for the objects (14.5x). The prototype also showed that an API-shaped restructuring of the object classes (pluggable strategies, hand object, trick records) would get 7.8x, which stays a TODO.
- **`Bridge/Harness.py`**: `run_batches(task, n, seed, batch_size, workers, reduce, **config)`. The n items are cut into fixed-size batches, each batch gets one child of `SeedSequence(seed)`, results are put back in batch order, so **the answer depends only on `(seed, batch_size)`, never on the number of workers** (tested with real worker processes at 1, 2 and 3 workers). `workers=1`, or a single batch, runs the same code in-process. Workers use the `spawn` method everywhere and limit numba to one thread. Failures are re-raised as `HarnessError` naming the batch.
- **Measured (6 cores, Windows):** `FastRound` 30,700 rounds/s on one worker, 136,000 on six (4.4x); the `Deck`/`Round` objects 2,110 to 9,700 (4.6x); a million rounds of `simpleHigh` against `simpleHigh` with a rotating leader in 7.6 s (mean 6.500 / 6.500 tricks per side). Results identical at every worker count. The pool costs about 0.8 s per call, and 2,000-round batches ran as fast as 100,000-round ones (my first guess, "batches of about 2 s", was too cautious).
- **`PLAN_PLAYING.md`** rewritten with Brian's decisions (correct = highest bid met, confusion matrix of over/under bids, repeated play as weights, declarer sees own hand and dummy with perfect defenders, prove DDS then use it, uniform among equivalent cards, likelihood model for the auction, start with the exact suit-combination solver).

## 2026-11-20 — exact probabilities, fast simulation and the statistics notebook

167 tests, **100% statement and branch coverage**. Pushed; CI (3.12 / 3.13 / 3.14) was green on the first GitHub run.

- **`Bridge/Probability.py`** (numpy only): exact HCP distribution for any number of cards (dynamic program) and an independent closed form (`hcp_pmf_multivariate_hypergeometric`: the 625-term weighted sum of multivariate-hypergeometric probabilities), the honor count (exactly hypergeometric), all 39 hand patterns, suit-length, partner-length, combined-length, partner-aces and opponent-split distributions. Cross-checked against `scipy.stats.hypergeom`, brute-force enumeration of all pairs and triples of cards, and textbook values. (Several values I first typed from memory were wrong and were replaced by the computed ones.)
- **`Bridge/Simulation.py`** (numba, multi-threaded): `deal_summaries(n, seed)` deals and summarizes n decks into per-seat per-suit lengths and honor bitmasks. Each deal has its own splitmix64 stream, so results depend only on the seed, never on the thread count or n (tested). A first version allocated per deal inside the parallel loop and was slower on 6 threads than on 1; working in blocks of 4096 deals fixed it (20M deals: 8.2 s serial, 1.5 s on 6 threads). About 25x faster than a vectorised numpy dealer and over 1000x faster than `Deck`/`Hand` objects. Kernels are `# pragma: no cover` (numba-compiled) and are verified against `Deck`/`Hand` for conventions and against `Probability` statistically.
- **`Notebooks/HCP stats.ipynb` rewritten** (49 cells, 19 figures, all labelled, outputs saved): dealing speed and thread scaling; exact vs simulated HCP with z-scores and chi-square checks; **the exact distribution is a weighted multivariate hypergeometric** (the honor count alone is hypergeometric, and a plain hypergeometric cannot fit because it is under-dispersed while HCP is over-dispersed, variance/mean 1.71); eight fitted families scored against the exact pmf; PyMC fits with LOO comparison; hand shapes; partner statistics for points, suit lengths, fits, opponent splits, aces and shape agreement; who opens; a headline table.
- **What it found:**
  - Best parametric fit is the shifted gamma (KL 1.0e-3 nats), then log-normal; **Johnson SU collapses onto the log-normal** (a first single-start fit was stuck at its normal limit, an optimizer problem I fixed with multi-start). No smooth family gets the tails right (gamma overestimates P(25+ points) by about 100%, normal underestimates by about 50%).
  - With 1,000 hands, LOO rejects the Poisson (-90) and the negative binomial (-8, about 4 SE) and cannot separate the discretized normal from the beta-binomial.
  - Partner's points: correlation -1/3 exactly, mean `(40-h)/3`; the partnership has 26+ points in 12.6% of deals, even money with 19 points in my hand; after a balanced 15-17 opening partner averages 8.05 points.
  - Suit lengths: holding 4, partner has 4+ in 33.7%; holding 5, partner has 3+ in 54.4%; an 8+ fit in a given suit 26.15%, in some suit 84.3%, in a major 48.9%; an 8-card fit splits 3-2 in 67.8%.
  - Balanced hands pair with balanced hands slightly more than chance (50.5% vs 44.9%).
  - **With the project's 14-point opening rule only 19.9% of hands open and nobody opens in 28.7% of deals** (an independence estimate says 41.2%; 28.2% +/- 0.6% from real `Deck`/`Hand` objects). `BeginningBidder` agrees with the 14-point rule on 1,200 object hands.
- **Dependencies:** numba is now a runtime dependency; pymc and arviz are in the notebooks group (numba compile mode, there is no C compiler on this machine).
- **Performance review** (measured, nothing changed): the TODOs are in PROJECT_MAP.md. Headline: 84% of the notebook's 388 s is the two `fit_all` calls, one objective evaluation costs 528 us with frozen scipy distributions vs 21 us with `scipy.special` (25x), and the object-based play path runs 2,200 rounds/s/thread with the cost in Python object overhead.
- **Design decisions recorded in the map:** `Card` stays as is; `Hand` is to be reworked so strategies can count cards; scoring and whole games come later; explicit RNG plumbing for harnesses is a near-term TODO.

## 2026-11-20 — cleanup pass (the six cleanup items from the map)

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
