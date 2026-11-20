# Plan: playing hands to judge whether a bid was correct

Status: plan, updated with Brian's decisions (2026-11-20). Nothing here is built yet. Current state of the repo is in [PROJECT_MAP.md](PROJECT_MAP.md), finished work in [DONE.md](DONE.md).

## 1. Goal, and what "correct" means

Play a hand (declarer and defenders) well enough that the *result* can be used to judge the bidding that led to it. The play must:

* contain **finesses**: declarer faces real guesses about where cards are, so a double-dummy answer (everyone sees everything) is not enough;
* make **no mistakes**: every player is optimal *given what that player knows*;
* have **every player count cards**: track what has been played, who is void, what is still out, and use it.

**Decisions taken (Brian):**

* **Correct = the highest bid that is met** (that makes). Compare it with the bid actually reached: a bid above it is an **overbid**, a bid below it an **underbid**, equal is correct. The output is a **confusion matrix** (section 3).
* The play is run **many times** to see **what is possible** and **how probable** each result is; those probabilities are the **weights** the bidding is judged with. A single play is never the answer, the *distribution of outcomes* is.
* Start with **declarer sees own hand and dummy, defenders play perfectly** (section 4).
* **Prove double-dummy (DDS) does what we need, then use it** (section 7.2).
* Opponents **randomize uniformly among equivalent cards** (section 4), which is what makes the success probabilities well defined (restricted choice).
* What the auction tells us about hidden hands is a **likelihood model**, not hard rules (section 6).
* Start with the **exact suit-combination solver** (P1).
* Prefer **exact** computation wherever it exists; simulation is for what has no closed form and for checking the exact answers.

### Judging a bid has three levels, cheapest first

| Level | Question | Information used | Cost |
|---|---|---|---|
| A. Hindsight | did the contract make on the actual deal; how far from par? | the whole deal | cheap, noisy, not a fair test of one bid |
| B. Partnership | over the two hands that bid, what is the highest contract that is met, and how likely is each? | the partnership's 26 cards; the opponents' cards at their exact prior (later: given the auction) | moderate; the first useful evaluator |
| C. Per call | for each call in the auction, which candidate call is best given only that player's hand and the auction so far? | one hand plus the auction, the rest conditioned by the likelihood model | expensive; needs a system model (section 6) |

A bid is judged relative to the bidder's **information**, not the deal that happened: a 4-heart bid that goes down because the king was offside can still be correct. That is why the result of play enters as a probability.

## 2. What one evaluation produces

For a partnership (their 26 cards) and every strain and declarer, repeating the play over the unknown cards gives:

* **possible**: the double-dummy result, the tricks available with perfect information (the upper bound; also what a par calculation uses);
* **probable**: the *distribution* of tricks under the play model, `P(tricks = k)` for k = 0 to 13, from which `P(contract at level L makes) = P(tricks >= 6 + L)` for every level at once (one play per strain and declarer covers all levels, assuming the play maximizes the right objective, see 7.3);
* **expected score**, using duplicate scoring (contract, overtricks, undertricks, game and slam bonus, vulnerability), which is the reason scoring is a prerequisite.

The repeats come from three sources, and the plan keeps them apart: (1) the **layout** of the cards the partnership cannot see (exact prior; this is where finesses win or lose, and it is almost all of the variation); (2) the opponents' random choices among equivalent cards; (3) any randomness inside the sampling player. The probabilities above are over (1) and (2); the exact suit-combination solver (section 5) gives the layout probabilities for one suit in closed form, and the full-hand player estimates the rest by sampling.

Everything here is a *weight*: a bid's score is the probability-weighted result over these outcomes, and the confusion matrix below is built from the same distribution.

## 3. The output for judging bids: a confusion matrix

For each deal, the partnership has a **bid reached** (from the bidding code, or a toy rule at first) and a **highest met bid**. Bids are ordered as `Bid` already orders them: level, then strain clubs < diamonds < hearts < spades < notrump (a pass is below everything).

* **Highest met bid** = the highest contract, over strains and over which of the two partners declares, that makes. Because "makes" is uncertain, it is a *distribution* over the layouts: for each sampled layout play every strain and declarer, take the highest that makes, and count. So `P(highest met = c)` is estimated directly, no threshold needed. A thresholded view ("highest bid whose probability of making is at least p") is a convenience and can be shown too; sweeping p traces out a curve.
* **Matrix:** rows = the bid actually reached (or `pass`), columns = the highest met bid (or `none makes`). Each deal contributes **soft counts**: its row gets a share across columns equal to `P(highest met = column)`. The **diagonal** is correct; **below the diagonal** (reached < met) are **underbids**, **above** are **overbids**.
* **Resolutions:** the full 35 bids plus pass, and coarse views that are easier to read: pass / part-score / game / small slam / grand slam, and level-correct but strain-wrong. Summary numbers: correct, over and under rates, and the mean level error.
* "Highest" is by bid order, which is not the same as best score (3NT scores more than 4 clubs): report the matrix for "highest met" as defined, and next to it the one for "highest expected score", and where they disagree.

First customers: a toy bidder (points and fit to a contract, for example the rule-of-points mapping) and `BeginningBidder` plus a simple responder, so the confusion matrix says how good a bidding *rule* is, which is the project's stated goal.

## 4. Information model for play (decided)

| Seat | Sees | Plays |
|---|---|---|
| **Declarer** | own hand and dummy | optimal given that: counts cards, plays finesses and guesses the way that is right on average |
| **Defenders** | everything (all four hands) | perfectly, double-dummy |

This is the standard assumption of suit-combination analysis: the defenders are as good as possible, so a finesse is only taken when it is right on average, and the result is conservative for declarer. It needs no signalling conventions. A fully single-dummy defence (defenders also unsure of partner's hand) can be added later behind the same interface.

**Equivalent cards.** A perfect defender with the queen and jack of a suit plays either with equal probability (a fixed choice leaks information that declarer could exploit). So the opponents **randomize uniformly among equivalent cards**, and declarer's inference assumes it. This produces **restricted choice** (if the queen appears, the jack is more likely to be in the same hand, odds 2:1), computable exactly, and it is part of why repeated runs differ and why the probabilities of success are meaningful.

## 5. Finesses: the exact suit-combination solver (first thing to build)

Before any full-hand search, the exact answer for **one suit**: given declarer's and dummy's cards in the suit and how many are missing, which line of play wins the most tricks in the suit on average, and with what probability of each trick count?

* **Worlds:** every way the missing cards split between the two defenders, each with its exact probability (`C(m, j) * C(26 - m, 13 - j) / C(26, 13)` for `j` cards with the left-hand opponent, then every subset of the missing cards equally likely; `Probability.opponent_split_probabilities` has the split part).
* **Lines:** every sequence of plays from declarer's two hands. The defenders reply by the model of section 4 (best play, uniform among equivalents).
* **Solve:** expectimax over information sets. Declarer's choice may depend only on what declarer has seen, so worlds that look the same so far must share a choice. Values: expected tricks, and the probability of each trick count (that distribution is the weight of section 2).
* **Output:** best line, expected tricks, `P(k tricks)`. Examples: A-Q-x opposite x-x-x (finesse versus playing for the drop, the 50% finesse), J-x-x-x and restricted choice, the 3-2 split at 67.8%.

It is small, fast, exact, with textbook answers to test against, and it needs nothing else in the plan. It cannot see entries, squeezes or interaction between suits; the full-hand search covers those.

## 6. What the auction tells us: a likelihood model (decided)

Bidding gives information about the hidden hands. Model it as a **likelihood**: `P(call | hand, auction so far, system)`. The posterior over hidden hands is the prior (uniform deals, exact) times the product of the likelihood of every call made. Hard rules ("opened, so 14+ points") are the special case where the likelihood is 0 or 1, which is what `BeginningBidder` is; a stochastic or noisy bidder gives soft likelihoods, and the same machinery handles both.

* **Interface:** a bidding system provides `call_probabilities(hand_features, auction) -> distribution over calls`. This is a step on from the current `Bidding_logic` (one method per kind of call).
* **It factorizes per seat.** Given the public auction, each call depends only on that seat's own hand, so the likelihood is a product of per-seat factors. The only coupling between seats is that hands are disjoint (no card dealt twice), which is handled by **sequential importance sampling**: sample a hand for each seat in turn from the cards still available, weighted by that seat's likelihood and by the exact count of completions where it can be computed; report the effective sample size so a bad proposal is visible. Short auctions can use plain rejection.
* **Fast evaluation:** systems are written as functions of the hand *features* (suit lengths, honors, points), exactly what `Simulation.deal_summaries` already produces, so likelihoods for millions of sampled hands are computed in the numba kernel.
* **Exact where it exists:** when a call depends only on points and shape, the posterior over (points, shape) classes is exact counting (the same dynamic program as `Probability`, with the constraint added) and the hand inside a class is uniform. Sampling is the fallback.
* **Where it is used:** level B at first uses the prior only (the auction ignored). Then the opponents' layout is drawn from the posterior given *their* calls and passes (which is what a real declarer uses); level C needs it fully, to evaluate each candidate call.

## 7. The full-hand player

### 7.1 Representation and speed

Search needs a compact state, so the engine uses **bitboards** (a seat's hand is a 52-bit mask, legal moves are bit operations). The readable object classes (`Card`, `Hand`, `Trick`, `Round`) stay as the reference implementation and the test oracle, as `Simulation` is checked against `Deck`/`Hand` and `FastRound` against `Round`. The multiprocessing harness (`Harness.run_batches`) runs the repeated plays across cores with results independent of the number of workers.

### 7.2 Double-dummy: prove DDS fits, then use it (decided)

Use DDS (Bo Haglund's double-dummy solver, through the Python package `endplay`) **if** a short spike proves it does what we need. Acceptance criteria, each pass/fail:

1. **Correct:** agrees with a brute-force minimax of our own on small endings (up to 5 cards a hand), and with itself across equivalent relabellings; and the 20-entry table (4 declarers x 5 strains) agrees with a few published double-dummy results.
2. **Fast enough:** a full 13-card position in milliseconds; a whole `calc_dd_table` fast enough to evaluate thousands of layouts per second per core; the cost of "value of every legal card" at arbitrary mid-play positions, the call the sampling player makes.
3. **API fit:** it can solve from a partly played position (cards already played, a trick in progress, any hand to lead) and return the value of each legal card, not only the final tricks.
4. **Packaging:** installs on Windows and on the CI platforms (Linux, Python 3.12 to 3.14); license acceptable (DDS is Apache-2.0; check `endplay`'s). Resolves for Python 3.14 here already.
5. **Parallel:** safe to call from the harness's worker processes (one solver thread per worker).

If it passes, DDS is the double-dummy engine and we write only the small brute-force oracle for the tests. If it fails a criterion, write our own numba solver for exactly the part that failed.

### 7.3 Single-dummy play: sample, solve, vote

For a decision by declarer with knowledge `K`:

1. sample `S` layouts of the hidden hands consistent with `K` (voids, card counts, the auction likelihood), exactly distributed as the posterior;
2. solve each double-dummy, getting the value of every legal card;
3. play the card with the best score over the samples, ties among equivalent cards broken uniformly at random.

**Objective.** The *score* a card gets matters: the average number of tricks is the simple start, but the right objective for a specific contract is the **probability of making that contract** (this is what produces safety plays: give up an overtrick to guard against a bad split). With the per-sample values already in hand the change is only to use the indicator `tricks >= target` instead of the trick count, so plan for both and use the contract-specific one in the evaluator.

This "perfect-information Monte Carlo" plays finesses correctly whenever they are right on average, counts cards (through the sampler), and makes no mistakes in the sense above. Its known weakness is **strategy fusion**: each sample assumes declarer will later know where the cards are, so it can overvalue lines that need a guess. Mitigations: use the exact suit-combination solver whenever the position is a pure one-suit problem, and measure the loss by comparing the sampling player with the exact solver on single-suit positions before trusting it elsewhere.

### 7.4 Contract mechanics

`Round` has to learn the contract (level, strain, doubled), declarer and dummy: the opening lead by declarer's left-hand opponent, dummy shown after the lead, dummy played by declarer. The opening lead is the first decision of the defenders.

## 8. Card counting, precisely

Each player carries a `Knowledge` object, updated after every card:

* own hand, dummy (visible after the opening lead), every card played so far (by whom, in which trick);
* **voids**: a player who fails to follow suit is void in that suit;
* **unseen cards** per suit, and how many cards each hidden hand still holds (13 minus the cards played);
* the **vacant places** for each hidden hand: the slots that can still hold an unseen card of a given suit. The chance that a given unseen card is in a given hand is `vacant_places(hand) / total_vacant_places`, exact.

This is the **Hand rework** TODO in the map (a hand that remembers its original cards and what was played). Exact inference where it exists: priors over hidden hands are hypergeometric (`Probability.partner_suit_length_pmf`, `opponent_split_probabilities`, `partner_aces_pmf`); after voids and counts are known the remainder is again hypergeometric with the vacant places; restricted choice is a one-line Bayes update.

## 9. Modules and tests

| New module | Contents | Checked against |
|---|---|---|
| `Scoring` | duplicate score of a contract result, vulnerability, doubles | published scoring tables |
| `Contract` | level, strain, declarer, dummy, doubled | rules |
| `SuitCombinations` | exact solver of section 5, returns `P(k tricks)` | textbook probabilities (finesse 50%, 3-2 split 67.8%, restricted choice 2:1), brute-force enumeration of all worlds and all lines for small holdings |
| `Knowledge` | card counting, exact vacant-place probabilities, layout sampler | the hypergeometric formulas in `Probability`; **property test: a player's choice depends only on its information set** (swap unseen cards between hidden hands consistently with the information and the choice must not change; this is the test that nobody cheats) |
| `AuctionLikelihood` | `call_probabilities` interface, posterior sampling (sequential importance sampling, exact counting where possible) | exact counting on small constrained cases, effective-sample-size checks, rejection sampling on short auctions |
| `DoubleDummy` | adapter around DDS (or our solver if the spike fails) | brute-force minimax on small endings |
| `SingleDummy` | sampling player of section 7.3 | the exact suit-combination solver on single-suit positions; mean tricks never above double-dummy |
| `Evaluator` | outcome distributions, highest-met bid, the confusion matrix | par, known contracts, convergence under more samples |

All of it follows the project's habits: reference object code first, compiled code checked against it, seeds and thread-count independence, 100% branch coverage with numba kernels excluded and verified by equivalence tests.

## 10. Phases

| Phase | Deliverable | Size | Depends on |
|---|---|---|---|
| **P1** | `SuitCombinations`: the exact finesse / drop / restricted-choice solver with `P(k tricks)`, a notebook of the classic holdings | M | nothing (**first**) |
| P0 | prerequisites already on the map: `Hand` that tracks played and unseen cards, scoring, contract/declarer/dummy/opening lead in `Round`, explicit RNG plumbing | M | |
| P2 | **DDS spike**: prove criteria 1 to 5 of 7.2, then wrap it; brute-force oracle | S to M | |
| P3 | `Knowledge` and the layout sampler, plus the information-set property test | M | P0 |
| P4 | `SingleDummy` sampling player, contract-specific objective, strategy-fusion check against P1 | M | P2, P3 |
| P5 | `Evaluator` level B: outcome distributions per strain and declarer, highest-met bid, the **confusion matrix**, with a toy bidder | M | P4, scoring |
| P6 | `AuctionLikelihood` (section 6), then level C: per-call evaluation | L | P5, a bidding system |
| P7 | speed: harness over layouts and deals, caching solved positions by canonical form (suit relabelling) | M | P4 |

## 11. Where the other TODOs fit

* **Hand rework** (count cards): P0 and the basis of `Knowledge`.
* **Scoring and whole games:** `Scoring` is needed for the expected score; whole-game scoring (rubber, vulnerability rotation) can wait.
* **Multiprocessing harness (built) and RNG plumbing:** the repeated plays are embarrassingly parallel and reproducible by seed.
* **Integer engine (built, `FastRound`):** the faster baseline for plain play; the search engine (bitboards, DDS) is the next customer of the same idea.
* **Exact multivariate hypergeometric in PyMC:** the posterior over unseen cards and the auction likelihood are natural exact-likelihood uses.

## 12. Open questions that came out of the decisions

1. **"Met" as a distribution or a threshold?** Recommendation: the distribution of the highest met bid over layouts (section 3), with a thresholded view as a convenience. Agree?
2. **Declarer's objective:** maximize tricks first, then the probability of making the *specific* contract (safety plays)? Recommendation: both, using the contract-specific one in the evaluator.
3. **Which partner declares:** evaluate both and take the better, or the one the bidding would choose (the first to bid the strain)? Recommendation: both for "possible", the bidding's choice for judging a specific auction.
4. **Toy bidder** for the first confusion matrix: a points-to-contract rule? Which rule do you want to test first?
5. **Doubles and vulnerability** are ignored at first (undoubled, one fixed vulnerability): fine?
6. **Competition:** level B assumes the opponents pass; part of level C. Fine?

## 13. Risks

* **DDS fit:** the spike can fail a criterion (mid-play positions are the likely one); then we write our own solver for that part.
* **Strategy fusion** in the sampling player: quantified against the exact suit-combination solver before trusting it.
* **Likelihood model quality:** "bid correctness" is only as good as the model of what calls mean; the project's one bidder (`BeginningBidder`) is far too thin for level C. Level B does not need it.
* **Sampling cost and variance:** expected results need many layouts; use common random numbers (the same layouts for every candidate contract), exact conditioning where possible, and the harness.
