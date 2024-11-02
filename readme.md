# Open Data Quality Analyzer for Nuevo León

## Overview

The Open Data Quality Analyzer is a collaborative project aimed at evaluating and enhancing the quality of open government data in Nuevo León. This tool aligns with the goals of data transparency and citizen engagement by assessing data standards and providing actionable insights to improve data usability, completeness, and accessibility.

## Project Structure

- **data_quality**: Core Python modules for data validation:
  - `technical.py`: Implements technical checks for data quality.
  - `standards.py`: Contains functions to assess data against international standards.
  - `open_data.py`: Interfaces with open data sources, retrieving and formatting data for analysis.
- **data**: Sample data files representing open datasets related to public services, community diagnostics, labor satisfaction, and more.
- **example_output**: JSON files showing examples of data evaluation, grading, and filtration processes.
- **notebooks**: Jupyter notebooks providing step-by-step analysis, validation routines, and demonstrations of the standards applied to open data.

## Installation

1. Clone this repository.
2. Install dependencies using:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Data Validation**:
   Use `data_quality/technical.py` and `data_quality/standards.py` modules to run technical and standards-based checks on datasets.
2. **Evaluation and Grading**:
   Run notebooks in the `notebooks` folder for interactive data grading and quality evaluation.
3. **Example Outputs**:
   Review `example_output` JSON files for examples of graded and evaluated datasets.

## Contributing

This project welcomes contributions from developers, data scientists, and citizens interested in data quality and transparency. Feel free to open issues or submit pull requests.

## License

This project is distributed under the Creative Commons CC BY-SA 4.0 license.