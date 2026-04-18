# 📄 OpenCV Document Scanner

A CamScanner-style document scanner built with Python, OpenCV, and Streamlit.  
Upload images → auto-detect edges → perspective correct → download as PDF.

---

## 🌐 Live Demo
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

---

## 🗂️ Project Structure

```
opencv-document-scanner/
├── app.py                  ← Streamlit web app
├── scan.py                 ← core scanner (CLI version)
├── polygon_interacter.py   ← manual corner selector
├── imutils.py              ← image utility functions
├── transform.py            ← perspective transform math
├── requirements.txt        ← Python dependencies
├── sampleimages/           ← sample images to test with
│   ├── bookpage.jpeg
│   ├── eyeshadowpalatte.jpeg
│   ├── handwrittennotes.jpeg
│   ├── notepad.jpeg
│   ├── registerback.jpeg
│   └── ticketinstructions.jpeg
└── README.md
```

---

## 🚀 Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/opencv-document-scanner.git
cd opencv-document-scanner
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit app
```bash
streamlit run app.py
```

Open your browser and go to:
```
http://localhost:8501
```

---

## 💻 CLI Usage (without UI)

### Scan a whole folder
```bash
python scan.py --folder "sampleimages" --output result.pdf
```

### Scan specific images
```bash
python scan.py --images img1.jpg img2.jpg --output result.pdf
```

### Manual crop then scan
```bash
# Step 1 — select corners manually
python polygon_interacter.py --image "sampleimages/bookpage.jpeg"

# Step 2 — scan the cropped image
python scan.py --images "bookpage_cropped.jpg" --output result.pdf
```

### Choose enhancement mode
```bash
python scan.py --folder "sampleimages" --output result.pdf --mode grayscale
```

---

## 🎨 Enhancement Modes

| Mode | Best For | Example |
|------|----------|---------|
| `adaptive` | Text documents, books | bookpage.jpeg |
| `grayscale` | Handwritten notes | handwrittennotes.jpeg |
| `color` | Photos, colorful images | eyeshadowpalatte.jpeg |
| `auto` | Auto-picks based on filename | any |

---

## 🌍 Deploy on Streamlit Cloud

### Step 1 — Push to GitHub
Make sure all files are pushed to your GitHub repository.

### Step 2 — Go to Streamlit Cloud
Visit [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

### Step 3 — Create New App
- Click **New App**
- Select your repository
- Set **Main file path** to `app.py`
- Click **Deploy**

### Step 4 — Share your link!
You will get a free public URL like:
```
https://yourusername-opencv-document-scanner.streamlit.app
```

---

## 🛠️ How It Works

```
📷 Upload Image
      ↓
🔲 Resize for memory efficiency
      ↓
⚡ Canny Edge Detection
      ↓
🔍 Find largest 4-sided contour
      ↓
📐 Perspective Transform (birds eye view)
      ↓
✨ Enhance (adaptive / grayscale / color)
      ↓
📄 Save to PDF
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `opencv-python-headless` | Image processing & edge detection |
| `scipy` | Euclidean distance for point ordering |
| `Pillow` | Image format conversion |
| `reportlab` | PDF generation |
| `numpy` | Array & matrix operations |
| `streamlit` | Web app interface |

---

## 🖱️ Manual Corner Selection

When automatic edge detection fails (⚠ warning), use the manual tool:

```bash
python polygon_interacter.py --image "sampleimages/bookpage.jpeg"
```

**Controls:**
| Key | Action |
|-----|--------|
| Click | Place corner point |
| C | Confirm and crop |
| R | Reset all points |
| Q | Quit |

**Click corners in this order:**
```
1 ──── 2
│      │
4 ──── 3
```

---

## ✅ Scan Output Guide

```
✓ Document edges detected – perspective corrected   ← perfect scan
⚠ No clear document border – using full image       ← use manual crop
```

---

## 👩‍💻 Built With

- [OpenCV](https://opencv.org/) — Computer Vision
- [ReportLab](https://www.reportlab.com/) — PDF Generation
- [Streamlit](https://streamlit.io/) — Web Interface
- [SciPy](https://scipy.org/) — Scientific Computing
- [Pillow](https://python-pillow.org/) — Image Processing

---

## 📝 License

MIT License — free to use and modify.

---

Made with ❤️ using Python & OpenCV
