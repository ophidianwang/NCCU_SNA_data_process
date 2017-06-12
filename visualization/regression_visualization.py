# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np


x = np.linspace(-3, 5, 100)
y = x / 2 + 1

pt_x = np.random.rand(80) * 8 - 3
pt_y = pt_x / 2 + 1
pt_noise = np.random.normal(0, .3, 80)
pt_y += pt_noise

fig, ax = plt.subplots()
line1, = ax.plot(x, y, '-', linewidth=2, label='Regression', c='r')
ax.scatter(pt_x, pt_y, label='Samples')
ax.set_xlabel('X')
ax.set_ylabel('Y')

ax.legend(loc='lower right')
ax.grid(True)
plt.show()
