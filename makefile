
# Default variables
OBJECTIVE_CORRECTION_RESET ?= no

help:
	@echo "[make catalog-validation]: make sure the CLI param *catalog* is present."
	@echo "[make begin-validation]: make sure the CLI param *begin* is present."
	@echo "/!\ [make transcription catalog=catalog_name]: transcribe the given catalog (COST)"
	@echo "/!\ [make list catalog=catalog_name begin=4]: extract the list of object from the transcribed catalog; start at given page (COST)"
	@echo "/!\ [make objects catalog=catalog_name]: parse the objects descriptions to extract information (COST)"
	@echo "[make verify catalog=catalog_name]: check the content of each columns (Need a Ollama server running)"
	@echo "[make lemmas catalog=catalog_name]: transform information into lemmas (with spaCy)"
	@echo "[make authors catalog=catalog_name]: look for author information in description and validate it (Need a Ollama server running)"
	@echo "[make merge]: merge all objects.csv of all catalogs"
	@echo "[make correction]: apply corrections on all-objects.csv"
	@echo "[make vocabulary]: extract all vocabulary from all-objects.csv"
	@echo "[make round-1]: run all the first part of the pipeline, transcription + list + objects (COST)"
	@echo "[make round-2]: run all the second part of the pipeline, verify + lemmas + authors (RESOURCE INTENSIVE)"
	@echo "[make round-3]: run all the third part of the pipeline, merge + correction + vocabulary"
	@echo "[make all]: run all 3 parts, round-1 + round-2 + round-3"

### Param validation

catalog-validation:
	@if [ -z "$(catalog)" ]; then \
		echo "Error: [catalog] is required"; \
		exit 1; \
	fi

begin-validation:
	@if [ -z "$(begin)" ]; then \
		echo "Error: [begin] is required"; \
		exit 1; \
	fi


### ROUND 1 ###

transcription: catalog-validation
	@\
	echo "[PIPELINE-10]: TRANSCRIPTION"; \
	export OBJECTIVE_MODE=pipeline; \
	export OBJECTIVE_CATALOG=$(catalog); \
	cd pipeline; \
	python3.10 run-notebook.py 10-transcription.ipynb; \
	echo "-----"

list: catalog-validation begin-validation
	@\
	echo "[PIPELINE-11]: LIST"; \
	export OBJECTIVE_MODE=pipeline; \
	export OBJECTIVE_CATALOG=$(catalog); \
	export OBJECTIVE_PAGE_BEGIN=$(begin); \
	export OBJECTIVE_PAGE_END=$(end); \
	cd pipeline; \
	python3.10 run-notebook.py 11-list.ipynb; \
	echo "-----"

objects: catalog-validation
	@\
	echo "[PIPELINE-12]: OBJECTS"; \
	export OBJECTIVE_MODE=pipeline; \
	export OBJECTIVE_CATALOG=$(catalog); \
	cd pipeline; \
	python3.10 run-notebook.py 12-objects.ipynb; \
	echo "-----"


### ROUND 2 ###

verify:
	@\
	echo "[PIPELINE-20]: VERIFY"; \
	export OBJECTIVE_MODE=pipeline; \
	export OBJECTIVE_CATALOG=$(catalog); \
	cd pipeline; \
	python3.10 run-notebook.py 20-verify.ipynb; \
	echo "-----"

lemmas:
	@\
	echo "[PIPELINE-21]: LEMMAS"; \
	export OBJECTIVE_MODE=pipeline; \
	export OBJECTIVE_CATALOG=$(catalog); \
	cd pipeline; \
	python3.10 run-notebook.py 21-lemmas.ipynb; \
	echo "-----"

authors:
	@\
	echo "[PIPELINE-22]: AUTHORS"; \
	export OBJECTIVE_MODE=pipeline; \
	export OBJECTIVE_CATALOG=$(catalog); \
	cd pipeline; \
	python3.10 run-notebook.py 22-authors.ipynb; \
	echo "-----"

periods:
	@\
	echo "[PIPELINE-23]: PERIODS"; \
	export OBJECTIVE_MODE=pipeline; \
	export OBJECTIVE_CATALOG=$(catalog); \
	cd pipeline; \
	python3.10 run-notebook.py 23-periods.ipynb; \
	echo "-----"


### ROUND 3 ###

merge:
	@\
	echo "[PIPELINE-30]: MERGE"; \
	export OBJECTIVE_MODE=pipeline; \
	cd pipeline; \
	python3.10 run-notebook.py 30-merge.ipynb; \
	echo "-----"

correction:
	@\
	echo "[PIPELINE-31]: CORRECTION"; \
	export OBJECTIVE_MODE=pipeline; \
	cd pipeline; \
	python3.10 run-notebook.py 31-corrections.ipynb; \
	echo "-----"

vocabulary:
	@\
	echo "[PIPELINE-32]: VOCABULARY"; \
	export OBJECTIVE_MODE=pipeline; \
	export OBJECTIVE_CATALOG=$(catalog); \
	cd pipeline; \
	python3.10 run-notebook.py 32-vocabulary.ipynb; \
	echo "-----"


### Pipeline ###

round-1: catalog-validation begin-validation transcription list objects
round-2: verify lemmas authors periods
round-3: merge correction vocabulary
all: catalog-validation begin-validation round-1 round-2 round-3
round-2-3: catalog-validation round-2 round-3