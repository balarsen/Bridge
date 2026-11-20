"""
Duplicate bridge scoring of one hand.

`score(contract, tricks, vulnerable)` is the score for the declaring side: positive if the contract is
made, negative if it goes down.  `tricks` is the number of tricks declarer's side took (0 to 13).
"""
from .Contract import Contract

MINORS = ('clubs', 'diamonds')


def trick_points(strain, tricks):
    """points for `tricks` tricks bid and made in `strain`, before doubling: 20 a trick in a minor, 30 in a
    major, 40 for the first notrump and 30 for the rest"""
    if tricks <= 0:
        return 0
    if strain == 'notrump':
        return 40 + 30 * (tricks - 1)
    return tricks * (20 if strain in MINORS else 30)


def undertrick_penalty(down, vulnerable, doubled):
    """what declarer loses for going down `down` tricks"""
    if doubled == 0:
        return down * (100 if vulnerable else 50)
    if vulnerable:
        penalty = 200 + 300 * (down - 1)
    else:
        penalty = 100 * min(down, 1) + 200 * max(min(down, 3) - 1, 0) + 300 * max(down - 3, 0)
    return penalty * doubled  # redoubled is twice as much


def score(contract, tricks, vulnerable=False):
    """the score for the side that declares `contract` after taking `tricks` tricks"""
    if not isinstance(contract, Contract):
        raise TypeError('contract must be a Contract')
    if not 0 <= tricks <= 13:
        raise ValueError('tricks must be between 0 and 13')
    multiplier = (1, 2, 4)[contract.doubled]
    if tricks < contract.tricks_needed:
        return -undertrick_penalty(contract.tricks_needed - tricks, vulnerable, contract.doubled)

    contract_points = trick_points(contract.strain, contract.level) * multiplier
    total = contract_points
    # bonus for making game (100 or more contract points) or just a part score
    total += (500 if vulnerable else 300) if contract_points >= 100 else 50
    if contract.level == 6:
        total += 750 if vulnerable else 500
    elif contract.level == 7:
        total += 1500 if vulnerable else 1000
    total += 50 * contract.doubled  # for making a doubled (50) or redoubled (100) contract
    over = tricks - contract.tricks_needed
    if contract.doubled:
        total += over * (200 if vulnerable else 100) * contract.doubled
    else:
        total += trick_points(contract.strain, over) if contract.strain != 'notrump' else 30 * over
    return total


def ns_score(contract, tricks, vulnerable=False):
    """the same score from north-south's point of view"""
    s = score(contract, tricks, vulnerable)
    return s if contract.side == 'ns' else -s
