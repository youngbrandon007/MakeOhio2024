import math

import cv2
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from model import compute
import numpy as np

img = cv2.imread(f'images/wallpng.png')

depth, image_left, image_right, from_left, from_right, hit_left, hit_right, hil, hir = compute(img)
depth = depth / 5
depth = cv2.resize(depth, dsize=(64, 128), interpolation=cv2.INTER_CUBIC)

ogFrame = cv2.cvtColor(cv2.resize(img, (depth.shape[1], depth.shape[0])), cv2.COLOR_BGR2RGBA)

print(depth.shape)
D_X, D_Y = np.meshgrid(np.linspace(0, depth.shape[0], depth.shape[1]), np.linspace(0, depth.shape[1], depth.shape[0]))

D_X = D_X.flatten()
D_Y = D_Y.flatten()
D_Z = depth.flatten()
D_C = ogFrame.reshape((-1, 4)) / 255.0
fig = plt.figure()
sp = None


plt.axis('off')
plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
            hspace = 0, wspace = 0)

def gen_plane(p1a, p1b, p2a, p2b, pc, d, ord):
    AA, BB = np.meshgrid(np.linspace(p1a, p2a, int(abs(p1a - p2a) * d)), np.linspace(p1b, p2b, int(abs(p1b - p2b) * d)))
    AA = AA.flatten()
    BB = BB.flatten()
    CC = np.full(len(AA), pc)
    if ord == "xy":
        return AA, BB, CC
    elif ord == "yz":
        return CC, AA, BB
    elif ord == "xz":
        return AA, CC, BB


x1, y1, z1, x2, y2, z2, d = 70, 25, 100, 125, 45, 240, 1
R_X, R_Y, R_Z = zip(
    gen_plane(x1, y1, x2, y2, z1, d, "xy"),
    gen_plane(x1, y1, x2, y2, z2, d, "xy"),

    gen_plane(x1, z1, x2, z2, y1, d, "xz"),
    gen_plane(x1, z1, x2, z2, y2, d, "xz"),

    gen_plane(y1, z1, y2, z2, x1, d, "yz"),
    gen_plane(y1, z1, y2, z2, x2, d, "yz"),

)
R_X = np.concatenate((*R_X,))
R_Y = np.concatenate((*R_Y,))
R_Z = np.concatenate((*R_Z,))

mv = depth.max()
ALT_D_C = plt.cm.viridis(D_Z / mv)

def easeInOutSine(t):
    import math
    return -(math.cos(math.pi * t) - 1) / 2


def step(i):
    global time, sp
    alpha = easeInOutSine(min(90, max(0, i - 60)) / 90)
    alpha2 = easeInOutSine(min(20, max(0, i - 20)) / 20)
    beta = easeInOutSine(max(0, min(45, i - 150)) / 45)
    beta2 = easeInOutSine(min(20, max(0, i - 120)) / 20)
    if i < 120:
        fig.clf()
        sp = fig.add_subplot(111, projection='3d')
        if i < 20:
            sp.scatter(D_X, D_Y, D_Z, c=D_C)
        else:
            sp.scatter(D_X, D_Y, D_Z, c=D_C*(1-alpha2)+ALT_D_C*alpha2)
        sp.set_axis_off()
        sp.set_proj_type('ortho')
    else:
        fig.clf()
        sp = fig.add_subplot(111, projection='3d')
        sp.scatter(
            np.concatenate((D_X,R_X)),
            np.concatenate((D_Y,R_Y+(1-beta)*20)),
            np.concatenate((D_Z,R_Z)),
            c=np.concatenate((D_C*beta2+ALT_D_C*(1-beta2),np.full((len(R_X), 4), [0.0, 0.0, 1.0, beta]))))
        sp.set_axis_off()
        sp.set_proj_type('ortho')
    sp.view_init(elev=90 - alpha * 55, azim=90 + 100 * alpha, roll=90*alpha)
    return sp


an = animation.FuncAnimation(fig, step, frames=range(240), interval=1, blit=False, repeat=False)

# FOR SAVING
aw = animation.PillowWriter(fps=15, bitrate=1800)
an.save('scatter5.gif', writer=aw)

# FOR PREVIEWING
# plt.show()
