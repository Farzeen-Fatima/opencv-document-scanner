"""
Polygon Interacter — Manual Corner Selection
Click 4 corners of document, press C to crop and save.
"""

import cv2
import numpy as np
import argparse
import os
from transform import four_point_transform


MAX_DIM = 800

points = []
display = None
original = None
scale = 1.0

def resize_for_display(image):
    h, w = image.shape[:2]
    if max(h, w) <= MAX_DIM:
        return image, 1.0
    s = MAX_DIM / max(h, w)
    return cv2.resize(image, (int(w * s), int(h * s))), s

def draw(img):
    canvas = img.copy()
    colours = [(0,255,0),(0,255,255),(0,165,255),(0,0,255)]
    labels  = ["TL","TR","BR","BL"]
    for i, pt in enumerate(points):
        cv2.circle(canvas, pt, 6, colours[i], -1)
        cv2.putText(canvas, labels[i], (pt[0]+8, pt[1]-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, colours[i], 2)
    if len(points) == 4:
        pts = np.array(points, np.int32)
        cv2.polylines(canvas, [pts], True, (0,255,0), 2)
    remaining = 4 - len(points)
    msg = (f"Click {remaining} more corner(s)" if remaining > 0
           else "Press [C] to crop  [R] to reset  [Q] to quit")
    cv2.putText(canvas, msg, (10, canvas.shape[0]-12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2)
    return canvas

def on_mouse(event, x, y, flags, param):
    global points, display
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
        points.append((x, y))
        cv2.imshow("Scanner", draw(display))

def main():
    global points, display, original, scale

    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    args = ap.parse_args()

    original = cv2.imread(args.image)
    if original is None:
        print(f"Cannot load image: {args.image}")
        return

    display, scale = resize_for_display(original)

    cv2.namedWindow("Scanner")
    cv2.setMouseCallback("Scanner", on_mouse)
    cv2.imshow("Scanner", draw(display))

    while True:
        key = cv2.waitKey(20) & 0xFF

        if key == ord('r'):
            points = []
            cv2.imshow("Scanner", draw(display))

        elif key == ord('c'):
            if len(points) == 4:
                orig_pts = np.array(points, dtype="float32") / scale
                cropped = four_point_transform(original, orig_pts)
                cropped_display, _ = resize_for_display(cropped)
                cv2.imshow("Cropped Result", cropped_display)
                base = os.path.splitext(os.path.basename(args.image))[0]
                save_path = f"{base}_cropped.jpg"
                cv2.imwrite(save_path, cropped)
                print(f"\n✅ Saved to: {save_path}")
                print("Press any key to close.")
                cv2.waitKey(0)
                break
            else:
                print(f"Need 4 points — you have {len(points)}.")

        elif key == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()