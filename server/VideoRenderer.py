import cv2

from model import compute, overlay

cap = cv2.VideoCapture('IMG_2115.mov')

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

output = cv2.VideoWriter('output.mov', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (852, 480), True)

counter = 0
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mapped_frame, left, right, *_ = compute(frame)

        left = cv2.resize(left, (frame.shape[1], frame.shape[0]))
        right = cv2.resize(right, (frame.shape[1], frame.shape[0]))

        colored = overlay(frame, left, right)
        colored = cv2.cvtColor(colored, cv2.COLOR_RGBA2BGR)

        output.write(colored)
    else:
        print('OOPS I BROKE OUCHIE')
        break
    counter += 1
    # if counter == 120: break

cap.release()
output.release()
cv2.destroyAllWindows()

