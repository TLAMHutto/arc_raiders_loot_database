# ARC Raiders Loot Database

This repository contains three structured JSON files:

* `safe_to_sell.json`
* `safe_to_recycle.json`
* `what_to_keep.json`

These are used by the Python desktop app to provide fast keyword-based searching across all loot categories.

---

## Application Screenshot

Below is a preview of the search application interface:

![Loot Search Screenshot](./assets/loot_search_ui.png)

---

## Getting Started

### 1. Download the Repository

Clone the repository using Git:

```bash
git clone https://github.com/TLAMHutto/arc_raiders_loot_database.git
```

Or download it as a ZIP from GitHub and extract it locally.

---

### 2. Install Python (if not already installed)

Make sure you have **Python 3.9+** installed on your system.
You can check your version with:

```bash
python --version
```

---

### 3. Run the Python App

Navigate into the project directory:

```bash
cd arc_raiders_loot_database
```

Then start the application:

```bash
python loot_app.py
```

The program will automatically load the three JSON files:

* `safe_to_sell.json`
* `safe_to_recycle.json`
* `what_to_keep.json`

No packaging, no virtual environment, and no dependency installation is required beyond the standard Python library.

---
