# ANR-Access-ERC

Codebase hosting the pipeline used for the ANR/Access-ERC of project OBJECTive.

## Pipeline

### Input

Pipeline inputs are PDFs version of auction catalogues from the 19th century, mainly located in Paris. 

### Output

Pipeline outputs are CSV files containing:
- All objects listed in all auction catalogues parsed
- Vocabulary extracted from the object list

### How to run

The pipeline contains multiple Jupyter notebooks controled by a main makefile which handle order, notebooks groups, logs, files, ...

## Imports

## Analysis

In the analysis folder, an exploratory analysis directed by researcher questions is present.

### How to run

The notebook can be launched by the makefile recipe "analyze" which creates a html file with all interactive charts.
