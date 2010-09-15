from __future__ import division

import deck
from hand import hand
import matplotlib.pyplot as plt
import numpy

# create a deck
d = deck.deck()


balanced = []
points = []

num = int(5e4)
steps = num // 10
for i in range(num):
    if (i+1) % steps == 0:
        print("%d of %d" % (i+1, num))
    d.shuffle(7)
    d.cut()
    h1 = hand(d.deal()[0])
    h2 = hand(d.deal()[1])
    h3 = hand(d.deal()[2])
    h4 = hand(d.deal()[3])
    balanced.append([h1.balanced,
                     h2.balanced,
                     h3.balanced,
                     h4.balanced])
    points.append([h1.hc_points,
                   h2.hc_points,
                   h3.hc_points,
                   h4.hc_points])

fig=plt.figure()
ax=fig.add_subplot(111)
ax.hist(balanced)
ax.set_title('%d hands' % (num))
ax.set_ylabel('Number of hands')
ax.set_xticks([0., 1.])
ax.set_xticklabels(['Unbalanced', 'balanced'])
plt.draw()

points = numpy.array(points)

fig=plt.figure()
ax=fig.add_subplot(111)
ax.hist(points.flat, range(points.max()-points.min()), normed=True, cumulative=False)
ax.set_title('%d hands' % (num))
ax.set_ylabel('Fractional occurance')
ax.set_xlabel('High card points')
ax.axvline(13, lw=2, color='r')
plt.draw()



fig=plt.figure()
ax=fig.add_subplot(111)
ax.hist(points.flat, range(max(points)-min(points)), normed=True, cumulative=True)
ax.set_title('%d hands' % (num))
ax.set_ylabel('Cumulative occurance')
ax.set_xlabel('High card points')
ax.axvline(13, lw=2, color='r')
plt.draw()


    


