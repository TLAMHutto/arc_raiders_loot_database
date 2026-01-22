import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ---------------------------
# Data model (normalized)
# ---------------------------

@dataclass
class LootRecord:
    item: str
    category: str           # "sell" | "recycle" | "keep"
    sell_price: Optional[int] = None
    recycles_into: Optional[List[str]] = None
    use_for: Optional[List[str]] = None

    def searchable_text(self) -> str:
        """Text blob used for keyword matching."""
        parts = [self.item, self.category]
        if self.sell_price is not None:
            parts.append(str(self.sell_price))
        if self.recycles_into:
            parts.extend(self.recycles_into)
        if self.use_for:
            parts.extend(self.use_for)
        return " ".join(parts).lower()


# ---------------------------
# Loaders
# ---------------------------

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_safe_to_sell(path: str) -> List[LootRecord]:
    data = load_json(path)
    out: List[LootRecord] = []
    for row in data:
        out.append(LootRecord(
            item=row["item"],
            category="sell",
            sell_price=int(row["sell_price"])
        ))
    return out

def load_safe_to_recycle(path: str) -> List[LootRecord]:
    data = load_json(path)
    out: List[LootRecord] = []
    for row in data:
        out.append(LootRecord(
            item=row["item"],
            category="recycle",
            recycles_into=list(row.get("recycles_into", []))
        ))
    return out

def load_what_to_keep(path: str) -> List[LootRecord]:
    data = load_json(path)
    out: List[LootRecord] = []
    for row in data:
        out.append(LootRecord(
            item=row["item"],
            category="keep",
            use_for=list(row.get("use_for", []))
        ))
    return out

def build_index(db_dir: str) -> List[LootRecord]:
    """Loads all 3 files and returns one unified list (in memory)."""
    sell_path = os.path.join(db_dir, "safe_to_sell.json")
    recycle_path = os.path.join(db_dir, "safe_to_recycle.json")
    keep_path = os.path.join(db_dir, "what_to_keep.json")

    missing = [p for p in (sell_path, recycle_path, keep_path) if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError("Missing JSON files:\n" + "\n".join(missing))

    records: List[LootRecord] = []
    records.extend(load_safe_to_sell(sell_path))
    records.extend(load_safe_to_recycle(recycle_path))
    records.extend(load_what_to_keep(keep_path))
    return records


# ---------------------------
# Search
# ---------------------------

def matches_query(record: LootRecord, query: str) -> bool:
    """
    AND-search: all words must appear somewhere in the record's searchable text.
    """
    q = query.strip().lower()
    if not q:
        return True
    text = record.searchable_text()
    terms = [t for t in q.split() if t]
    return all(term in text for term in terms)

def format_details(record: LootRecord) -> str:
    if record.category == "sell":
        return f"Sell Price: {record.sell_price}"
    if record.category == "recycle":
        return "Recycles Into: " + ", ".join(record.recycles_into or [])
    if record.category == "keep":
        return "Use For: " + ", ".join(record.use_for or [])
    return ""


# ---------------------------
# GUI
# ---------------------------

class LootApp(tk.Tk):
    def __init__(self, db_dir: str):
        super().__init__()
        self.title("Loot Search")
        self.geometry("900x520")

        try:
            self.records = build_index(db_dir)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            raise

        # Top controls
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Search:").pack(side="left")
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(top, textvariable=self.query_var, width=45)
        self.query_entry.pack(side="left", padx=(6, 10))
        self.query_entry.bind("<Return>", lambda e: self.refresh())

        ttk.Label(top, text="Category:").pack(side="left")
        self.category_var = tk.StringVar(value="all")
        self.category_combo = ttk.Combobox(
            top,
            textvariable=self.category_var,
            values=["all", "sell", "recycle", "keep"],
            state="readonly",
            width=10
        )
        self.category_combo.pack(side="left", padx=(6, 10))
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        ttk.Button(top, text="Search", command=self.refresh).pack(side="left")
        ttk.Button(top, text="Clear", command=self.clear).pack(side="left", padx=(8, 0))

        # Results table
        cols = ("item", "category", "details")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        self.tree.heading("item", text="Item")
        self.tree.heading("category", text="Category")
        self.tree.heading("details", text="Details")

        self.tree.column("item", width=260, anchor="w")
        self.tree.column("category", width=80, anchor="center")
        self.tree.column("details", width=520, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Status bar
        self.status_var = tk.StringVar(value=f"Loaded {len(self.records)} records.")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", padx=10, pady=(0, 8))

        self.refresh()
        self.query_entry.focus_set()

    def clear(self):
        self.query_var.set("")
        self.category_var.set("all")
        self.refresh()

    def refresh(self):
        query = self.query_var.get()
        cat = self.category_var.get()

        # clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # filter + insert
        shown = 0
        for rec in self.records:
            if cat != "all" and rec.category != cat:
                continue
            if not matches_query(rec, query):
                continue
            self.tree.insert("", "end", values=(rec.item, rec.category, format_details(rec)))
            shown += 1

        self.status_var.set(f"Showing {shown} / {len(self.records)} records.")


if __name__ == "__main__":
    # DB dir = folder where this script lives
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = LootApp(db_dir=base_dir)
    app.mainloop()
