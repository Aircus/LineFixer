# 🧬 LineFixer v1.0.0  
**Smart Text Tool for Microbiologists**  
Created by **Tong**  
[GitHub Repository](https://github.com/Aircus/LineFixer)

---

## 🚀 Overview  
**LineFixer** is a macOS desktop app designed to clean and format text copied from PDFs — perfect for scientific writing.  
It automatically removes unwanted line breaks while preserving paragraph structure, and in *Microbiologist Mode*, it italicizes microbial genus and species names based on the latest **NCBI Taxonomy**.

---

## ✨ Key Features  
- 🧹 **Clean & Copy** – Instantly remove line breaks and copy plain text  
- 🔬 **Microbiologist Mode** – Auto-detect and italicize *Genus* and *Genus species*  
- 🧠 **NCBI Taxonomy Integration** – Built-in updater to fetch genus, species, and strain names  
- 🧭 **Taxonomy Update Button** – One-click refresh with progress bar and status  
- 🧩 **Family-level Filter** – Avoid false italics for families (*-aceae*, *-idae*, etc.)  
- 🖋️ **RTF Clipboard Output** – Pasting into Word preserves italics  

---

## 🧰 How to Use  
1. Paste copied PDF text into the **input box**  
2. Click **Clean & Copy** to remove unwanted line breaks  
3. Or click **Microbiologist Mode** to:  
   - Clean text  
   - Italicize microbial names  
   - Copy RTF to clipboard  
4. Paste directly into **Word** or any **RTF-compatible editor**

---

## 🔄 Update Taxonomy  
Click **Update Taxonomy** to fetch the latest **NCBI Taxonomy** (`new_taxdump.zip`)  

The app will:  
- Download and extract the archive  
- Parse genus, species, and strain names  
- Exclude family-level taxa (*-aceae*, *-idae*, etc.)  
- Automatically reload the taxonomy list  
- Show the **update date** and **total name count**

---

## 🧠 Example  

**Input:**  
