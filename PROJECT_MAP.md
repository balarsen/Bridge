# Bridge — Project Map

**How this file is kept:** it holds the *current state* of the repo and the *open* items, nothing else. When something is finished, move it to [DONE.md](DONE.md) (what was done, what was measured or decided) and delete it here, in the same commit as the work. Plans that grow large get their own file ([PLAN_PLAYING.md](PLAN_PLAYING.md)) and are linked from here.

Goal (README): automatically play bridge and collect statistics on various strategies.

## 1. Health at a glance

| Item | State |
|---|---|
| Python | 3.14 pinned (`.python-version`), `requires-python >=3.12` |
| Tooling | uv; `uv sync`, `uv run pytest`; `pyproject.toml` + `uv.lock` |
| Dependencies | runtime: numpy, numba. groups: `dev` (pytest, pytest-cov), `notebooks` (notebook, pandas, scipy, seaborn, matplotlib, nbstripout, pymc, arviz) |
| Tests | **230 pass**, `filterwarnings = error`, so any warning fails the suite |
| Coverage | **100% statement and branch** of `Bridge/` (`.coveragerc`: `source = Bridge`, `branch = True`, tests omitted); `uv run pytest --cov=Bridge --cov-report=html` writes `htmlcov/` |
| CI | `.github/workflows/ci.yml`, Python 3.12 / 3.13 / 3.14, dev group only; green on every push so far |
| Remote | `origin` = github.com/balarsen/Bridge, `master` |

## 2. Module map

All code is in `Bridge/`. Seats are lower-case strings (`'north'`...), a `Position` equals its string.

### Cards and hands
| Module | Role | Notes |
|---|---|---|
| `Suit.py` | `Suit`, order spades, hearts, diamonds, clubs; `index`; `letterToSuit` | one immutable object per suit (`Suit('spades') is Suit('spades')`); equals and hashes like its name |
| `Value.py` | `Value`, `'0'` is ten; `rank` 0..12 | one immutable object per value, hashable |
| `Card.py` | `Card(value, suit)`; `toCode`/`fromCode`; `suit_index`, `rank`, `code` (= position in an unshuffled deck); `ALL_CARDS` | immutable (assigning an attribute raises), the 52 cards are created once and shared by `Deck` and `fromCode`. `<`/`>` are same-suit only (cross-suit gives False for both), so it is not a total order |
| `Hand.py` | `Hand(list)`, exactly 13 cards at creation; `get_suit`, `clubs()`..., `highCard(suit)`, `lowCard(suit)`, `distro()`, `hcp()`, `longest()`, `strongest()`, `balanced()` | still a plain list in deal order; keeps a per-suit sorted cache (built on first use, updated by `remove`, dropped by any other list change). It shrinks as cards are played and remembers nothing else; the 13 check is only at creation |
| `Deck.py` | `Deck(list)`; `shuffle`, `cut`, `deal`, `toCode`/`fromCode`; `rng` parameter | `rng=None` shares one module-level generator, an int or `Generator` gives reproducible decks |
| `Scorers.py` | `SimpleHighCardValue` (J1 Q2 K3 A4) over a deck or hands | `Hand.hcp()` uses its `cardScorer` |

### Statistics
| Module | Role | Notes |
|---|---|---|
| `Probability.py` | exact combinatorics, numpy only: `hcp_pmf(n_cards)` (dynamic program), `hcp_pmf_multivariate_hypergeometric` (closed form, independent check), `honor_count_pmf`, `shape_probabilities`, `suit_length_pmf`, `partner_suit_length_pmf`, `combined_suit_length_pmf`, `partner_aces_pmf`, `opponent_split_probabilities` | the ground truth for the simulation and for fitted models. HCP is a *weighted multivariate hypergeometric* (no single named family; the honor count alone is exactly hypergeometric) |
| `Simulation.py` | `deal_summaries(n, seed, parallel)`: numba, multi-threaded bulk dealing into per-deal `lengths[deal, seat, suit]` and `honors` bitmasks; `Deals` (`points`, `hcp`, `aces`, `shapes`), `summarize_decks` | each deal has its own splitmix64 stream, so results depend only on the seed, never on the thread count. About 1000x faster than `Deck` objects (10M deals/s on 6 threads). Kernels are `# pragma: no cover` (numba-compiled) and verified against `Deck`/`Hand` |

### Seats and play
| Module | Role | Notes |
|---|---|---|
| `Position.py` | `Position`; `name`, `cycle`, `index2pos`, `pos2index`, `side` | single source of truth for seats; the helpers are dict lookups and build no objects |
| `Table.py` | `Seat` (position + score), `Table` (north/east/south/west) | scores are stored but never updated |
| `Trick.py` | `beats(card, other, trump)`; `Trick(list)`: `nextCard`, `leadSuit`, `currentWinner`, `wouldWin`, `winner`, `getCard`, `north`... | all trump logic lives here |
| `Round.py` | `HandLogic` ABC, `simpleHigh`, `Round` (`play_trick`, `play`, `tricks`, `winners`) | the readable reference; strategies are plugins; trump is a suit or `'notrump'`; no declarer/contract concept |
| `FastRound.py` | integer-card engine: `play_deck`, `play_round(rng)`, `simulate(rng, n, trump, leader)` | `simpleHigh` at all four seats only; identical to `Round` (tested); 14.5x faster. `simulate` is a ready-made `Harness` task |
| `Harness.py` | `run_batches(task, n, seed, batch_size, workers, reduce, **config)`: process pool, one seed per batch | results depend only on `(seed, batch_size)`, never on the worker count. 4.4x on 6 cores; the pool costs about 0.8 s per call, so use it for runs of several seconds |

### Bidding
| Module | Role | Notes |
|---|---|---|
| `Bid.py` | `Bid(level, strain)` or `Bid('pass')`; total ordering; `isPass` | no double / redouble |
| `Bidding.py` | `Bidding(list)` auction, `Redeal`, `Bidding_logic` ABC | does not enforce turn order in `addBid` (`nextBid` goes in order); the winning bid is returned, but nothing turns it into a trump/declarer |
| `BeginningBidder.py` | opening bid for a beginner: 14+ HCP | `raiseBid` / `jumpBid` are stubs |

### Non-code
| File | Role |
|---|---|
| `README.md` | setup, roadmap, testing, optional nbstripout |
| `DONE.md` | history of finished work |
| `PLAN_PLAYING.md` | the plan for playing hands to judge bids (decisions, phases P0 to P7, open questions) |
| `Findings.txt` | 2012 result plus a 2026 addendum (result 2 does not reproduce) |
| `Notebooks/HCP stats.ipynb` | statistics notebook: exact vs simulated, distribution fits (scipy and PyMC), shapes, partner statistics, openers/redeal. 49 cells, 19 figures, outputs saved; about 6.5 min to run, 84% of it the fitting cells; not run by CI |
| `.github/workflows/ci.yml` | tests on 3.12-3.14 |
| `pyproject.toml`, `uv.lock`, `.python-version`, `.coveragerc`, `.gitignore`, `License.txt` (BSD-3) | config |

### Dependency graph
```
Suit   Value
  \     /
   Card ──── Scorers
    │           │
    └── Hand ───┘  (Hand uses Scorers.cardScorer)
         │
        Deck

Position ──┬── Table
           ├── Trick ── Round (also uses Hand's API and Suit)
           └── Bidding

Bid ── BeginningBidder (also Bidding_logic, Hand API)

Position, Suit, Value ── Simulation (numba)       Position, Suit ── FastRound
Probability (numpy only)                          Harness (numpy only; runs any task, e.g. FastRound.simulate)
```

## 3. Direction

- **Use the exact method wherever possible** (Brian). Counting, hypergeometric and multivariate-hypergeometric results (`Probability`) first; simulation only for what has no closed form and as a check; fitted families only as approximations.
- **Hand by hand for now** (Brian): deal, bid, play one hand. Whole games and full scoring come after the single-hand loop works.
- **Playing hands to judge bids:** [PLAN_PLAYING.md](PLAN_PLAYING.md) (correct = the highest bid that is met, shown as a confusion matrix of over and under bids; play repeated over the unknown cards, the outcome probabilities weight the bidding; declarer sees own hand and dummy, defenders perfect; prove DDS fits, then use it; the auction enters as a likelihood model). It starts with the exact suit-combination solver (P1), which needs nothing else. Six smaller open questions are at the end of the plan.

## 4. Open items

### Waiting for Brian
- Review `Notebooks/HCP stats.ipynb`. Questions it raises: which exact-hypergeometric PyMC model to build first (below), whether the 14-point opening rule should change (nobody opens in 28.7% of deals), whether to speed up its fitting cells (performance item 1).
- The six open questions at the end of [PLAN_PLAYING.md](PLAN_PLAYING.md).

### Prerequisites shared with the playing plan
- **TODO: rework `Hand` so strategies can count cards.** Today `Hand` is a `list` subclass that shrinks as cards are played and remembers nothing. Make it a small class that keeps the original 13 cards, the cards played so far (and by whom, in which trick), and what is still unseen, so a strategy can ask "which spades are still out?", "how many trumps have been played?". Keep the `get_suit`/`hcp`/`longest`/`strongest`/`balanced` API. Touches `Hand`, `Round` (which removes cards from hands today), `simpleHigh` and tests. Natural companion to the exact "unseen cards are hypergeometric" results in `Probability`. The per-suit cache that `Hand` already has is the part of this that the performance work covered; what is left is the memory of played cards.
- **TODO: scoring and whole games** (contract, declarer, tricks over/under, vulnerability, doubles/redoubles, part-score and game bonuses, rubber/duplicate scoring, dealer and vulnerability rotation over a session). The expected score in the playing plan needs duplicate scoring first.
- **TODO (soon): explicit RNG plumbing.** `Deck(rng=None)` shares one module-level generator across all decks, fine for scripts but not for a harness. Still needed: a harness or `Game` object that owns a `np.random.Generator` and passes it to every `Deck`; no use of the shared default inside library code paths; tests that the same seed reproduces a whole session. (`Harness` and `Simulation` already derive reproducible streams from a seed.)

### Bridge features (README roadmap)
1. Bidding beyond the opening bid: `raiseBid`, `jumpBid`, double / redouble, responder logic.
2. From auction to play: turn the winning bid into contract, declarer and trump; opening lead by the left-hand opponent; dummy.
3. More play strategies and bidding strategies behind the existing `HandLogic` / `Bidding_logic` interfaces, then a harness to compare them statistically (the project's stated goal).
4. A full-game loop: deal, bid, play, score, repeat, with seeded runs.
5. **Redeal rule:** with the 14-point opening rule nobody opens in about 28.7% of deals (an independence estimate would say 41.2%); real bridge uses 12-13 points. Decide whether `BeginningBidder.OPEN_HCP` should be lower, or add a rule (for example the rule of 20) so auctions start.
6. Strategies can now be scored against exact baselines (for example a notrump opening should leave partner about 8.05 points on average).

### Statistics / PyMC ideas
- **Use the exact multivariate hypergeometric as a PyMC model.** Its likelihood is exact (`C(4,a) C(4,k) C(4,q) C(4,j) C(36,n-a-k-q-j) / C(52,n)`), so it can carry real inference instead of a parametric approximation. Candidates: infer the deck/honor composition from observed hands; Bayesian check that a shuffle or dealing machine is fair (honor counts per hand against the exact pmf); partner-hand inference (posterior of partner's points, suit lengths and aces given my hand and the bidding so far); a hierarchical model across players or sessions.
- No smooth family gets the tails right (they overestimate P(25+ points) by about 2x or underestimate it); a model that keeps the bounded, finite-population structure should. Decide whether a fitted family is ever needed now that the exact pmf is cheap.
- Conditional distributions that need the whole hand (not just points): partner's points given my *shape and honors* (exact, hypergeometric on the unseen cards), instead of the simulation-only version.

### Performance (measured 2026-11-20)
| Path | Measured | Verdict |
|---|---|---|
| `Simulation.deal_summaries` (numba) | 0.4 us/deal on one thread, 10M deals/s on 6 threads; 4M deals in 0.3 s | already fast; leave alone |
| `Probability.hcp_pmf` | 7 ms cold, then cached | fine |
| Object path: `Deck` + `Round.play` | 0.183 ms per round = 5,460 rounds/s/thread (was 0.454 ms, 2,200/s); 15,300 rounds/s on 6 workers | `FastRound` still plays `simpleHigh` 5.6x faster than the objects; the rest of the gap to the 7.8x prototype is item 2 |
| Notebook `HCP stats.ipynb` | 388 s of cell time; the two `fit_all` calls are 212 s + 114 s = 84%; PyMC 30 s; everything simulated or exact under 10 s | the fitting code, not the simulation (item 1) |
| `BeginningBidder.openBid` | 4.6 us | not worth touching |

1. **TODO: speed up the distribution fitting (the notebook goes from about 6.5 min to about 1 min).** (a) Warm-start `fit_all(exact_pmf)` from the first fit's optimum instead of starting cold again (the 114 s call only shows the parameters barely move). (b) The objective builds a frozen scipy distribution on every evaluation: **528 us against 79 us for `stats.gamma.cdf(x, ...)` against 21 us for `scipy.special.gammainc`, 25x per evaluation**, identical results; use direct cdfs (`special.gammainc`, `erf`, `betainc`, `ndtr`). (c) The tolerances (xatol 1e-10, fatol 1e-15, 40,000 evaluations, 3 restarts, two optimizers per start) are far tighter than the 1e-6 differences reported; a cold gamma fit needs 200-430 evaluations. Loosen them and use one optimizer unless a family fails to converge (only Johnson SU needs the multi-start). (d) The 8 families are independent: fit them in parallel (`joblib`, already installed through PyMC; about 5x on 6 cores). (e) Cache the fits keyed on the pmf. PyMC (30 s) is mostly numba compile time per model plus the beta-binomial's slow sampling (14 s); low priority.
2. **Low priority: the rest of the gap on the object path** (2.5x was reached with the API unchanged, a scratch prototype with leaner classes reached 7.8x). What is left needs structural changes: `Trick` and `Hand` as slotted classes rather than `list` subclasses, the trick winner kept as state while cards are played, trick and winner records without `Position` names, and an integer seat all the way through `Round`. Worth it only if strategies other than `simpleHigh` are run at scale (`FastRound` already covers `simpleHigh`). Usage note, not library: pass one shared `Generator` to every `Deck` instead of `Deck(rng=int)`, which builds a generator per deck (about 17 us of a 52 us build).
3. **Low priority, only if we want billions of deals:** streaming reducers in the numba kernels (accumulate joint HCP counts, suit-length matrices and shape counts per thread and merge, so no per-deal arrays; today 100M deals would need 3.2 GB); compute `hcp`/`aces` in the kernel or `cached_property` (the `Deals` properties recompute on every access, sorting shapes for 16M hands takes about 1.2 s); a partial shuffle when only the two partner hands matter (up to 2x).
4. **Decision later:** a compiled (numba or bitboard) play engine for strategies other than `simpleHigh`; the search-oriented one is part of [PLAN_PLAYING.md](PLAN_PLAYING.md). Cost: plain-Python strategies stay at object speed, so compile only what large comparisons need.
5. **TODO: keep the numbers honest.** The figures above are one-off measurements. Add a small benchmark script (rounds/s, deals/s, notebook cell times from the executed notebook's timing metadata, which `nbconvert` records) to re-run before and after each change; not part of the CI gate.
6. **Do not optimise:** `Bidding`, `BeginningBidder`, `Position`'s string API, `deal()` (2 us), `Probability` (7 ms and cached), the test suite (8 s).

### Housekeeping
- **nbstripout** is a dependency but not installed in the repo; the README has the one-time opt-in command.
- Optionally run the notebook in CI (`jupyter nbconvert --execute`); about 6.5 minutes now, about 3 or less after performance item 1, and needs the `notebooks` group.
