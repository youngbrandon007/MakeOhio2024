import math

from time import time

import cv2
import torch

import matplotlib.pyplot as plt
import numpy as np
import heapq as hq

MIN_GAP = 25
BUFFER = 4
                                                                                       
DEPTH_CAP = 40
WIDTH_CAP = 40

# model_type = "DPT_Large"     # MiDaS v3 - Large     (highest accuracy, slowest inference speed)
# model_type = "DPT_Hybrid"   # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed)
model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)

midas = torch.hub.load("intel-isl/MiDaS", model_type)

device = torch.device("cuda") if torch.cuda.is_available() else (torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu"))

print(f'Using {device} for compute.')
midas.to(device)
midas.eval()

midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform

def createVisuals(img):
    
    pass

def compute(img):
    # start = time()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    input_batch = transform(img).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)

    depth = prediction.cpu().numpy()[0]
    r = depth.max()

    danger_l = np.zeros(shape=(math.ceil(r),))
    danger_r = np.zeros(shape=(math.ceil(r),))

    # mid = time()
    for y in range(depth.shape[0]):
        dang_drop = []
        for x in range(depth.shape[1]):
            cv = depth[y][x] - MIN_GAP
            if x - BUFFER >= 0 and depth[y][x-BUFFER] <= cv:
                hq.heappush(dang_drop, (-depth[y][x-BUFFER], x-BUFFER))
            while len(dang_drop) and -dang_drop[0][0] > cv:
                hv, fx = hq.heappop(dang_drop)
                dep = depth[y][fx+BUFFER]
                val = min(WIDTH_CAP, x - fx) * min(DEPTH_CAP, dep+hv)
                danger_l[int(dep)] = max(danger_l[int(dep)], val)
        while dang_drop:
            hv, fx = hq.heappop(dang_drop)
            dep = depth[y][fx+BUFFER]
            val = min(WIDTH_CAP, depth.shape[1] - fx) * min(DEPTH_CAP, dep+hv)
            danger_l[int(dep)] = max(danger_l[int(dep)], val)
        for x in range(depth.shape[1]-1,-1,-1):
            cv = depth[y][x] - MIN_GAP
            if x + BUFFER < depth.shape[1] and depth[y][x+BUFFER] <= cv:
                hq.heappush(dang_drop, (-depth[y][x+BUFFER], x+BUFFER))
            while len(dang_drop) and -dang_drop[0][0] > cv:
                hv, fx = hq.heappop(dang_drop)
                dep = depth[y][fx-BUFFER]
                val = min(WIDTH_CAP, fx - x) * min(DEPTH_CAP, dep+hv)
                danger_r[int(dep)] = max(danger_r[int(dep)], val)
        while dang_drop:
            hv, fx = hq.heappop(dang_drop)
            dep = depth[y][fx-BUFFER]
            val = min(WIDTH_CAP, fx) * min(DEPTH_CAP, dep+hv)
            danger_r[int(dep)] = max(danger_r[int(dep)], val)

    out_l = [
         # (danger_l.shape[0],0)
        ]
    out_r = [
         # (danger_r.shape[0],0)
        ]
    c_l, c_r = 0, 0
    for j in range(len(danger_l)-1,-1,-1):
        if danger_l[j] and danger_l[j] > c_l:
            c_l = danger_l[j]
            out_l.append((j, c_l))
        if danger_r[j] and danger_r[j] > c_r:
            c_r = danger_r[j]
            out_r.append((j, c_r))
    # out_l.append((0, c_l))
    # out_r.append((0, c_r))

    # end = time()
    
    # print(f'| Total Time: {end - start:.3f}s | MiDaS: {mid - start:.3f}s | Edge detection: {end - mid:.3f}s |')
    return depth, out_l, out_r



if __name__ == "__main__":
    img_names = ['1corner.png', '2corner.png', 'bridge.png', 'tunnel.png', 'generic.png']
    
    imgs = list(cv2.cvtColor(cv2.imread("test_images/" + f), cv2.COLOR_BGR2RGB) for f in img_names)

    fig, ax = plt.subplots(max(2, len(imgs)), 4)
    
    for i in range(len(imgs)):
        img = imgs[i]
        res, dang_l, dang_r = compute(img)

        ax[i][0].imshow(img)
        ax[i][1].imshow(res)
        def f(dang,p):
            xs, ys = zip(*dang)
            ax[i][p].scatter(x=xs, y=ys, c=xs)
        f(dang_r, 2)
        f(dang_l, 3)
    plt.show()
