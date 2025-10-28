.PHONY: all clean watch

# Variables
DATA = cv.toml
TEMPLATE = templates/base.tex.j2
OUTPUT_DIR = output
TEX_OUTPUT = $(OUTPUT_DIR)/cv.tex
PDF_NAME = $(shell python3 -c "import importlib, sys; toml = importlib.import_module('tomllib' if sys.version_info >= (3, 11) else 'tomli'); print(toml.load(open('cv.toml','rb')).get('output','cv.pdf'))")
PDF_OUTPUT = $(OUTPUT_DIR)/$(PDF_NAME)

# Default target
all: $(PDF_OUTPUT)

# Render LaTeX from TOML + Jinja2
$(TEX_OUTPUT): $(DATA) $(TEMPLATE) render.py
	@mkdir -p $(OUTPUT_DIR)
	@python3 render.py

# Build PDF from LaTeX
$(PDF_OUTPUT): $(TEX_OUTPUT)
	@cd $(OUTPUT_DIR) && xelatex -interaction=batchmode cv.tex > /dev/null 2>&1 && mv -f cv.pdf "$(PDF_NAME)"
	@echo "✓ PDF generated: $(PDF_OUTPUT)"

# Clean
clean:
	@rm -rf $(OUTPUT_DIR)/*
	@echo "✓ Cleaned output directory"

# Watch for changes
watch:
	@echo "Watching data/templates for changes..."
	@{ find templates -type f -name '*.tex.j2'; echo $(DATA); } | entr -r make
