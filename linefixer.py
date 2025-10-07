# LineFixer v1.0.0 • Created by Tong
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import tkinter.font as tkfont
import re, os, zipfile, datetime, threading, time, requests, warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

VERSION_TEXT = "Version 1.0.0 • Created by Tong"

COMMON_CAP_WORDS = {
    "A","An","The","This","That","These","Those","It","Its","They","Their","We","Our",
    "In","On","At","From","To","For","With","By","As","Of","And","Or","But","If","When",
    "Although","While","Beyond","During","Before","After","Within","Between","Because",
    "Bayesian","Naive","KernelExplainer","SHAP","Fig"
}

# Family/Order suffixes to ignore
FAMILY_SUFFIXES = (
    "aceae","idae","viridae","mycetes","phyceae","mycotina","opsida","ales"
)

START, END = "\x01", "\x02"

GENERA_SET = set()
BINOMIAL_SET = set()

def update_taxonomy():
    def is_valid_taxon_name(name: str) -> bool:
        if not name:
            return False
        name = name.replace("‘","'").replace("’","'").replace("“",'"').replace("”",'"')
        if " " in name and name.split(" ",1)[0] in COMMON_CAP_WORDS:
            return False
        return re.fullmatch(r"[A-Z][a-z]{2,}(?: [a-z][a-z-]{2,})?", name) is not None

    def task():
        try:
            progress_var.set(10)
            status_label.config(text="Downloading taxonomy files...", fg="blue")
            root.update_idletasks()

            url = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/new_taxdump/new_taxdump.zip"
            local_zip = os.path.join(os.path.expanduser("~"), "Desktop", "new_taxdump.zip")

            for attempt in range(3):
                try:
                    r = requests.get(url, stream=True, timeout=180, verify=False)
                    r.raise_for_status()
                    break
                except Exception as e:
                    if attempt == 2:
                        raise e
                    time.sleep(3)

            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(local_zip, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            progress = int(10 + (downloaded / total) * 30)
                            progress_var.set(min(progress, 40))
                            root.update_idletasks()

            progress_var.set(45)
            status_label.config(text="Extracting files...", fg="blue")
            root.update_idletasks()

            extract_dir = os.path.join(os.path.dirname(local_zip), "taxdump")
            os.makedirs(extract_dir, exist_ok=True)
            with zipfile.ZipFile(local_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            progress_var.set(60)
            status_label.config(text="Parsing taxonomy...", fg="blue")
            root.update_idletasks()

            target_ranks = {"genus", "species", "strain"}
            selected_ids = set()
            with open(os.path.join(extract_dir, "nodes.dmp"), encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) > 2 and parts[2].lower() in target_ranks:
                        selected_ids.add(parts[0])

            taxon_names = []
            with open(os.path.join(extract_dir, "names.dmp"), encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) > 3 and parts[3].lower() == "scientific name" and parts[0] in selected_ids:
                        nm = parts[1]
                        if is_valid_taxon_name(nm):
                            taxon_names.append(nm)

            taxon_names = sorted(set(taxon_names))
            with open("genus_list.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(taxon_names))

            reload_taxonomy()

            progress_var.set(100)
            date_str = datetime.date.today().isoformat()
            status_label.config(
                text=f"Last updated: {date_str} (genera: {len(GENERA_SET)}, binomials: {len(BINOMIAL_SET)})",
                fg="green"
            )
            messagebox.showinfo(
                "LineFixer",
                f"Taxonomy list updated successfully.\nGenera: {len(GENERA_SET)}\nBinomials: {len(BINOMIAL_SET)}"
            )

        except Exception as e:
            status_label.config(text="Update failed", fg="red")
            messagebox.showerror("LineFixer", f"Update failed: {e}")

        finally:
            try: os.remove(local_zip)
            except Exception: pass
            time.sleep(0.3)
            progress_var.set(0)
            root.update_idletasks()

    threading.Thread(target=task).start()

def sanitize_loaded_name(name: str) -> bool:
    if not name:
        return False
    if " " in name and name.split(" ",1)[0] in COMMON_CAP_WORDS:
        return False
    return re.fullmatch(r"[A-Z][a-z]{2,}(?: [a-z][a-z-]{2,})?", name) is not None

def load_taxonomy_sets():
    builtin = {"Escherichia","Bacillus","Methanothrix","Methanocorpusculum","Sphingobium"}
    genera = set(builtin)
    binomials = set()
    path = "genus_list.txt"
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            for raw in f:
                name = raw.strip()
                if not name or not sanitize_loaded_name(name):
                    continue
                tokens = name.split()
                if len(tokens) >= 1:
                    g = tokens[0]
                    if g not in COMMON_CAP_WORDS:
                        genera.add(g)
                if len(tokens) >= 2:
                    pair = tokens[0] + " " + tokens[1]
                    binomials.add(pair)
    print(f"Loaded taxonomy: genera={len(genera)}, binomials={len(binomials)}")
    return genera, binomials

def reload_taxonomy():
    global GENERA_SET, BINOMIAL_SET
    GENERA_SET, BINOMIAL_SET = load_taxonomy_sets()

reload_taxonomy()

def clean_text(text):
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            out.append("\n")
        else:
            if i < len(lines)-1 and lines[i+1].strip() and not s.endswith(('.',':',';')):
                s += " "
            out.append(s)
    return "".join(out)

def mark_italics(text):
    t = text

    full_pat = re.compile(r"\b([A-Z][a-z]{2,})\s+([a-z][a-z-]{2,})\b")
    def sub_full(m):
        g, s = m.group(1), m.group(2)
        if g not in COMMON_CAP_WORDS:
            pair = f"{g} {s}"
            if pair in BINOMIAL_SET:
                return f"{START}{g} {s}{END} "
        return m.group(0)
    t = full_pat.sub(sub_full, t)

    genus_only_pat = re.compile(r"(?<!\x01)\b([A-Z][a-z]{2,})\b")
    def sub_genus(m):
        g = m.group(1)
        if g in COMMON_CAP_WORDS or g.endswith(FAMILY_SUFFIXES):
            return m.group(0)
        if g in GENERA_SET:
            return f"{START}{g}{END} "
        return m.group(0)
    t = genus_only_pat.sub(sub_genus, t)

    t = re.sub(r'\s{2,}', ' ', t)
    t = re.sub(r'\s+([,.;:])', r'\1', t)
    return t

def compute_preview(marked):
    plain, ital = [], []
    i = 0
    while i < len(marked):
        if marked.startswith(START, i):
            start = len(plain); i += len(START)
        elif marked.startswith(END, i):
            ital.append((start, len(plain))); i += len(END)
        else:
            plain.append(marked[i]); i += 1
    return "".join(plain), ital

def escape_rtf(s):
    s = (s.replace('‘', "'").replace('’', "'")
           .replace('“', '"').replace('”', '"')
           .replace('–', '-').replace('—', '-')
           .replace('…', '...'))
    s = s.replace('\\', r'\\').replace('{', r'\{').replace('}', r'\}')
    s = s.replace('\n', r'\par ' + '\n')
    return s

def to_rtf(marked):
    out = []
    i = 0
    while i < len(marked):
        if marked.startswith(START, i):
            out.append(r'\i '); i += len(START)
        elif marked.startswith(END, i):
            out.append(r'\i0'); i += len(END)
        else:
            out.append(escape_rtf(marked[i])); i += 1
    return r'{\rtf1\ansi ' + ''.join(out) + '}'

def copy_rtf_and_plain(rtf, plain):
    try:
        from AppKit import NSPasteboard
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setString_forType_(rtf, "public.rtf")
        pb.setString_forType_(plain, "public.utf8-plain-text")
    except Exception:
        import pyperclip; pyperclip.copy(plain)

def process_standard():
    raw = input_text.get("1.0", tk.END)
    cleaned = clean_text(raw)
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, cleaned)
    output_text.config(state="disabled")
    try:
        import pyperclip; pyperclip.copy(cleaned)
    except: pass
    messagebox.showinfo("LineFixer", "Cleaned text copied.")

def process_microbiologist_mode():
    raw = input_text.get("1.0", tk.END)
    cleaned = clean_text(raw)
    marked = mark_italics(cleaned)
    plain, italics = compute_preview(marked)
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, plain)
    output_text.tag_configure("italic", font=ITALIC_FONT)
    for s, e in italics:
        output_text.tag_add("italic", f"1.0+{s}c", f"1.0+{e}c")
    output_text.config(state="disabled")
    copy_rtf_and_plain(to_rtf(marked), plain)
    messagebox.showinfo("LineFixer", "RTF copied with italics.")

def clear_input():
    input_text.delete("1.0", tk.END)

root = tk.Tk()
root.title("LineFixer v1.0.0")
root.geometry("940x720")
root.lift(); root.focus_force()

DEFAULT_FONT = tkfont.nametofont("TkDefaultFont")
ITALIC_FONT = DEFAULT_FONT.copy(); ITALIC_FONT.configure(slant="italic")

tk.Button(root, text="Clear Input", width=16, command=clear_input).pack(pady=(10,0))
tk.Button(root, text="Update Taxonomy", width=16, command=update_taxonomy).pack(pady=(5,5))

progress_var = tk.IntVar(value=0)
progress = ttk.Progressbar(root, length=200, variable=progress_var, mode='determinate')
progress.pack(pady=(0,5))

status_label = tk.Label(root, text="Last updated: (not yet)", fg="gray")
status_label.pack()

tk.Label(root, text="Paste original PDF text:").pack()
input_text = scrolledtext.ScrolledText(root, height=13, font=DEFAULT_FONT)
input_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

row = tk.Frame(root); row.pack(pady=6)
tk.Button(row, text="Clean & Copy", width=18, command=process_standard).pack(side=tk.LEFT, padx=6)
tk.Button(row, text="Microbiologist Mode", width=18,
          command=lambda: [root.focus_force(), process_microbiologist_mode()]).pack(side=tk.LEFT, padx=6)

tk.Label(root, text="Preview:").pack()
output_text = scrolledtext.ScrolledText(root, height=13, font=DEFAULT_FONT)
output_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
output_text.config(state="disabled")

tk.Label(root, text=VERSION_TEXT, fg="gray").pack(pady=(6,12))
root.mainloop()
