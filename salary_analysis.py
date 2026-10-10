"""
Job Market Salary Analysis
==========================
Reads a Kaggle CSV of data-science / AI / ML salaries and answers:

    Q1  How does average yearly salary (USD) change with experience level?
    Q2  Which job titles appear most often, and which pay the highest median?
    Q3  (extra) Does the remote-work ratio affect salary?

Charts are saved to the charts/ folder.

Run it from the project folder:   python salary_analysis.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

# ------------------------------------------------------------------ settings
# Change these in one place instead of hunting through the code.
DATA_FILE = Path("data") / "ds_salaries.csv"   # where the Kaggle file lives
CHART_DIR = Path("charts")                      # where chart images are saved
SHOW_CHARTS = False        # True = also pop the charts up on screen
DROP_DUPLICATES = True     # True = remove rows that are exact copies of another
MIN_RECORDS = 10           # a job title needs at least this many rows to be trusted

# Columns the analysis cannot run without.
REQUIRED_COLUMNS = ["experience_level", "job_title", "salary_in_usd", "remote_ratio"]

# The dataset stores short codes; these dictionaries turn them into words.
EXPERIENCE_LABELS = {"EN": "Entry", "MI": "Mid", "SE": "Senior", "EX": "Executive"}
EXPERIENCE_ORDER = list(EXPERIENCE_LABELS.values())   # Entry -> Executive

REMOTE_LABELS = {0: "On-site", 50: "Hybrid", 100: "Remote"}
REMOTE_ORDER = list(REMOTE_LABELS.values())


# ------------------------------------------------------------------ helpers
def money(value):
    """Format a number as dollars, e.g. 125000 -> $125,000 (NaN -> '-')."""
    return "-" if pd.isna(value) else f"${value:,.0f}"


def percent(value):
    """Format a number as a signed percentage, e.g. +12.3% (NaN -> '-')."""
    return "-" if pd.isna(value) else f"{value:+.1f}%"


def print_table(title, table, formatters=None):
    """Print a titled table so the console output is easy to read."""
    print(f"\n=== {title} ===")
    print(table.to_string(formatters=formatters, na_rep="-"))


# ------------------------------------------------------------------ 1. LOAD
def load_data(path):
    """Read the CSV into a DataFrame and make sure it has what we need."""
    if not path.exists():
        raise SystemExit(
            f"Could not find {path}.\n"
            "Download the dataset from Kaggle and save it in the data/ folder."
        )

    df = pd.read_csv(path)

    # Some versions of this dataset have an extra unnamed index column. Drop it.
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise SystemExit(f"The file is missing expected columns: {missing}")

    return df


# ------------------------------------------------------------------ 2. INSPECT
def inspect_data(df):
    """Print a first look at the raw data: size, types, gaps, duplicates."""
    print("=== FIRST LOOK AT THE RAW DATA ===")
    print(f"Rows: {len(df):,}   Columns: {df.shape[1]}")

    print("\nFirst 5 rows:")
    print(df.head().to_string())

    print("\nColumn types and non-empty counts:")
    df.info()

    print("\nSalary (USD) summary statistics:")
    print(df["salary_in_usd"].describe().round(0).to_string())

    print("\nMissing values per column:")
    print(df.isna().sum().to_string())

    print(f"\nExact duplicate rows: {df.duplicated().sum():,}")

    print("\nExperience level codes found:")
    print(df["experience_level"].value_counts().to_string())

    print("\nRemote ratio values found:")
    print(df["remote_ratio"].value_counts().to_string())


# ------------------------------------------------------------------ 3. CLEAN
def clean_data(df):
    """Return a cleaned copy: no gaps, no duplicates, readable labels."""
    df = df.copy()               # never change the caller's data by accident
    rows_before = len(df)

    # 1. Drop rows that are missing something we need.
    df = df.dropna(subset=REQUIRED_COLUMNS)

    # 2. Optionally drop exact duplicate rows.
    if DROP_DUPLICATES:
        df = df.drop_duplicates()

    # 3. Make sure salary is a number, and ignore impossible values.
    df["salary_in_usd"] = pd.to_numeric(df["salary_in_usd"], errors="coerce")
    df = df[df["salary_in_usd"] > 0].copy()   # NaN > 0 is False, so NaN rows go too

    # 4. Tidy job titles (a stray space would split one title into two).
    df["job_title"] = df["job_title"].str.strip()

    # 5. DATA CONVERSION: short codes -> readable labels.
    #    An ordered Categorical remembers Entry < Mid < Senior < Executive,
    #    so tables and charts sort in the natural order, not alphabetically.
    df["experience"] = pd.Categorical(
        df["experience_level"].map(EXPERIENCE_LABELS),
        categories=EXPERIENCE_ORDER, ordered=True)
    df["remote"] = pd.Categorical(
        df["remote_ratio"].map(REMOTE_LABELS),
        categories=REMOTE_ORDER, ordered=True)

    # 6. Drop rows whose code we did not recognise (they became NaN above).
    df = df.dropna(subset=["experience", "remote"])

    print(f"\nCleaning kept {len(df):,} of {rows_before:,} rows "
          f"({rows_before - len(df):,} removed).")
    return df.reset_index(drop=True)


# ------------------------------------------------------------------ 4. QUESTION 1
def summarise(df, group_column):
    """Count, mean and median salary for each group in group_column."""
    return (df.groupby(group_column, observed=True)["salary_in_usd"]
              .agg(records="count", mean="mean", median="median")
              .round(0))


def question_1(df):
    """Q1: how does salary change across experience levels?"""
    table = summarise(df, "experience")        # already Entry -> Executive order

    # How much higher is each level than the one before it?
    table["mean_change_vs_previous"] = (
        table["mean"] / table["mean"].shift(1) - 1) * 100

    print_table("Q1: SALARY BY EXPERIENCE LEVEL", table, {
        "records": "{:,}".format, "mean": money, "median": money,
        "mean_change_vs_previous": percent})

    # SORT: the same numbers ranked from highest to lowest average salary.
    ranked = table.sort_values("mean", ascending=False)[["mean", "median"]]
    print_table("Q1: RANKED BY AVERAGE SALARY", ranked,
                {"mean": money, "median": money})
    return table


# ------------------------------------------------------------------ 5. QUESTION 2
def question_2(df):
    """Q2: which job titles are most common, and which pay the most?"""
    counts = df["job_title"].value_counts()      # COUNT, sorted high -> low
    most_common = counts.head(10)

    print("\n=== Q2a: 10 MOST COMMON JOB TITLES (number of records) ===")
    print(most_common.to_string())

    # FILTER: keep only titles with enough rows for a median to mean something.
    reliable_titles = counts[counts >= MIN_RECORDS].index
    reliable = df[df["job_title"].isin(reliable_titles)]
    print(f"\n{len(reliable_titles)} titles have at least {MIN_RECORDS} records "
          f"({len(reliable):,} rows).")

    # AGGREGATE + SORT: median salary per title, highest first.
    pay = (reliable.groupby("job_title")["salary_in_usd"]
                   .agg(records="count", median="median", mean="mean")
                   .round(0)
                   .sort_values("median", ascending=False))

    if pay.empty:
        print(f"No title has {MIN_RECORDS}+ records - lower MIN_RECORDS.")
    else:
        print_table("Q2b: HIGHEST-PAYING TITLES (by median salary)", pay.head(10),
                    {"records": "{:,}".format, "median": money, "mean": money})
    return most_common, pay


# ------------------------------------------------------------------ 6. QUESTION 3 (extra)
def question_3(df):
    """Q3: does the share of remote work change salary?"""
    overall = summarise(df, "remote")
    print_table("Q3: SALARY BY REMOTE RATIO", overall,
                {"records": "{:,}".format, "mean": money, "median": money})

    # Experience also drives pay, so compare remote groups at the SAME
    # experience level - splitting by both gives a fairer comparison.
    pivot = df.pivot_table(index="experience", columns="remote",
                           values="salary_in_usd", aggfunc="median",
                           observed=True).round(0)
    counts = df.pivot_table(index="experience", columns="remote",
                            values="salary_in_usd", aggfunc="count",
                            observed=True).fillna(0).astype(int)

    print_table("Q3: MEDIAN SALARY BY EXPERIENCE x REMOTE", pivot,
                {col: money for col in pivot.columns})
    print_table("Q3: RECORDS IN EACH CELL (small numbers = weak evidence)", counts)
    return overall, pivot


# ------------------------------------------------------------------ 7. CHARTS
def dollars_axis(ax, axis="y"):
    """Show axis numbers as $125,000 instead of 125000."""
    formatter = FuncFormatter(lambda value, _position: f"${value:,.0f}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(formatter)


def finish_chart(fig, filename):
    """Save the chart as a PNG, optionally show it, then free its memory."""
    CHART_DIR.mkdir(exist_ok=True)
    path = CHART_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Saved chart: {path}")
    if SHOW_CHARTS:
        plt.show()
    plt.close(fig)


def chart_experience(table):
    """Bar chart: mean and median salary for each experience level."""
    fig, ax = plt.subplots(figsize=(8, 5))
    table[["mean", "median"]].plot(kind="bar", ax=ax, color=["#4C72B0", "#DD8452"])
    ax.set_title("Salary by Experience Level")
    ax.set_xlabel("Experience level")
    ax.set_ylabel("Yearly salary (USD)")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(["Mean", "Median"])
    dollars_axis(ax)
    finish_chart(fig, "salary_by_experience.png")


def chart_top_titles(pay):
    """Horizontal bar chart: the 10 highest-paying titles by median salary."""
    top = pay.head(10).iloc[::-1]          # reversed so the highest bar is on top
    labels = [f"{title} (n={n})" for title, n in zip(top.index, top["records"])]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(labels, top["median"], color="#55A868")
    ax.set_title("Top 10 Highest-Paying Job Titles")
    ax.set_xlabel(f"Median yearly salary (USD) - titles with {MIN_RECORDS}+ records")
    dollars_axis(ax, axis="x")
    finish_chart(fig, "top_paying_titles.png")


def chart_remote(overall):
    """Bar chart: median salary for on-site, hybrid and remote roles."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(overall.index.astype(str), overall["median"], color="#8172B3")
    ax.set_title("Median Salary by Remote Ratio")
    ax.set_xlabel("Work arrangement")
    ax.set_ylabel("Median yearly salary (USD)")
    dollars_axis(ax)
    finish_chart(fig, "salary_by_remote_ratio.png")


# ------------------------------------------------------------------ MAIN
def main():
    raw = load_data(DATA_FILE)
    inspect_data(raw)

    df = clean_data(raw)

    experience_table = question_1(df)
    _, title_pay = question_2(df)
    remote_table, _ = question_3(df)

    print("\n=== SAVING CHARTS ===")
    chart_experience(experience_table)
    if not title_pay.empty:
        chart_top_titles(title_pay)
    chart_remote(remote_table)


if __name__ == "__main__":
    main()
