import math
import torch
import numpy as np
import heapq as hq
import cv2

MIN_GAP = 25
BUFFER = 2
DEPTH_CAP = 30
WIDTH_CAP = 40
VERTICAL_BLUR = 15
HIT_DEPTH = 500
HIT_DANGER = 900

# model_type = "DPT_Large"     # MiDaS v3 - Large     (highest accuracy, slowest inference speed)
# model_type = "DPT_Hybrid"   # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed)
model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)

midas = torch.hub.load("intel-isl/MiDaS", model_type)

device = torch.device("cuda") if torch.cuda.is_available() else (torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu"))
midas.to(device)
midas.eval()

midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform


def __calc_danger_val(width, depth):
    return min(WIDTH_CAP, width) * min(DEPTH_CAP, depth)


kernel1 = np.full((1, VERTICAL_BLUR), 1 / VERTICAL_BLUR)
def compute(img):
    # start = time()
    
    # contrast = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    # lc, ac, bc = cv2.split(contrast)

    # clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    # nlc = clahe.apply(lc)

    # img = cv2.cvtColor(cv2.merge((nlc, ac, bc)), cv2.COLOR_LAB2RGB)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    input_batch = transform(img).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)

    u_depth = prediction.cpu().numpy()[0]

    depth = cv2.filter2D(src=u_depth, ddepth=-1, kernel=kernel1)
    r = math.ceil(depth.max())
    # depth *= NORMALIZED_SIZE / r

    danger_levels_left = np.zeros(shape=(r+1, 3))
    danger_levels_right = np.zeros(shape=(r+1, 3))
    danger_image_left = np.zeros(shape=depth.shape)
    danger_image_right = np.zeros(shape=depth.shape)
    hit_image_left = np.zeros(shape=depth.shape)
    hit_image_right = np.zeros(shape=depth.shape)

    hit_left = 0
    hit_right = 0

    lp = depth.shape[1] // 4
    hp = depth.shape[1] - lp
    # mid = time()
    for y in range(depth.shape[0]):
        dang_drop = []
        for x in range(lp, depth.shape[1]+1):
            depth_cutoff = depth[y][x] - MIN_GAP if x < depth.shape[1] else -1
            if x - BUFFER >= 0:
                buffer_depth = depth[y][x - BUFFER]
                if buffer_depth <= depth_cutoff:
                    hq.heappush(dang_drop, (-buffer_depth, x - BUFFER))
            while dang_drop and -dang_drop[0][0] > depth_cutoff:
                hv, fx = hq.heappop(dang_drop)
                dep = depth[y][fx + BUFFER]
                val = __calc_danger_val(x - fx, dep + hv)
                if val >= HIT_DANGER and dep >= HIT_DEPTH:
                    hit_left += 1
                    hit_image_left[y][fx] = 1
                danger_image_left[y][fx] = val
                if danger_levels_left[int(dep)][0] < val:
                    danger_levels_left[int(dep)] = np.array([val, fx, y])
        for x in range(hp, -2, -1):
            depth_cutoff = depth[y][x] - MIN_GAP if x > -1 else -1
            if x + BUFFER < depth.shape[1]:
                buffer_depth = depth[y][x + BUFFER]
                if buffer_depth <= depth_cutoff:
                    hq.heappush(dang_drop, (-buffer_depth, x + BUFFER))
            while dang_drop and -dang_drop[0][0] > depth_cutoff:
                hv, fx = hq.heappop(dang_drop)
                dep = depth[y][fx - BUFFER]
                val = __calc_danger_val(fx - x, dep + hv)
                if val >= HIT_DANGER and dep >= HIT_DEPTH:
                    hit_right += 1
                    hit_image_right[y][fx] = 1
                danger_image_right[y][fx] = val
                if danger_levels_right[int(dep)][0] < val:
                    danger_levels_right[int(dep)] = np.array([val, fx, y])

    out_danger_from_left = []
    out_danger_from_right = []
    c_l, c_r = 0, 0
    for j in range(r, -1, -1):
        if danger_levels_left[j][0] > c_l:
            c_l = danger_levels_left[j][0]
            out_danger_from_left.append((j, c_l, danger_levels_left[j][1], danger_levels_left[j][2]))
        if danger_levels_right[j][0] > c_r:
            c_r = danger_levels_right[j][0]
            out_danger_from_right.append((j, c_r, danger_levels_right[j][1], danger_levels_right[j][2]))
    # end = time()
    return u_depth, danger_image_left, danger_image_right, out_danger_from_left, out_danger_from_right, hit_left, hit_right, hit_image_left, hit_image_right