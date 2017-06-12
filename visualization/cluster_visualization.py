# -*- coding: utf-8 -*-

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

num_1 = 20
num_2 = 30
num_3 = 15

cluster_1_x = np.random.normal(5, 0.5, num_1)
cluster_1_y = np.random.normal(3, 0.5, num_1)
cluster_1_z = np.random.normal(4, 0.5, num_1)

cluster_2_x = np.random.normal(5, 0.5, num_2)
cluster_2_y = np.random.normal(3, 0.5, num_2)
cluster_2_z = np.random.normal(1, 0.5, num_2)

cluster_3_x = np.random.normal(1, 0.5, num_3)
cluster_3_y = np.random.normal(1, 0.5, num_3)
cluster_3_z = np.random.normal(2.5, 0.5, num_3)

x = np.concatenate((cluster_1_x, cluster_2_x, cluster_3_x))
y = np.concatenate((cluster_1_y, cluster_2_y, cluster_3_y))
z = np.concatenate((cluster_1_z, cluster_2_z, cluster_3_z))
print(x)
print(y)
print(z)

c_list = ['r']*num_1 + ['g']*num_2 + ['b']*num_3
print(c_list)


# fig = plt.figure(figsize=plt.figaspect(2.))
inv_h, inv_w = plt.figaspect(2.)
fig = plt.figure(figsize=(inv_w, inv_h))
fig.suptitle('more dimension, learn deeper')

# first figure
ax = fig.add_subplot(1, 2, 1)
ax.scatter(x, y, c=c_list)
ax.legend()
ax.set_xlim(0, 6)
ax.set_ylim(0, 6)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.grid(True)

# second figure
ax = fig.add_subplot(1, 2, 2, projection='3d')
ax.scatter(x, y, z, c=c_list)

# Make legend, set axes limits and labels
ax.legend()
ax.set_xlim(0, 6)
ax.set_ylim(0, 6)
ax.set_zlim(0, 6)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Customize the view angle so it's easier to see that the scatter points lie
# on the plane y=0
ax.view_init(elev=20., azim=-35)

plt.show()
