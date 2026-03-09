# mmarrder — Healthcare Analytics & Personal ETL Toolkit

A Python utility library to streamline **Healthcare ETL**, **Excel-based data structuring**, and **operational analytics** (hospital workflows, QX scheduling, reporting-ready exports).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What this library solves

In healthcare operations, a lot of value is trapped in Excel exports and semi-structured operational files.  
`mmarrder` packages reusable pipelines and utilities to:

- Transform messy Excel structures into tidy pandas DataFrames
- Produce **Excel outputs with structured tables** (ready for Power BI / SharePoint refresh)
- Provide **operational summaries and KPIs** with consistent logic

---

## Installation

From GitHub:

```bash
pip install git+https://github.com/MilovanMarrder/mmarrder.git


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

import mmarrder as mm
import pandas as pd

# 1. Connect to Clinical DB
conn = mm.db_connector(creds='secure_config')

# 2. Extract and Structure Notes
# Converts raw text blocks into structured columns
raw_data = pd.read_sql("SELECT notes FROM emr_table", conn)
structured_df = mm.leq_notes_structurer(raw_data)

# 3. Generate Report Graphics
# Automatically handles legend formatting for dense medical data
mm.plot_clinical_trends(
    structured_df, 
    metric='patient_volume',
    fix_legend=True
)

```

## Development Roadmap

Current focus is on expanding statistical capabilities for patient outcome tracking:

Basic ETL & DB Connectors (v1.1.1)

Clinical Note Structuring

Readmission Risk Calculation Module (In Progress)

LoS (Length of Stay) Prediction Helpers


Version History

Version	Type	Changes
0.0.6	Feat	Added simple connector to DB for rapid SQL querying.
0.0.5	Fix	Refactored leq_notes_structurer for better error handling.
0.0.4	Feat	Initial release of note structuring logic.
0.1.3	Fix	Resolved graphic rotation and legend duplication bugs.
0.1.4	Added normalizar_textos
0.1.6   Added tabla_calendario (generación de tabla calendario automática)

**Milovan Marrder**

_Healthcare Data Analyst | Mathematics & Business Background
LinkedIn Profile_


