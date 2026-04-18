import sys
import os
import tempfile
import argparse
import cv2
import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from imutils import resize
from transform import four_point_transform

def preprocess_for_edge_detection(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    return edged

def find_document_contour(edged):
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            return approx
    return None

def enhance_document(image, mode="adaptive"):
    if mode == "adaptive":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=21, C=10)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    elif mode == "grayscale":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    elif mode == "color":
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return image

def scan_image(image_path, enhancement_mode="adaptive"):
    print(f"  Processing: {os.path.basename(image_path)}")
    image = cv2.imread(image_path)
    if image is None:
        print(f"  [WARNING] Could not load image: {image_path}")
        return None
    h, w = image.shape[:2]
    if max(h, w) > 1000:
        scale = 1000 / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)))
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    small = resize(image, height=500)
    edged = preprocess_for_edge_detection(small)
    contour = find_document_contour(edged)
    if contour is not None:
        contour_scaled = contour.reshape(4, 2) * ratio
        warped = four_point_transform(orig, contour_scaled)
        print(f"    ✓ Document edges detected – perspective corrected")
    else:
        print(f"    ⚠ No clear document border – using full image")
        warped = orig
    enhanced = enhance_document(warped, mode=enhancement_mode)
    return enhanced

def images_to_pdf(cv2_images, output_path):
    pil_images = []
    for img in cv2_images:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_images.append(Image.fromarray(rgb))
    if not pil_images:
        print("[ERROR] No images to save.")
        return
    c = rl_canvas.Canvas(output_path, pagesize=A4)
    a4_w, a4_h = A4
    tmp_dir = tempfile.gettempdir()
    for i, pil_img in enumerate(pil_images):
        tmp_path = os.path.join(tmp_dir, f"scanned_page_{i}.jpg")
        pil_img.save(tmp_path, "JPEG", quality=95)
        img_w, img_h = pil_img.size
        margin = 20
        max_w = a4_w - 2 * margin
        max_h = a4_h - 2 * margin
        scale = min(max_w / img_w, max_h / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale
        x = (a4_w - draw_w) / 2
        y = (a4_h - draw_h) / 2
        c.drawImage(tmp_path, x, y, width=draw_w, height=draw_h)
        c.showPage()
        os.remove(tmp_path)
    c.save()
    print(f"\n✅ PDF saved to: {output_path}")

FILENAME_HINTS = {
    "eyeshadow": "color", "palette": "color", "colour": "color",
    "color": "color", "photo": "color",
    "handwritten": "grayscale", "notes": "grayscale", "notepad": "grayscale",
}

def pick_mode(image_path):
    name = os.path.basename(image_path).lower()
    for keyword, mode in FILENAME_HINTS.items():
        if keyword in name:
            return mode
    return "adaptive"

def parse_args():
    ap = argparse.ArgumentParser(description="CamScanner-style document scanner")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--images", nargs="+")
    group.add_argument("--folder")
    ap.add_argument("--output", default="scanned_document.pdf")
    ap.add_argument("--mode", choices=["adaptive", "grayscale", "color", "auto"], default="auto")
    return ap.parse_args()

def collect_image_paths(args):
    if args.images:
        return args.images
    exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    paths = sorted([
        os.path.join(args.folder, f)
        for f in os.listdir(args.folder)
        if f.lower().endswith(exts)
    ])
    return paths

def main():
    args = parse_args()
    image_paths = collect_image_paths(args)
    if not image_paths:
        print("[ERROR] No images found.")
        sys.exit(1)
    print(f"\n📄 Document Scanner — processing {len(image_paths)} image(s)\n")
    scanned_pages = []
    for path in image_paths:
        mode = args.mode if args.mode != "auto" else pick_mode(path)
        result = scan_image(path, enhancement_mode=mode)
        if result is not None:
            scanned_pages.append(result)
    if scanned_pages:
        images_to_pdf(scanned_pages, args.output)
    else:
        print("[ERROR] No pages were successfully processed.")
        sys.exit(1)

if __name__ == "__main__":
    main()