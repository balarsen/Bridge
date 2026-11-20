# Bridge — Project Map

Current state of the repo and what is open. Finished work and its history are in [DONE.md](DONE.md).

Snapshot: 2026-11-20, branch `master`. HEAD is the uv commit (`5271b77`); the cleanup pass described in DONE.md is in the working tree, **not yet committed**. Nothing is pushed.
Goal (README): automatically play bridge and collect statistics on various strategies.

## 1. Health at a glance

| Item | State |
|---|---|
| Python | 3.14 pinned (`.python-version`), `requires-python >=3.12`; the suite was also run on 3.12 |
| Tooling | uv; `uv sync`, `uv run pytest`; `pyproject.toml` + `uv.lock` |
| Dependencies | runtime: numpy. groups: `dev` (pytest, pytest-cov), `notebooks` (notebook, pandas, scipy, seaborn, matplotlib, nbstripout) |
| Tests | **143 pass**, `filterwarnings = error`, so any warning fails the suite |
| Coverage | **100% statement and branch** of `Bridge/` (`.coveragerc`: `source = Bridge`, `branch = True`, tests omitted); `uv run pytest --cov=Bridge --cov-report=html` writes `htmlcov/` |
| CI | `.github/workflows/ci.yml` (3.12 / 3.13 / 3.14, dev group only); verified locally, not yet run on GitHub |
| Remote | commits are local, not pushed |

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
| `Notebooks/HCP stats.ipynb` | HCP distribution over 100k deals and balanced-hand statistics; runs end to end on the current packages (executed headlessly, ~1 min); not run by CI |
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

### Housekeeping
1. **Commit the cleanup pass** (and decide whether to push, which would trigger the first real CI run).
2. **nbstripout** is a dependency but not installed in the repo; the README has the one-time opt-in command.
3. Optionally run the notebook in CI (`jupyter nbconvert --execute`); it takes about a minute and needs the `notebooks` group.

### Features (README roadmap)
4. Bidding beyond the opening bid: `raiseBid`, `jumpBid`, double / redouble, responder logic.
5. From auction to play: turn the winning bid into contract, declarer and trump; opening lead by the left-hand opponent; dummy.
6. Scoring: use `Table`/`Seat.score` or replace them; contract scoring, vulnerability.
7. More play strategies and bidding strategies behind the existing `HandLogic` / `Bidding_logic` interfaces, then a harness to compare them statistically (the project's stated goal).
8. A full-game loop: deal, bid, play, score, repeat, with seeded runs (the `rng` plumbing is ready for it).

### Design questions to settle when we get there
- Should hands stay `list` subclasses or become a small class with a played-cards history (needed for any strategy that counts cards)?
- Should `Card` compare as a total order (suit then value)? With trump now handled in `Trick.beats`, this is purely about convenience (sorting a hand across suits).
- How far toward real bridge rules do we go (vulnerability, doubles, scoring) versus a simpler statistics harness?
- `Deck(rng=None)` shares one generator across all decks; fine for scripts, but a simulation harness should pass its own `Generator` (or per-worker seeds) explicitly.

## 4. Suggested next steps
- Commit the cleanup pass.
- Build the end-to-end loop (items 5 and 8: auction to contract to play to score), then 4, 6 and 7.
