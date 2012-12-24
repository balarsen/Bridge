from __future__ import division

import deck
import matplotlib.pyplot as plt
import numpy

# create a deck
d = deck.deck()


balanced = []
points = []

num = int(1e4)
steps = num // 10
for i in range(num):
    if (i+1) % steps == 0:
        print("%d of %d" % (i+1, num))
    d.shuffle(7)
    d.cut()
    h1, h2, h3, h4 = d.deal()
    balanced.append([h1.balanced,
                     h2.balanced,
                     h3.balanced,
                     h4.balanced])
    points.append([h1.hc_points,
                   h2.hc_points,
                   h3.hc_points,
                   h4.hc_points])
balanced = zip(*balanced)

fig=plt.figure()
ax=fig.add_subplot(111)
ax.hist(balanced[0])
ax.set_title('%d hands' % (num))
ax.set_ylabel('Number of hands')
ax.set_xticks([0., 1.])
ax.set_xticklabels(['Unbalanced', 'balanced'])

1/0

# scatter, if I am balanced is my partner?
# these need ot be counted !!!
cnt = numpy.histogram2d(balanced[0], balanced[2])[0]

fig=plt.figure()
ax=fig.add_subplot(111)
ax.scatter(balanced[0], balanced[2])
ax.set_title('%d hands' % (num))
ax.set_ylabel('Number of hands')
ax.set_xticks([0., 1.])
ax.set_xticklabels(['Unbalanced', 'balanced'])
ax.set_yticks([0., 1.])
ax.set_yticklabels(['Unbalanced', 'balanced'])


1/0

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





