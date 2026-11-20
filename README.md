# Bridge

This is an ongoing (slow) project meant to be able to automatically play bridge
and collect statistics on various strategies.

## Setup

The project uses [uv](https://docs.astral.sh/uv/) (Python 3.12+, developed on 3.14).

```
uv sync          # creates .venv with the package, test and notebook dependencies
uv run pytest
```

Notebooks: `uv run jupyter notebook Notebooks/`

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
