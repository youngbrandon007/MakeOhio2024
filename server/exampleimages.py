import math

import cv2
import matplotlib.pyplot as plt
import numpy as np
from model import compute


def draw_scatter(figure, dang):
    xs, ys = zip(*dang)
    sct = figure.scatter(x=xs, y=ys, c=xs, vmin=0, vmax=500)
    figure.set_xlim(0, 500)
    figure.set_ylim(0, 1500)
    return sct

def draw_image(figure, img):
    im = figure.imshow(img)
    figure.set_axis_off()
    return im

if __name__ == "__main__":
    img_names = ['1corner.png', '2corner.png', 'bridge.png', 'tunnel.png', 'generic.png']
    imgs = list(cv2.cvtColor(cv2.imread(f'images/{f}'), cv2.COLOR_BGR2RGB) for f in img_names)

    fig, ax = plt.subplots(max(2, len(imgs)), 6)
    
    for i in range(len(imgs)):
        img = imgs[i]
        depth, image_left, image_right, from_left, from_right, left_hit, right_hit = compute(img)
        draw_image(ax[i][0], img)
        draw_image(ax[i][1], depth)
        draw_image(ax[i][2], image_left)
        draw_image(ax[i][3], image_right)
        draw_scatter(ax[i][4], from_left)
        draw_scatter(ax[i][5], from_right)
    plt.show()
