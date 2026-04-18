import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import io
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from scipy.spatial import distance as dist

st.set_page_config(page_title="Document Scanner", page_icon="📄", layout="centered")

# ── Helper functions built in ──────────────────────────────────────────────────

def resize(image, height):
    (h, w) = image.shape[:2]
    r = height / float(h)
    dim = (int(w * r), height)
    return cv2.resize(image, dim)

def order_points(pts):
    xSorted = pts[np.argsort(pts[:, 0]), :]
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost
    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]
    return np.array([tl, tr, br, bl], dtype="float32")

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0]-bl[0])**2)+((br[1]-bl[1])**2))
    widthB = np.sqrt(((tr[0]-tl[0])**2)+((tr[1]-tl[1])**2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0]-br[0])**2)+((tr[1]-br[1])**2))
    heightB = np.sqrt(((tl[0]-bl[0])**2)+((tl[1]-bl[1])**2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([[0,0],[maxWidth-1,0],[maxWidth-1,maxHeight-1],[0,maxHeight-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

def preprocess_for_edge_detection(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return cv2.Canny(blurred, 75, 200)

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
        enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, blockSize=21, C=10)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    elif mode == "grayscale":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return cv2.cvtColor(clahe.apply(gray), cv2.COLOR_GRAY2BGR)
    elif mode == "color":
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    return image

def scan_image(pil_image, enhancement_mode="adaptive"):
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
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
        detected = True
    else:
        warped = orig
        detected = False
    enhanced = enhance_document(warped, mode=enhancement_mode)
    return Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)), detected

def images_to_pdf_bytes(pil_images):
    pdf_buffer = io.BytesIO()
    c = rl_canvas.Canvas(pdf_buffer, pagesize=A4)
    a4_w, a4_h = A4
    tmp_dir = tempfile.gettempdir()
    for i, pil_img in enumerate(pil_images):
        tmp_path = os.path.join(tmp_dir, f"scan_{i}.jpg")
        pil_img.save(tmp_path, "JPEG", quality=95)
        img_w, img_h = pil_img.size
        margin = 20
        scale = min((a4_w - 2*margin) / img_w, (a4_h - 2*margin) / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale
        x = (a4_w - draw_w) / 2
        y = (a4_h - draw_h) / 2
        c.drawImage(tmp_path, x, y, width=draw_w, height=draw_h)
        c.showPage()
        os.remove(tmp_path)
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

FILENAME_HINTS = {
    "eyeshadow": "color", "palette": "color", "photo": "color",
    "handwritten": "grayscale", "notes": "grayscale", "notepad": "grayscale",
}

def pick_mode(filename):
    name = filename.lower()
    for keyword, m in FILENAME_HINTS.items():
        if keyword in name:
            return m
    return "adaptive"

# ── UI ─────────────────────────────────────────────────────────────────────────

st.title("📄 Document Scanner")
st.caption("Upload images · Auto-detect edges · Download scanned PDF")
st.markdown("---")

uploaded_files = st.file_uploader(
    "Upload your images",
    type=["jpg", "jpeg", "png", "bmp"],
    accept_multiple_files=True
)

mode = st.selectbox(
    "Enhancement Mode",
    options=["auto", "adaptive", "grayscale", "color"],
    format_func=lambda x: {
        "auto":      "🤖 Auto",
        "adaptive":  "⬛ Adaptive — B&W text",
        "grayscale": "🩶 Grayscale — handwritten notes",
        "color":     "🌈 Color — photos"
    }[x]
)

st.markdown("---")

if uploaded_files:
    st.markdown(f"**{len(uploaded_files)} image(s) ready**")

    if st.button("🔍 Scan & Generate PDF"):
        scanned_pages = []
        statuses = []
        progress = st.progress(0)

        for i, uploaded_file in enumerate(uploaded_files):
            pil_image = Image.open(uploaded_file).convert("RGB")
            selected_mode = pick_mode(uploaded_file.name) if mode == "auto" else mode
            scanned, detected = scan_image(pil_image, enhancement_mode=selected_mode)
            scanned_pages.append(scanned)
            statuses.append((uploaded_file.name, detected))
            progress.progress((i + 1) / len(uploaded_files))

        progress.empty()

        st.markdown("### ✅ Results")
        for name, detected in statuses:
            if detected:
                st.success(f"✓ {name} — edges detected & corrected")
            else:
                st.warning(f"⚠ {name} — no border found, used full image")

        st.markdown("### 👀 Preview")
        cols = st.columns(min(len(scanned_pages), 3))
        for i, (page, col) in enumerate(zip(scanned_pages, cols)):
            with col:
                st.image(page, caption=f"Page {i+1}", use_container_width=True)

        with st.spinner("Building PDF..."):
            pdf_bytes = images_to_pdf_bytes(scanned_pages)

        st.download_button(
            label="⬇ Download Scanned PDF",
            data=pdf_bytes,
            file_name="scanned_document.pdf",
            mime="application/pdf"
        )
else:
    st.info("👆 Upload images above to get started")

st.markdown("---")
st.caption("Built with OpenCV · ReportLab · Streamlit")