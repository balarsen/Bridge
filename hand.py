

class hand(list):
    """
    needs to build from a deck, get cards, know how many there are and collect points
    """
    def __init__(self, c):
        self.cards = c
        # careful here only one hard per call
        self.n_cards = self.cards.shape[0]
        self.get_hc_points()
        self.n_suits()
        self.is_balanced()

    def __str__(self):
        self.sort()
        lst = [val for val in self.cards]
        return str(lst)

    __repr__ = __str__


    def get_hc_points(self):
        tmp = sum([val._hc for val in self.cards])
        self.hc_points = tmp

    def n_suits(self):
        suits = [val.suit for val in self.cards]
        distro = {'spades':suits.count('spades'),
                  'hearts':suits.count('hearts'),
                  'diamonds':suits.count('diamonds'),
                  'clubs':suits.count('clubs')}
        self.distro = distro

    def is_balanced(self):
        """
        count the number of each suit looking for balanced hands
        balanced hands are 4,3,3,3  5,3,3,2  4,4,3,2
        """
        tmp = self.distro.values()
        tmp.sort()
        bal = [tmp == [2,3,4,4],
               tmp == [2,3,3,5],
               tmp == [3,3,3,4]]
        if any(bal):
            self.balanced = True
        else:
            self.balanced = False



        
        


