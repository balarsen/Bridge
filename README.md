# Bridge

This is an ongoing (slow) project meant to be able to automatically play bridge
and collect statistics on various strategies.

## Setup

The project uses [uv](https://docs.astral.sh/uv/) (Python 3.12+, developed on 3.13: the double-dummy solver, the `dd` group, has wheels for 3.12 and 3.13 only).

```
uv sync          # creates .venv with the package, test and notebook dependencies
uv run pytest
```

Notebooks: `uv run jupyter notebook Notebooks/`

`Notebooks/Play one hand.ipynb` takes one deal through the double-dummy table, the auction, the play (a simple strategy against one that counts cards) and the score, then judges the bidding over 2,000 deals with a confusion matrix.

`Notebooks/HCP stats.ipynb` is the statistics notebook: exact probabilities (`Bridge.Probability`) against a fast
multi-threaded simulation (`Bridge.Simulation`, millions of deals per second), distribution fits (scipy and PyMC),
hand shapes, and partner statistics such as "if I hold 4 of a suit, how many does partner hold?".

Optional, once per clone: keep Jupyter's kernel-version metadata out of git diffs while keeping
the saved outputs (this edits `.git/config` and `.gitattributes`):

```
uv run nbstripout --install --keep-output --extra-keys "metadata.language_info.version"
```

## Roadmap

### In Progress/Done
- basic structure of the game: cards, decks, hands, tricks, seats
- `<`, `>`, `==` operators so that cards and bids can be compared
- high card point scoring and hand evaluation (`Scorers`, `Hand.hcp/longest/strongest/balanced`)
- bidding mechanics (`Bid`, `Bidding`) and a first opening-bid strategy (`BeginningBidder`)
- playing a hand: `Trick`, `Round` and a `simpleHigh` playing strategy

### To Do
- Bidding beyond the opening bid (raises, jumps, double/redouble) and contracts
- Smarter play logic
- Modular system for playing and bidding strategies, compare them with statistics

See `PROJECT_MAP.md` for a module-by-module map and the cleanup TODO list.

## Testing

`uv run pytest`

#### Testing with coverage
`uv run pytest --cov-report html --cov=Bridge` then look at `htmlcov/index.html`
