# 📄 OpenCV Document Scanner

A CamScanner-style document scanner built with Python, OpenCV, and Streamlit.  
Upload images → auto-detect edges → perspective correct → download as PDF.

---

## 🎥 Demo
![Demo](demo.gif)

## ✨ Features

- 📤 Upload multiple images directly in the browser
- 🔍 Auto-detects document edges using OpenCV
- 📐 Perspective correction — straightens tilted documents
- 🎨 Three enhancement modes:
  - **Adaptive** — clean black & white for text documents
  - **Grayscale** — for handwritten notes
  - **Color** — for photos and colorful images
- 👀 Preview all scanned pages before downloading
- 📥 One-click PDF download
- 🖱️ Manual corner selection tool (polygon_interacter.py)

## 🎨 Enhancement Modes

| Mode | Best For | Example |
|------|----------|---------|
| `adaptive` | Text documents, books | bookpage.jpeg |
| `grayscale` | Handwritten notes | handwrittennotes.jpeg |
| `color` | Photos, colorful images | eyeshadowpalatte.jpeg |
| `auto` | Auto-picks based on filename | any |


## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `opencv-python-headless` | Image processing & edge detection |
| `scipy` | Euclidean distance for point ordering |
| `Pillow` | Image format conversion |
| `reportlab` | PDF generation |
| `numpy` | Array & matrix operations |
| `streamlit` | Web app interface |
## 🖱️ Manual Corner Selection

When automatic edge detection fails (⚠ warning), use the manual tool:
![Manual Crop Demo](crop_demo.gif)

```bash
python polygon_interacter.py --image "sampleimages/bookpage.jpeg"

**Click corners in this order:**
```
1 ──── 2
│      │
4 ──── 3


## 👩‍💻 Built With

- [OpenCV](https://opencv.org/) — Computer Vision
- [ReportLab](https://www.reportlab.com/) — PDF Generation
- [Streamlit](https://streamlit.io/) — Web Interface
- [SciPy](https://scipy.org/) — Scientific Computing
- [Pillow](https://python-pillow.org/) — Image Processing

Made with ❤️ using Python & OpenCV
