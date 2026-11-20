# Plan: playing hands to judge whether a bid was correct

Status: proposal for Brian to react to (2026-11-20). Nothing here is built yet. Current state of the repo is in [PROJECT_MAP.md](PROJECT_MAP.md), finished work in [DONE.md](DONE.md).

## 1. Goal and what "correct" means

Play a hand (declarer and defenders) well enough that the *result* can be used to judge the auction that led to it. The play must:

* contain **finesses**: declarer faces real guesses about where cards are, so a double-dummy answer (everyone sees everything) is not enough;
* make **no mistakes**: every player is optimal *given what that player knows*;
* have **every player count cards**: track what has been played, who is void, what is still out, and use it.

A bid is **correct** when its expected result is (nearly) the best available *given the information the bidder had*. That is a statement about the bidder's information, not about the deal that happened to be dealt: a 4-heart bid that goes down because the king was offside can still be correct. So there are three levels of judging, cheapest first, and the plan builds toward the last:

| Level | Question | Information used | Cost |
|---|---|---|---|
| A. Hindsight | did the contract make; how far from par (best contract with all 52 cards known)? | the whole deal | cheap, noisy, not a fair test of a bid |
| B. Partnership | over the two hands that bid, which contract has the best expected score, averaged over the opponents' cards? | the partnership's 26 cards, opponents' cards at their exact prior | moderate; the first useful evaluator |
| C. Per call | for each call in the auction, which candidate call has the best expected score given only that player's hand and the auction so far? | one hand plus the auction; the rest sampled/conditioned exactly where possible | expensive; needs a model of what the other calls mean |

Expected score is duplicate scoring (contract, overtricks, undertricks, game/slam bonus, vulnerability) so scoring is a prerequisite (section 8).

## 2. Three information models for play

Real "no mistakes" single-dummy play is hard, so build a ladder and stop where it is good enough:

| Mode | Declarer sees | Defenders see | Finesses? | Use |
|---|---|---|---|---|
| **DD** (double dummy) | everything | everything | no (all known) | par and an upper bound on tricks; the reference everything else is compared with |
| **SD declarer, DD defenders** | own hand + dummy | everything | yes | the standard textbook assumption for suit-combination analysis: defenders are as good as possible, so a finesse is only worth taking when it is right on average. Conservative for declarer. First target. |
| **SD all** | own hand + dummy | own hand + dummy | yes | realistic and fair, but defenders then need partner-signalling conventions to be good; leave until the rest works |

Equivalent cards (Q and J in the same hand, say) are the other subtlety: a perfect defender plays them with equal probability (a deterministic choice leaks information that declarer can exploit). So the opponents **randomize uniformly among equivalent cards** and declarer's inference assumes that. This is exactly what produces **restricted choice** (if the queen appears, the jack is more likely to be with the same defender: odds 2:1), and it can be computed exactly.

## 3. Card counting, precisely

Each player carries a `Knowledge` object that is updated after every card:

* own hand, dummy (visible after the opening lead), every card played so far, by whom and in which trick;
* **voids**: a player who fails to follow suit is void in that suit;
* **unseen cards** per suit, and how many cards each hidden hand still holds (always known: 13 minus cards played);
* from those, the **vacant places** for each hidden hand: the number of slots that can still hold an unseen card of a given suit. The chance that a given unseen card is in a given hand is then `vacant_places(hand) / total_vacant_places` (exact, no sampling).

This is the same bookkeeping as the **Hand rework** TODO in the map (a hand that remembers its original cards and what has been played). Do that first.

Exact inference where it exists (preferred, see "prefer exact methods"):

* priors over hidden hands are hypergeometric: `Probability.partner_suit_length_pmf`, `opponent_split_probabilities`, `partner_aces_pmf`;
* after voids and counts are known, the remaining distribution is again hypergeometric on the unseen cards with the vacant places;
* restricted choice and "vacant places" odds are one-line Bayes updates.

Where exactness stops: constraints from the **auction** ("North opened 1 spade", so 14+ points, 5+ spades by our `BeginningBidder` rule) over the full hidden hands. Plan: express them as hard constraints produced by the bidding code (the rule that made the call can say which hands could have made it), then (1) count exactly where the constraint is on points and shape only (extend `Probability` with constrained counts, same dynamic program) and (2) otherwise sample hidden hands by rejection or importance weights using the fast dealer. A likelihood model of the auction (P(call | hand)) is the more general form and can come later.

## 4. Finesses: an exact suit-combination solver first

Before any full-hand search, build the exact answer for **one suit**: given declarer's and dummy's cards in the suit and how many cards are missing, which line of play wins the most tricks in that suit on average?

* **Worlds:** every way the missing cards split between the two defenders, each with its exact probability (`C(m, j) * C(26 - m, 13 - j) / C(26, 13)` for `j` cards with the left-hand opponent, then every subset of the missing cards equally likely).
* **Lines:** every sequence of plays from declarer's hands, with the defenders' replies determined by the model of section 2 (best play, uniform among equivalents).
* **Solve:** expectimax over information sets: at each step declarer's choice may depend only on what declarer has seen so far, so worlds that look the same so far must share a choice. Values are expected tricks and the probability of each trick count.
* **Output:** the best line, its expected tricks, and the probability of making N tricks, for any holding. For example A-Q-x opposite x-x-x: finesse versus playing for the drop, the 50% finesse, the restricted-choice odds for J-x-x-x.

Why start here: it is small, fast, exact, has well known textbook answers to test against, and it is what gives the full-hand player its finesse decisions where entries and timing do not matter. It cannot see entries, squeezes or interaction between suits; those come from the full-hand search below.

## 5. The full-hand player

### 5.1 Representation and speed

Search needs a compact state, so the engine uses **bitboards**: each seat's hand is a 52-bit mask, a trick is a few integers, legal moves are bit operations. This is the same direction as the "integer-array play engine" item in the performance review (measured there: an API-shaped integer version of one round is 7.8x faster than the current objects, a fully inlined one 12-14x). The readable object classes (`Card`, `Hand`, `Trick`, `Round`) stay as the reference implementation and the test oracle, exactly as `Simulation` is checked against `Deck`/`Hand`.

### 5.2 Double-dummy solver (perfect information)

Input: four hands, trump, who leads, any partly played trick. Output: tricks for each side under best play, and the value of each legal first card (needed for the single-dummy player below). Method: alpha-beta search with a transposition table, move ordering, and pruning of **equivalent cards** (cards that are adjacent in rank among the cards still in play are interchangeable).

**Decision for Brian:** write our own numba solver, or depend on **`endplay`** (a Python wrapper around the mature DDS solver by Bo Haglund; it resolves for Python 3.14 here, license and Linux wheels for CI to be checked)? Recommendation: write a small solver of our own for endings of up to about 6 cards a hand and use it as the test oracle, then benchmark 13-card hands; use `endplay` for production speed if ours is too slow, keeping ours as the check. Our own solver is also the only way to make it fit the information-set machinery below, and owning it fits the project's aims.

### 5.3 Single-dummy play: sample, solve, vote

For a decision by player P with knowledge `K`:

1. sample `S` hidden-hand assignments consistent with `K` (voids, counts, auction constraints), exactly distributed as the posterior (section 3);
2. solve each sample double-dummy, getting the value of every legal card;
3. play the card with the best average value; break ties among equivalent cards uniformly at random.

This is "perfect information Monte Carlo". It plays finesses correctly whenever the finesse is right on average, counts cards (through the sampler), and makes no mistakes in the sense above. Its known weakness is **strategy fusion**: each sample assumes P will later know the cards, so it can overvalue lines that need a guess it will in fact have to make. Mitigations, in increasing cost: use the exact suit-combination solver (section 4) for the suit being played whenever the position is a pure suit-combination problem; compare PIMC against that exact solver on single-suit positions to measure the loss; if the loss matters, move to information-set search.

### 5.4 Opening lead, dummy, contract

`Round` has to learn the contract (level, strain, doubled), declarer and dummy: opening lead by declarer's left-hand opponent, dummy shown after the lead, dummy played by declarer. The opening lead is the first single-dummy decision for the defenders and depends on the auction, so it exercises the auction-constraint machinery.

## 6. Modules and tests

| New module | Contents | Checked against |
|---|---|---|
| `Scoring` | duplicate score of a contract result, vulnerability, doubles | published scoring tables |
| `Contract` | level, strain, declarer, dummy, doubled | rules |
| `SuitCombinations` | exact solver of section 4 | textbook probabilities (finesse 50%, 3-2 split 67.8%, restricted choice 2:1), brute-force enumeration of all worlds and all lines for small holdings |
| `Knowledge` | card counting of section 3, exact vacant-place probabilities, posterior sampler | hypergeometric formulas in `Probability`; **property test: a player's choice depends only on its information set** (swap unseen cards between hidden hands consistently with the information and the choice must not change; this is the test that no player cheats) |
| `DoubleDummy` | bitboard solver (or the `endplay` adapter) | brute-force minimax on small endings, `endplay` on random 13-card deals |
| `SingleDummy` | PIMC player of section 5.3 | the exact suit-combination solver on single-suit positions; mean tricks never above DD |
| `Evaluator` | level B and C of section 1 | par, known contracts, convergence under more samples |

All of it follows the project's habits: reference object code first, compiled code checked against it, seeds and thread-count independence, 100% branch coverage with the numba kernels excluded and verified by equivalence tests.

## 7. Phases

| Phase | Deliverable | Size | Depends on |
|---|---|---|---|
| P0 | **prerequisites already on the map:** `Hand` that tracks played/unseen cards; scoring; contract/declarer/dummy/opening lead in `Round`; explicit RNG plumbing (a harness that owns the generator) | M | |
| P1 | `SuitCombinations`: exact finesse / drop / restricted-choice solver, with its own small tests and a notebook of the classic holdings | M | none (can start now) |
| P2 | `DoubleDummy` on bitboards: endings first, then 13 cards; benchmark; decide own vs `endplay` | L | P0 |
| P3 | `Knowledge` + posterior sampler, information-set property test | M | P0 |
| P4 | `SingleDummy` PIMC player; measure strategy fusion against P1 | M | P2, P3 |
| P5 | `Evaluator` level B: expected score of every (strain, level, declarer) for a partnership's 26 cards, "was this contract best?" | M | P4, scoring |
| P6 | Level C: per-call evaluation, needs the bidding side to produce a call for every candidate (a system model, beyond `BeginningBidder`) and auction-constrained sampling | L | P5, a bidding system |
| P7 | speed: multiprocessing over samples and deals, caching solved positions by canonical form (suit relabelling) | M | P4 |

P1 is the cheapest start with the highest "exact" content and no dependency on the other work; P0 is mostly work the map already lists.

## 8. Where the other TODOs fit

* **Hand rework** (count cards): P0 and the basis of `Knowledge`.
* **Scoring and whole games:** `Scoring` is needed for every level of judging; whole-game scoring (rubber, vulnerability rotation) can wait.
* **Explicit RNG plumbing and multiprocessing:** sampling hidden hands is embarrassingly parallel; the harness in the multiprocessing plan is the thing P5 and P6 run on.
* **Integer-array engine:** this plan is its first real customer.
* **Exact multivariate hypergeometric in PyMC:** the unseen-card posterior of section 3 is a natural PyMC / exact-likelihood use.

## 9. Decisions needed from Brian

1. **Information model:** start at "SD declarer, DD defenders" (finesses matter, defenders unbeatable, no signalling needed)? Or go straight to fully single-dummy defenders?
2. **Definition of correct:** expected duplicate score (recommended; IMP/match-point variants later), judged at level B first, then level C?
3. **Double-dummy engine:** own numba solver (recommended as oracle and learning) with `endplay` as the production option, or `endplay` from the start?
4. **Equivalent cards:** uniform random among equivalents (recommended, gives restricted choice exactly), or deterministic lowest?
5. **Auction information:** hard constraints derived from the bidding code (recommended first), or a likelihood model?
6. **Start now with P1** (suit combinations, independent of everything else)?

## 10. Risks

* **Double-dummy speed:** 13-card search can be slow without careful pruning; mitigated by `endplay` as a fallback and by caching.
* **Strategy fusion** in PIMC: quantified against the exact suit-combination solver before trusting it.
* **Bidding information:** the quality of "bid correctness" is limited by how well the auction's meaning is modelled; the project's one bidder (`BeginningBidder`) is far too thin for level C. Level B does not need it.
* **Variance:** expected scores from sampling need many deals; use common random numbers (same deals for every candidate contract), exact conditioning where possible, and the multiprocessing harness.
