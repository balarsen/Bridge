# Bridge — Project Map

Current state of the repo and what is open. Finished work and its history are in [DONE.md](DONE.md).

Snapshot: 2026-11-20, branch `master`, pushed to `origin` (github.com/balarsen/Bridge). The statistics work (Simulation, Probability, the rewritten notebook) is described in DONE.md.
Goal (README): automatically play bridge and collect statistics on various strategies.

## 1. Health at a glance

| Item | State |
|---|---|
| Python | 3.14 pinned (`.python-version`), `requires-python >=3.12`; the suite was also run on 3.12 |
| Tooling | uv; `uv sync`, `uv run pytest`; `pyproject.toml` + `uv.lock` |
| Dependencies | runtime: numpy, numba. groups: `dev` (pytest, pytest-cov), `notebooks` (notebook, pandas, scipy, seaborn, matplotlib, nbstripout, pymc, arviz) |
| Tests | **167 pass**, `filterwarnings = error`, so any warning fails the suite |
| Coverage | **100% statement and branch** of `Bridge/` (`.coveragerc`: `source = Bridge`, `branch = True`, tests omitted); `uv run pytest --cov=Bridge --cov-report=html` writes `htmlcov/` |
| CI | `.github/workflows/ci.yml` (3.12 / 3.13 / 3.14, dev group only); first run on GitHub was green on all three (commit `8c12e41`) |
| Remote | `origin` = github.com/balarsen/Bridge, `master` pushed |

## 2. Module map

All code is in `Bridge/`. Seats are lower-case strings (`'north'`...), a `Position` equals its string.

### Cards and hands
| Module | Role | Notes |
|---|---|---|
| `Suit.py` | `Suit`, order spades, hearts, diamonds, clubs; `letterToSuit` | equals its string; hashable |
| `Value.py` | `Value`, `'0'` is ten; `rank` 0..12 | hashable |
| `Card.py` | `Card(value, suit)`; `toCode`/`fromCode` | a card is only suit + value, no trump state. `<`/`>` are same-suit only (cross-suit gives False for both), so it is not a total order |
| `Hand.py` | `Hand(list)`, exactly 13 cards at creation; `get_suit`, `clubs()`..., `highCard(suit)`, `lowCard(suit)`, `distro()`, `hcp()`, `longest()`, `strongest()`, `balanced()` | `Hand` shrinks as cards are played; the 13 check is only at creation |
| `Deck.py` | `Deck(list)`; `shuffle`, `cut`, `deal`, `toCode`/`fromCode`; `rng` parameter | `rng=None` shares one module-level generator, an int or `Generator` gives reproducible decks |
| `Scorers.py` | `SimpleHighCardValue` (J1 Q2 K3 A4) over a deck or hands | `Hand.hcp()` uses its `cardScorer`; used by the notebook |

### Statistics (new)
| Module | Role | Notes |
|---|---|---|
| `Probability.py` | exact combinatorics, numpy only: `hcp_pmf(n_cards)` (dynamic program), `hcp_pmf_multivariate_hypergeometric` (closed form, independent check), `honor_count_pmf`, `shape_probabilities`, `suit_length_pmf`, `partner_suit_length_pmf`, `combined_suit_length_pmf`, `partner_aces_pmf`, `opponent_split_probabilities` | the ground truth for the simulation and for fitted models. HCP is a *weighted multivariate hypergeometric* (no single named family; the honor count alone is exactly hypergeometric; a plain hypergeometric cannot fit because it is under-dispersed and HCP is over-dispersed) |
| `Simulation.py` | `deal_summaries(n, seed, parallel)`: numba, multi-threaded bulk dealing into per-deal `lengths[deal, seat, suit]` and `honors` bitmasks; `Deals` (`points`, `hcp`, `aces`, `shapes`), `summarize_decks` | each deal has its own splitmix64 stream, so results depend only on the seed, never on thread count (tested). About 1000x faster than `Deck` objects (10M deals/s on 6 threads). Kernels are `# pragma: no cover` (numba-compiled) and verified against `Deck`/`Hand` instead |

### Seats and play
| Module | Role | Notes |
|---|---|---|
| `Position.py` | `Position`; `cycle`, `index2pos`, `pos2index`, `side` | single source of truth for seats |
| `Table.py` | `Seat` (position + score), `Table` (north/east/south/west) | scores are stored but never updated |
| `Trick.py` | `beats(card, other, trump)`; `Trick(list)`: `nextCard`, `leadSuit`, `currentWinner`, `wouldWin`, `winner`, `getCard`, `north`... | all trump logic lives here |
| `Round.py` | `HandLogic` ABC, `simpleHigh`, `Round` (`play_trick`, `play`, `tricks`, `winners`) | one strategy only; trump is a suit or `'notrump'`; no declarer/contract concept |

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
| `Findings.txt` | 2012 result plus a 2026 addendum (result 2 does not reproduce, see DONE.md) |
| `Notebooks/HCP stats.ipynb` | statistics notebook: exact vs simulated (4M deals), distribution fits (scipy and PyMC), shapes, partner joint statistics, openers/redeal, headline table. 49 cells, 19 labelled figures, executed outputs saved; ~6.5 min to run (84% of it the fitting cells, see the performance review); not run by CI |
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
```

## 3. Open items

### Next: review the statistics notebook with Brian
`Notebooks/HCP stats.ipynb` was rebuilt around `Probability` + `Simulation` (see DONE.md for what is in it and what it found) and is ready to review. The open questions it raises: which of the exact-hypergeometric PyMC models below to build first, whether the 14-point opening rule should change (nobody opens in 28.7% of deals), and whether to speed up its fitting cells (see the performance review).

### Housekeeping
1. **nbstripout** is a dependency but not installed in the repo; the README has the one-time opt-in command.
2. Optionally run the notebook in CI (`jupyter nbconvert --execute`); about 3 minutes and needs the `notebooks` group.

### Statistics / PyMC ideas (to decide after we review the notebook)
- **Use the exact multivariate hypergeometric as a PyMC model.** Its likelihood is exact (`C(4,a) C(4,k) C(4,q) C(4,j) C(36,n-a-k-q-j) / C(52,n)`), so it can carry real inference instead of a parametric approximation. Candidates: infer the deck/honor composition from observed hands; Bayesian check that a shuffle or dealing machine is fair (honor counts per hand against the exact pmf); partner-hand inference (posterior of partner's points / suit lengths / aces given my hand and the bidding so far); a hierarchical model across players or sessions.
- Fit quality: no smooth family gets the tails right (they overestimate P(25+ points) by ~2x or underestimate it); a model that keeps the bounded, finite-population structure (hypergeometric-based) should. Decide whether a fitted family is ever needed now that the exact pmf is cheap.
- Conditional distributions that need the whole hand (not just points): partner's points given my *shape and honors* (exact by hypergeometric on the unseen cards), instead of the simulation-only version.

### Performance review (measured 2026-11-20, nothing changed yet)
Measured with cProfile / micro-timings on this machine (6 cores). Where time actually goes, and what is worth doing, in order of impact:

| Path | Measured | Verdict |
|---|---|---|
| `Simulation.deal_summaries` (numba) | 0.4 us/deal on one thread, 10M deals/s on 6 threads (4-5x from threading); 4M deals in 0.3 s | already fast; leave alone (ideas below only if we want billions of deals) |
| `Probability.hcp_pmf` | 7 ms cold, then cached | fine |
| Object path: `Deck` + `Round.play` (simpleHigh) | **0.447 ms per round = 2,200 rounds/s/thread**; 84% of it is playing the 13 tricks, deck build + shuffle 0.076 ms, deal 0.003 ms | the part that will matter once strategies are compared over millions of rounds (see 2-4) |
| Notebook `HCP stats.ipynb` | 388 s of cell time; **212 s + 114 s = 84% is the two `fit_all` calls**; PyMC 30 s; everything simulated or exact < 10 s in total | the fitting code, not the simulation (see 1) |
| `BeginningBidder.openBid` | 4.6 us | not worth touching |

1. **TODO: speed up the distribution fitting (notebook goes from ~6.5 min to ~1 min).** (a) Warm-start `fit_all(exact_pmf)` from the first fit's optimum instead of starting cold again (the 114 s call only exists to show the parameters barely move). (b) The objective builds a frozen scipy distribution on every evaluation: **528 us vs 79 us for `stats.gamma.cdf(x, ...)` vs 21 us for `scipy.special.gammainc`, 25x per evaluation** with identical results; use direct cdfs (`special.gammainc`, `erf`, `betainc`, `ndtr`) or at least the unfrozen `.cdf(x, *params)`. (c) The tolerances (xatol 1e-10, fatol 1e-15, 40,000 evaluations, 3 restarts, two optimizers per start) are far tighter than the 1e-6 differences the notebook reports; a cold gamma fit needs 200-430 evaluations. Loosen them and use one optimizer unless a family fails to converge (only Johnson SU needs the multi-start). (d) The 8 families are independent: fit them in parallel (`joblib` is already installed via PyMC; ~5x on 6 cores). (e) Cache the fits keyed on the pmf so re-running the notebook does not refit. PyMC (30 s) is mostly numba compile time per model plus the beta-binomial's slow sampling (14 s); low priority, maybe fewer draws for the demo or a better parametrisation.
2. **TODO: make the object path cheaper without changing its API (est. 3-5x on play).** The profile of 300 rounds shows the cost is Python object overhead, not algorithms: `Suit.__eq__` (about 760 calls per round, each with `isinstance`), `Card.__eq__` (about 250/round), `tuple.index` (about 625/round, from `Value.rank` and the suit ordering in `simpleHigh.lead`), `Hand.get_suit` sorting on every call (46/round, 6-9 us each), `Position` string validation inside `Trick` and `index2pos`. Concretely:
   - Make `Card` immutable (nothing mutates it since `trump` was removed) and create the 52 cards once; `Deck()` becomes a list copy (26 us now). Precompute `suit_index` and `rank` ints on the card and compare those in `Trick.beats` and `Hand.get_suit` instead of going through `Suit.__eq__`; intern `Suit` and `Value`.
   - `Hand` keeps per-suit sorted lists, updated on removal (the same change as the Hand-rework TODO above): `get_suit` becomes O(1), and `distro`, `longest`, `strongest`, `balanced` come from one pass instead of 4 `get_suit` calls each (21-27 us each now).
   - Integer positions internally (`Position` validates the string on every call).
   - Pass one shared `Generator` to every `Deck` instead of `Deck(rng=int)`, which creates a new generator per deck (+23 us on an 86 us build). Ties to the RNG-plumbing TODO.
   - `SimpleHighCardValue.cardScorer` rebuilds a dict on every card: make it a module constant (tiny, but 85% of an opening-bid decision).
3. **TODO: multiprocessing for the object path, before any compilation.** Deals are independent: `ProcessPoolExecutor` with one `SeedSequence.spawn` child per worker, batches of at least 10,000 rounds per task to amortise Windows process start-up. About 5x on 6 cores for almost no code, and it is the same seed plumbing the RNG TODO needs.
4. **Decision for later: an integer-array play engine** (cards 0-51, hands as arrays or bitmasks, a numba kernel for trick resolution and compiled baseline strategies such as `simpleHigh`), expected 100x or more over objects. Same pattern as `Simulation`: the readable object classes stay as the reference implementation and the test oracle, the compiled engine is checked against them (same seeds, same deals). Cost: strategies that are plain Python stay at object speed, so compile only what large comparisons need. Worth deciding once whole-game simulation exists.
5. **Low priority, only if we want billions of deals:** streaming reducers in the numba kernels (accumulate joint HCP counts, suit-length matrices and shape counts per thread and merge, so no per-deal arrays; today 100M deals would need 3.2 GB); compute `hcp`/`aces` in the kernel or `cached_property` (the `Deals` properties recompute on every access, sorting shapes for 16M hands takes about 1.2 s); a partial shuffle when only the two partner hands matter (up to 2x).
6. **Do not optimise:** `Bidding`, `BeginningBidder`, `Position`'s string API, `deal()` (2 us), `Probability` (7 ms and cached), the test suite (4 s).
7. **TODO: keep the numbers honest.** The figures above are one-off measurements. Add a small benchmark script (rounds/s, deals/s, notebook cell times from the executed notebook's timing metadata, which `nbconvert` records) that can be re-run before and after each change; not part of the CI gate.

### Bridge-playing features that the statistics now inform
- **Redeal rule:** with the project's 14-point opening rule, simulation says nobody opens in about 28.7% of deals (an independence estimate would say 41.2%); real bridge uses 12-13 points. Decide whether `BeginningBidder.OPEN_HCP` should be lower, or add a rule (e.g. rule of 20) so auctions actually start.
- Strategies can now be scored against exact baselines (e.g. a notrump-opening rule should pass partner's points about 8.05 on average).

### Features (README roadmap)
4. Bidding beyond the opening bid: `raiseBid`, `jumpBid`, double / redouble, responder logic.
5. From auction to play: turn the winning bid into contract, declarer and trump; opening lead by the left-hand opponent; dummy.
6. Scoring: use `Table`/`Seat.score` or replace them; contract scoring, vulnerability.
7. More play strategies and bidding strategies behind the existing `HandLogic` / `Bidding_logic` interfaces, then a harness to compare them statistically (the project's stated goal).
8. A full-game loop: deal, bid, play, score, repeat, with seeded runs (the `rng` plumbing is ready for it).

### Decisions and TODOs from the design questions (Brian, 2026-11-20)
- **TODO: rework `Hand` so strategies can count cards.** Today `Hand` is a `list` subclass that shrinks as cards are played and remembers nothing. Make it a small class that keeps the original 13 cards, the cards played so far (and by whom, by trick), and what is still unseen, so a strategy can ask "which spades are still out?", "how many trumps have been played?". Keep the `get_suit`/`hcp`/`longest`/`strongest`/`balanced` API. Touches `Hand`, `Round` (hands are removed from today), `simpleHigh`, and tests. Natural companion to the exact "unseen cards are hypergeometric" results in `Probability`.
- **Decision: `Card` stays as it is** (same-suit comparison only, not a total order): the easiest thing, and trump already lives in `Trick.beats`. If a sorted display of a hand is wanted later, add a sort-key helper (suit order, then value) instead of changing `Card` comparison. Low priority.
- **Decision: we are going hand by hand for now** (deal, bid, play one hand); real-bridge rules wait. **TODO: scoring and whole games** (contract, declarer, tricks over/under, vulnerability, doubles/redoubles, part-scores and game bonuses, rubber/duplicate scoring, dealer and vulnerability rotation over a session) once the single-hand loop works end to end. Builds on items 5, 6 and 8 below.
- **TODO (soon): explicit RNG plumbing for simulation harnesses.** `Deck(rng=None)` shares one module-level generator across all decks, fine for scripts but not for a harness. Needs: a harness/`Game` object that owns a `np.random.Generator` and passes it to every `Deck`; per-worker seeds from `np.random.SeedSequence.spawn` for multiprocessing; no use of the shared default inside library code paths; tests that the same seed reproduces a whole session. `Simulation.deal_summaries` already derives its stream from `(seed, deal number)`, so it is reproducible regardless of thread count.

## 4. Suggested next steps
- Commit the cleanup pass.
- Build the end-to-end loop (items 5 and 8: auction to contract to play to score), then 4, 6 and 7.
