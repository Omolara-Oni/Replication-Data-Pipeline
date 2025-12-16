# Replication Data Pipeline
*Reproducible data ingestion, transformation, and validation pipeline*

# Project Overview

This project replicates results from an existing research paper by rebuilding the data workflow from the original sources through to the final outputs. The goal was not to improve or extend the model, but to understand how the results were produced and whether they could be regenerated consistently using the available data.

To do this, I reconstructed the full process programmatically, working from raw datasets through a series of defined transformations and checks. The emphasis throughout the project was on clarity, traceability, and being able to rerun the entire process without manual intervention.

# Project Structure

- `src/` contains all analysis and data preparation scripts
- `data/raw/` stores original source data
- `data/outputs/` includes regression results and tables
- `docs/` holds documentation and supporting materials
  
# Approach

I approached this project by breaking the work into clear stages rather than treating it as a single analysis:

* Loading raw data directly from source files

* Applying transformations step by step using scripted logic

* Creating derived variables using documented formulas

* Checking intermediate and final outputs for consistency

* Comparing reproduced results against the original paper

By keeping each step explicit, it was easier to identify where assumptions were being made and to understand how changes in the data affected downstream results

# Data Workflow

The workflow follows a structured, repeatable flow:

## 1.Data Ingestion

* Raw source datasets are loaded as-is to allow full reprocessing

* File formats, schemas, and encodings are handled explicitly

## 2.Data Cleaning & Transformation

* Cleaning steps are applied using scripted logic

* Intermediate datasets are structured for traceability

## 3.Validation & Consistency Checks

   * Row counts, column types, and key relationships are verified

   * Outputs are checked against expected ranges and benchmarks

   * Failures are surfaced early to prevent silent errors

## 4.Output Generation

  * Final datasets are written in standardized formats

  * Results can be regenerated end-to-end from raw inputs

  * Outputs align with the original study’s reported results

# Data Model & Structure

Although this project is research-driven, the data is structured to support engineering use cases:

* Clearly defined schemas for each dataset

* Consistent naming conventions across transformations

* Explicit primary identifiers where applicable

* Separation of raw, processed, and final datasets

This organization helped keep the project manageable as the number of transformations grew.

# Key  Takeaway

Working through this replication highlighted how sensitive results can be to data handling choices, especially when working with long historical time series and incomplete records. Small differences in cleaning logic or variable definitions can have noticeable downstream effects.

Building the workflow programmatically made those dependencies visible and easier to reason about, and reinforced the importance of transparent, repeatable data processes.

# Tools Used

* Python – data ingestion, transformation and validation

* Pandas / NumPy – structured data manipulation

* Version control (Git) to track changes and iterations



# How to Run the Project
* Clone the repo: git clone <repo-url>
* Installrequirements: pip install -r requirements.txt
* Run python script: python run_pipeline.py


