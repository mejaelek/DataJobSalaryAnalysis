 <!--
  HOW TO USE THIS FILE
  - Replace every [FILL IN ...] marker, then delete all of these HTML comments.
  - Do NOT mention that this is a class assignment (the template forbids it).
  - Use good spelling and grammar: this page is public on GitHub.
-->

# Overview

This project analyses real salary data for data science, analytics and machine-learning jobs. I wrote it to practise the everyday workflow of a data analyst: load a raw CSV file, inspect and clean it, ask clear questions, answer them with Pandas, and present the evidence in charts.

**Dataset:** [Data Science Salaries 2023](https://www.kaggle.com/datasets/arnabchaki/data-science-salaries-2023) on Kaggle, shared by RandomArnab: 3,755 rows covering [2023]. Each row is one salary record with the job title, experience level, salary in USD, remote-work ratio, company size and country. [The dataset page describes the records as data science job salaries, and the author credits no further source]. My analysis removes 1,171 exact duplicate rows, leaving 2,584 records. on Kaggle, [3,755] rows covering [11]. Each row is one salary record with the job title, experience level, salary in USD, remote-work ratio, company size and country. [on the Kaggle page.]

**Why I wrote it:** I am building towards a career as a data analyst / engineer / scientist, and I wanted to see what this market actually pays and how pay changes with experience, job title and remote work. It also gave me hands-on practice with Pandas and Matplotlib.

**How to run it:**

1. Download the dataset from the link above and save the CSV as `data/ds_salaries.csv`.
2. Create and activate a virtual environment, then run `pip install -r requirements.txt`.
3. Run `python salary_analysis.py`. Tables print to the terminal and charts are saved to the `charts/` folder.

[Software Demo Video](https://youtu.be/GUhYZl5B0jQ)

# Data Analysis Results

<!-- Write each answer in 3-5 sentences: the answer, the numbers that prove it, and one limit. -->

**Question 1: How does average yearly salary (USD) change across experience levels?**

[FILL IN: your answer, with the actual numbers from the program output and one caveat such as sample size.]

![Salary by experience ](charts/salary_by_experience.png)

**Question 2: Which job titles appear most often, and which of those pay the highest median salary?**

[FILL IN: your answer, with the numbers and the minimum-records rule you used.]

![Top paying job titles](charts/top_paying_titles.png)

**Question 3 (extra): Does the remote-work ratio affect salary?**

[FILL IN: your answer, including what happened when you compared at the same experience level.]

![Salary by remote ratio](charts/salary_by_remote_ratio.png)

**Limits of this analysis:** [FILL IN: for example, the data is self-reported, covers mainly data and AI roles, and some groups have few records.]

# Development Environment

- Visual Studio Code on Windows, with the Microsoft Python extension
- Git and GitHub for version control
- Python [FILL IN: version from `python --version`]
- Libraries: Pandas [FILL IN: version] for loading, cleaning, grouping and sorting the data, and Matplotlib [FILL IN: version] for the charts

# Useful Websites

* [Pandas 10 Minutes Tutorial](https://pandas.pydata.org/docs/user_guide/10min.html)
* [Pandas Getting Started Tutorials](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html)
* [Matplotlib Documentation](https://matplotlib.org/)
* [Kaggle Datasets](https://www.kaggle.com/datasets)
* [FILL IN: any other page that really helped you]

# Future Work

* Repeat the analysis for a single year at a time to separate pay growth from the other effects
* Compare salaries by country and company size
* Load the data into a SQL database and answer the same questions with SQL queries
* Add a statistical test or confidence ranges for the groups that have few records
