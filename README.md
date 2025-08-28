# ANR-Access-ERC

Codebase hosting the pipeline used for the ANR/Access-ERC of project OBJECTive.

## Pipeline

The pipeline folder contains multiple Jupyter notebooks controled by a main makefile which handle order, notebooks groups, logs, files, ... 
It takes as inputs PDFs (images) of auction catalogues from the 19th century; and outputs CSV tables containing all object listed in all auction catalogues parsed, and the vocabulary extracted from them.

The make recipe `make help` displays everything doable with the pipeline.

## Imports

The import folder contains all necessaries code to import data into the project's SPARQL endpoint.
`make import-graphdb` starts the upload.

## Analysis

In the analysis folder, an exploratory analysis directed by researcher questions is present.
It is runnable by running "make analyze". This recipe will create an output HTML files containing interactive charts.

---

To know more about our project, visit our Zenodo publication: **OBJECTive - Objects Through the Art Market: A Global Perspective**