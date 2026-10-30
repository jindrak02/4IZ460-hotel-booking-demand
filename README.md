# Hotel Booking Demand – analysis of cancelled bookings

Semester project for the course **4IZ457 – Interpretable Methods** (Prague University of Economics and Business, winter semester 2026/27).

## Project goal

The goal is to identify characteristics and patterns associated with **cancelled hotel bookings**
using interpretable data analysis methods.

Planned methods:

- 4ft-Miner
- SD4ft-Miner
- CF-Miner
- Contingency tables
- Further interpretable methods in later project phases

Analyses are implemented in Python, primarily with the [CleverMiner](https://pypi.org/project/cleverminer/) library.

## Dataset

Publicly available **Hotel Booking Demand** dataset from Kaggle:
<https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand>

The original file is stored in `data/raw/`, data prepared for analyses in `data/processed/`.
Both directories are versioned in Git so that every team member works with the same data
without downloading it manually.

## Technologies

- Python 3.12
- [uv](https://docs.astral.sh/uv/) – Python environment and dependency management
- Git + GitHub – version control and team collaboration

## Repository structure

```
.
├── data/
│   ├── raw/          # original, unmodified dataset
│   └── processed/    # shared prepared data for all analyses
├── scripts/          # data preparation and transformation scripts
├── analyses/         # individual analytical tasks
├── reports/          # interim and final project presentations
├── pyproject.toml    # project metadata and dependency list
├── .python-version   # Python version for uv (3.12)
├── .gitignore
└── README.md
```

## Local setup

1. Install `uv` (if you don't have it yet) following <https://docs.astral.sh/uv/getting-started/installation/>.
   On macOS, `brew install uv` is enough.
2. Clone the repository and enter its directory:

   ```bash
   git clone https://github.com/jindrak02/4IZ460-hotel-booking-demand.git
   cd 4IZ460-hotel-booking-demand
   ```

3. Create the virtual environment and install dependencies:

   ```bash
   uv sync
   ```

   `uv` downloads Python 3.12 on its own (according to `.python-version`), creates `.venv/`
   and installs everything from `pyproject.toml`.

4. Run scripts inside the project environment:

   ```bash
   uv run python scripts/script_name.py
   ```

### Adding a dependency

```bash
uv add cleverminer
```

The command records the library in `pyproject.toml` and updates `uv.lock`. Commit both files
so that others get the same versions after `uv sync`.

## Team workflow with Git

- The `main` branch is shared and should always be in a working state.
- Do each task on its own branch, e.g. `analysis-4ft-seasonality` or `data-preparation`.
- Before starting work, pull the latest state: `git pull`.
- Commit and push finished work, then open a **pull request** into `main` on GitHub.
  Others review it and merge it after approval.
- Commit messages follow the conventions in `CLAUDE.md`.
- Remember to commit `pyproject.toml` and `uv.lock` after every `uv add`.
- Do not commit `.venv/` or caches – `.gitignore` takes care of that.

Basic work cycle:

```bash
git checkout main
git pull
git checkout -b branch-name
# ... work ...
git add .
git commit -m "feat(analysis): describe the change"
git push -u origin branch-name
```
