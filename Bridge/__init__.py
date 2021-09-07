suits = {'spades':1,
         'hearts':2,
         'diamonds':3,
         'clubs':4,
         'notrump':5}
tmp = dict( (val[1], val[0]) for val in suits.items())
suits.update(tmp)

positions = ['North', 'East', 'South', 'West']

values = {'two':2,
          'three':3,
          'four':4,
          'five':5,
          'six':6,
          'seven':7,
          'eight':8,
          'nine':9,
          'ten':10,
          'jack':11,
          'queen':12,
          'king':13,
          'ace': 14}
tmp = dict( (val[1], val[0]) for val in values.items())
values.update(tmp)
