<div align="center">
  <h1>SafeHire AI</h1>
  <p><strong>Ethical, Offline AI Document Verification for Recruitment</strong></p>
  <p><i>Team Oblivion — Open Innovation Hackathon</i></p>
</div>

<br />

> [!IMPORTANT]
> **Privacy First & Ethical AI:** SafeHire AI verifies resumes, certificates, ID proofs, and offer letters entirely on a local machine. No document data is ever sent to the cloud, ensuring strict compliance with data privacy standards and ethical AI usage. 

SafeHire AI combines Optical Character Recognition (OCR), forensic tamper detection (Error Level Analysis), semantic pattern matching, and AI-generated text stylometry into a single, highly transparent **Semantic Validity Score**.

---

## ✨ Features & Architecture

- **100% Offline Processing:** Ensure candidate privacy by keeping sensitive files on your local machine.
- **Explainable AI:** Every score is broken down into exhibits. We believe in white-box systems where HR professionals understand *why* a document was flagged.
- **AI Authorship Detection:** Detects if document attributes were manipulated or generated using AI tools (e.g. ChatGPT) by analyzing stylometric signals like burstiness and type-token ratios.
- **Modern Verification Desk Interface:** A fully bespoke, dark/light theme web interface designed specifically for review workflows, featuring an animated wax-seal gauge.

---

## 🚀 Getting Started (Windows)

We have provided automated batch scripts to make installation and startup seamless on Windows.

### Step 1: Installation
Run the `install.bat` file to automatically:
1. Create a Python Virtual Environment (`venv`).
2. Install all required dependencies from `requirements.txt`.
3. Check for and automatically install **Tesseract OCR** (an essential system dependency) via `winget` if it is missing.

> [!TIP]
> Just double click `install.bat` in your file explorer, or run it from your command prompt:
> ```cmd
> .\install.bat
> ```

### Step 2: Start the Server
Once installation is complete, run the `start_app.bat` file to launch the SafeHire AI backend server and serve the Verification Desk UI.

> ```cmd
> .\start_app.bat
> ```
> Once started, open your browser and navigate to: **http://127.0.0.1:8000**

---

## 💻 Manual Setup (macOS / Linux / Custom)

If you are not using the batch scripts, you can manually start the server:

```bash
# 1. Install the system OCR engine (one-time)
sudo apt-get install tesseract-ocr        # Ubuntu/Debian
# brew install tesseract                  # macOS

# 2. Set up virtual environment and install dependencies
python -m venv venv
source venv/bin/activate                  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

# 3. Launch the application
uvicorn api:app --reload
```

---

## 🔍 Understanding the Output

Every document processed by SafeHire AI returns a comprehensive evaluation:

- **Forensic Integrity:** Visualizes tampering via Error Level Analysis heatmaps.
- **Semantic Match:** Evaluates if the document's content matches the expected patterns of its type (e.g., resumes vs. ID proofs), returning a fixed relevance score.
- **AI Authorship:** Explicitly flags whether the document attributes were likely updated or generated using AI tools, based on predictable linguistic patterns.
- **OCR Text & Metadata:** Exposes raw extracted text and hidden EXIF metadata.

The **Verification Desk** UI presents these as inspectable tabs. The goal is to empower humans to make informed decisions, not to automate rejection blindly.

---

<div align="center">
  <sub>Built for the Open Innovation Hackathon. SafeHire AI runs entirely on the host device.</sub>
</div>
