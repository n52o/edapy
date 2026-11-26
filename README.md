# edapy

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.1.0-orange)

**edapy** is a lightweight, zero-boilerplate Python library for fast Exploratory Data Analysis (EDA). Clean datasets, inspect distributions, detect IQR outliers, and export full statistical summaries in a single line of code.

## Features

- **One-line Load & Clean (`edapy.load`)**: Reads CSV files, removes duplicate rows automatically, reports missing values, and previews the dataset.
- **Smart Column Stats (`edapy.stats`)**: Computes `sum`, `mean`, `median`, `Q1`, `Q3`, `IQR`, lower/upper bounds, and outlier counts—automatically encoding text/categorical columns into numeric values without throwing errors.
- **Instant Summary Table (`edapy.summary`)**: Generates a complete EDA summary table across all or selected columns and exports it directly to CSV.

## Installation

```bash
pip install edapy-tools