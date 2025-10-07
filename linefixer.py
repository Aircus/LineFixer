#!/usr/bin/env python3
import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import os, re, requests, pandas as pd, threading, datetime, tarfile

# ---------- App storage path ----------
def app_data_path(name: str) -> str:
    base = os.path.expanduser("~/Library/Application Support/LineFixer")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, name)

GENUS_FILE = app_data_path("genus_list.txt")

# ---------- Default taxon names ----------
def load_names():
    if os.path.exists(GENUS_FILE):
        with open(GENUS_FILE, "r", encoding="utf-8") as f:
            return {ln.strip() for ln in f if ln.strip()}
    return {
        "Escherichia","Bacillus","Methanothrix","Methanocorpusculum",
        "Sphingobium","Marivita","Roseobacter","Aquaspirillum",
        "Cloacibacterium","Smithella","Cloacimonas","Pseudarcobacter"
    }

NAMES = load_names()

STOPWORDS_CAP = {
    "A","An","The","This","That","These","Those","It","Its","They","Their","We","Our",
    "You","Your","In","On","At","From","To","For","With","By","As","Of","And","Or","But",
    "If","When","While","Because","Although","Beyond","During","Before","After","Within",
    "Between","Figure","Fig","Table","Supplementary","Methods","Results","Discussion",
    "Introduction","Conclusion"
}

FAMILY_SUFFIXES = ("aceae","idae")

# ---------- Clean pasted text ----------
def clean_text(text: str) -> str:
    replacements = {
        "‘": "'", "’": "'", "‚": ",",
        "“": '"', "”": '"', "´": "'", "`": "'",
        "–": "-", "—": "-", "…": "...",
        "\xa0": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            out.append("\n")
        else:
            if i < len(lines)-1 and lines[i+1].strip() and not s.endswith(('.',':',';','?','!')):
                s += " "
            out.append(s)
    return "".join(out)

# ---------- Token helpers ----------
def _split_token(tok: str):
    m = re.match(r'^(\W*)([A-Za-z][A-Za-z0-9_-]*)(\W*)$', tok)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return ("", tok, "")

# ---------- Italicization logic ----------
def italicize_with_markers(text: str) -> str:
    tokens = text.split()
    parts = [_split_token(t) for t in tokens]
    ital = [False] * len(parts)

    STOP_NEXT = {
        "belongs","possesses","occurs","exists","contains","represents",
        "was","were","is","are","be","been","being",
        "has","have","had","does","did","done","doing",
        "can","could","may","might","shall","should","will","would",
        "must","also","and","or","of","in","on","to","for","with",
        "family","genus","species","strain"
    }

    for i, (_, core, _) in enumerate(parts):
        if not core or core in STOPWORDS_CAP or core.endswith(FAMILY_SUFFIXES):
            continue

        if core in NAMES:
            # Genus + species (next lowercase token not stopword)
            if i + 1 < len(parts):
                nxt = parts[i + 1][1]
                if (
                    nxt and nxt.islower() and re.fullmatch(r"[a-z][a-z-]{2,}", nxt)
                    and nxt not in STOP_NEXT
                ):
                    ital[i] = True
                    ital[i + 1] = True
                    continue
            ital[i] = True

    out = []
    for (pre, core, post), it in zip(parts, ital):
        token = pre + (f"*{core}*" if it else core) + post
        out.append(token)
    return " ".join(out)

# ---------- Marker conversion ----------
def strip_markers_and_ranges(s: str):
    plain = []
    ranges = []
    i = 0
    in_it = False
    start = 0
    while i < len(s):
        ch = s[i]
        if ch == "*":
            if not in_it:
                start = len(plain); in_it = True
            else:
                ranges.append((start, len(plain))); in_it = False
            i += 1
        else:
            plain.append(ch); i += 1
    if in_it:
        ranges.append((start, len(plain)))
    return "".join(plain), ranges

def _rtf_escape(ch: str) -> str:
    if ch in ["\\","{","}"]:
        return "\\" + ch
    if ch == "\n":
        return r"\par " + "\n"
    if ord(ch) > 127:
        return f"\\u{ord(ch)}?"
    return ch

def build_rtf_from_plain_and_ranges(plain: str, ranges):
    marks = []
    for s, e in ranges:
        marks.append((s, r"\i "))
        marks.append((e, r"\i0 "))
    marks.sort(key=lambda x: x[0])
    out = []
    mi = 0
    for idx, ch in enumerate(plain):
        while mi < len(marks) and marks[mi][0] == idx:
            out.append(marks[mi][1]); mi += 1
        out.append(_rtf_escape(ch))
    while mi < len(marks):
        out.append(marks[mi][1]); mi += 1
    return r"{\rtf1 " + "".join(out) + "}"

# ---------- Clipboard ----------
def copy_rtf_and_plain(rtf: str, plain: str):
    try:
        from AppKit import NSPasteboard
        from Foundation import NSData
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        data = rtf.encode("utf-8")
        nsdata = NSData.dataWithBytes_length_(data, len(data))
        pb.setData_forType_(nsdata, "public.rtf")
        pb.setString_forType_(plain, "public.utf8-plain-text")
        return True
    except Exception:
        try:
            import pyperclip; pyperclip.copy(plain)
        except Exception:
            pass
        return False

# ---------- Update taxonomy ----------
def update_taxonomy():
    status_label.config(text="Updating taxonomy...")
    def run():
        try:
            url = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz"
            tar_path = app_data_path("new_taxdump.tar.gz")
            out_dir = app_data_path("taxdump")
            os.makedirs(out_dir, exist_ok=True)
            r = requests.get(url, stream=True, timeout=90)
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with open(tar_path, "wb") as f:
                done = 0
                for chunk in r.iter_content(1024*1024):
                    if chunk:
                        f.write(chunk); done += len(chunk)
                        pct = done*100/total if total else 0
                        status_label.config(text=f"Downloading taxonomy... {pct:.1f}%")
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(out_dir)
            def parse_dmp(path, ncols):
                df = pd.read_csv(path, sep="|", header=None, usecols=range(ncols), engine="python")
                return df.apply(lambda x: x.astype(str).str.strip())
            names = parse_dmp(os.path.join(out_dir, "names.dmp"), 4)
            names.columns = ["tax_id","name_txt","unique_name","class"]
            nodes = parse_dmp(os.path.join(out_dir, "nodes.dmp"), 3)
            nodes.columns = ["tax_id","parent","rank"]
            merged = pd.merge(names, nodes, on="tax_id", how="left")
            taxa = merged.loc[merged["rank"].isin(["genus","species","strain"]), "name_txt"].dropna().unique()
            taxa = [t.strip() for t in taxa]
            with open(GENUS_FILE, "w", encoding="utf-8") as f:
                for t in taxa:
                    f.write(t + "\n")
            global NAMES
            NAMES = set(taxa)
            status_label.config(text=f"✅ Update completed: {len(NAMES)} names ({datetime.date.today()})")
            messagebox.showinfo("LineFixer", f"Taxonomy updated.\nSaved {len(NAMES)} names.")
        except Exception as e:
            status_label.config(text=f"❌ Update failed: {e}")
            messagebox.showerror("LineFixer", f"Update failed:\n{e}")
    threading.Thread(target=run, daemon=True).start()

# ---------- Actions ----------
def do_clean_and_copy():
    text = input_box.get("1.0", tk.END)
    cleaned = clean_text(text)
    try:
        import pyperclip; pyperclip.copy(cleaned)
    except Exception:
        pass
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, cleaned)
    output_box.config(state="disabled")
    messagebox.showinfo("LineFixer", "Cleaned text copied to clipboard.")

def do_micro_mode():
    text = input_box.get("1.0", tk.END)
    cleaned = clean_text(text)
    marked = italicize_with_markers(cleaned)
    plain, ranges = strip_markers_and_ranges(marked)
    rtf = build_rtf_from_plain_and_ranges(plain, ranges)
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, plain)
    output_box.tag_configure("i", font=(DEFAULT_FONT.cget("family"), DEFAULT_FONT.cget("size"), "italic"))
    for s, e in ranges:
        output_box.tag_add("i", f"1.0+{s}c", f"1.0+{e}c")
    output_box.config(state="disabled")
    copied_rich = copy_rtf_and_plain(rtf, plain)
    if copied_rich:
        messagebox.showinfo("LineFixer", "RTF copied with italics. Paste into Word/Pages.")
    else:
        messagebox.showwarning("LineFixer", "Copied plain text only. Install 'pyobjc' for rich paste.")

def do_clear():
    input_box.delete("1.0", tk.END)

# ---------- GUI ----------
root = tk.Tk()
root.title("LineFixer v1.0.0 — Created by Tong")
root.geometry("900x680")
DEFAULT_FONT = font.nametofont("TkDefaultFont")
tk.Button(root, text="Clear Input", command=do_clear).pack(pady=(10,4))
tk.Button(root, text="Update Taxonomy", command=update_taxonomy).pack(pady=(0,6))
status_label = tk.Label(root, text="Ready.", anchor="w")
status_label.pack(fill="x", padx=8)
tk.Label(root, text="Input Text:").pack(anchor="w", padx=8)
input_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=12)
input_box.pack(padx=8, pady=4, fill="both", expand=False)
btn_row = tk.Frame(root); btn_row.pack(pady=6)
tk.Button(btn_row, text="Clean & Copy", width=18, command=do_clean_and_copy).pack(side="left", padx=6)
tk.Button(btn_row, text="Microbiologist Mode", width=18, command=do_micro_mode).pack(side="left", padx=6)
tk.Label(root, text="Output Preview:").pack(anchor="w", padx=8)
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=14)
output_box.pack(padx=8, pady=4, fill="both", expand=True)
output_box.config(state="disabled")
root.mainloop()