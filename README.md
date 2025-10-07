# 🧬 LineFixer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Windows%20|%20Linux-lightgrey)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)]()

## 🚀 Overview
**LineFixer** is a cross-platform desktop tool built for scientists and writers who often copy text from PDFs.  
It **removes unwanted line breaks** while preserving paragraph spacing, making your text instantly ready for reuse in manuscripts or reports.

### 🌟 Microbiologist Mode
The standout feature, **Microbiologist Mode**, integrates the latest **NCBI Taxonomy** to:
- 🔹 Automatically detect and *italicize* microbial **genus** and **species** names  
- 🔹 Ensure consistent scientific formatting  
- 🔹 Update taxonomy lists with one click  

No more manual edits — LineFixer helps you stay accurate and efficient.

---

## 💡 Key Features
- 🧹 Clean up broken lines from pasted PDF text  
- 🧬 Auto-italicize *genus* and *species* names  
- 🔄 One-click taxonomy updates  
- 💻 Works on **macOS**, **Windows**, and **Linux**

---

## ⚙️ Installation

### 💻 Option 1: macOS App
Download the latest `.dmg` installer from the [Releases](https://github.com/Aircus/LineFixer/releases) page.  
Drag **LineFixer.app** into your **Applications** folder and run it directly.

### 🐍 Option 2: Run from Source
If you prefer to run it from source:

```bash
git clone https://github.com/Aircus/LineFixer.git
cd LineFixer
pip install -r requirements.txt
python3 linefixer.py
```

---

## 🧭 Usage
1. **Paste** text copied from a PDF into LineFixer.  
2. Click **Fix Line Breaks** to clean the text.  
3. (Optional) Toggle **Microbiologist Mode** to automatically *italicize* genus and species names.  
4. Use **Update Taxonomy** to fetch the latest list from NCBI.  
5. Click **Copy Output** to paste the formatted text into your document.

---

## 📦 Dependencies
The main dependencies include:
- `tkinter`
- `pandas`
- `requests`

You can install all dependencies with:
```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing
Contributions are welcome!  
If you'd like to add features, improve taxonomy recognition, or fix bugs:
1. Fork the repo  
2. Create a new branch (`git checkout -b feature/new-feature`)  
3. Commit your changes (`git commit -m "Add new feature"`)  
4. Push and open a Pull Request

---

## 🧑‍💻 Author
Developed by **Tong**, Researcher at the Swedish University of Agricultural Sciences (SLU).  
For questions or suggestions, feel free to open an issue.

---

## 🖼️ Screenshots

### 🧭 Main Interface
<p align="center">
  <img src="assets/screenshot_main.png" alt="LineFixer main interface" width="600"/>
</p>

### 🧬 Microbiologist Mode
<p align="center">
  <img src="assets/screenshot_microbiologist_mode.png" alt="Microbiologist Mode example" width="600"/>
</p>

### 🔄 Taxonomy Update
<p align="center">
  <img src="assets/screenshot_update_taxonomy.png" alt="Update taxonomy example" width="600"/>
</p>

> 🖼️ You can replace these placeholder images later by placing your own screenshots in an `assets/` folder within the repository.

---

## 🪪 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
