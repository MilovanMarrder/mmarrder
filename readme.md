# mmarrder: Healthcare Analytics & ETL Toolkit 🏥📊

> A robust Python utility library designed to streamline **Clinical Data Engineering**, **Automated Reporting**, and **Healthcare ETL pipelines**.

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.6-blue)](https://pypi.org/project/mmarrder/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Working in healthcare analytics often involves repetitive tasks: cleaning messy EMR exports, standardizing clinical notes, and generating recurring regulatory reports. 

**`mmarrder`** encapsulates established workflows into reusable modules, allowing analysts to focus on insights rather than data wrangling. It bridges the gap between raw database extraction and polished stakeholder reporting.

## Key Features

### Clinical Data Structuring
- **Unstructured Text Parsing**: Tools to extract structured data from clinical notes (e.g., `leq_notes_structurer`), converting free-text medical records into analyzable datasets.
- **Data Validation**: Automated checks to ensure data integrity before analysis.

### ETL & Connectivity
- **Seamless DB Connection**: Wrapper functions for secure and rapid connections to hospital SQL databases (`simple connector to db`).
- **Automated Extraction**: Streamlined queries to pull large datasets for daily operational dashboards.

### Reporting & Visualization
- **Parametric Reporting**: Generate standardized visual reports ensuring consistency across different timeframes.
- **Smart Legends & Tables**: Solves common plotting issues like duplication of table legends (`duplication_table_as_legend`), optimized for medical publication standards.

## Installation

Install the latest version directly from the repository:

```bash
pip install git+https://github.com/MilovanMarrder/mmarrder.git
