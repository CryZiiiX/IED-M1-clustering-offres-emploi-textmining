# =============================================================================
# Makefile — Clustering d'offres d'emploi par fouille de données textuelles
# M1 Informatique Big Data — Fouille de données textuelles
# =============================================================================

PYTHON     = venv/bin/python
PIP        = venv/bin/pip
JUPYTER    = venv/bin/jupyter
NOTEBOOK   = notebooks/01_clustering_offres_emploi.ipynb

.PHONY: help venv install notebook run clean clean-outputs docs tree

# ---- Cible par défaut -----------------------------------------------------

help: ## Affiche les cibles disponibles
	@echo ""
	@echo "Cibles disponibles :"
	@echo "---------------------"
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
		| awk -F ':.*## ' '{printf "  make %-16s %s\n", $$1, $$2}'
	@echo ""

# ---- Environnement --------------------------------------------------------

venv: ## Crée l'environnement virtuel
	@if [ ! -d venv ]; then \
		echo "Création de l'environnement virtuel..." ; \
		python3 -m venv venv ; \
		echo "OK — venv créé." ; \
	else \
		echo "venv existe déjà." ; \
	fi

install: venv ## Installe les dépendances (requirements.txt)
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt -q
	@echo "Dépendances installées."

# ---- Exécution -------------------------------------------------------------

notebook: install ## Lance Jupyter Notebook sur le notebook principal
	$(JUPYTER) notebook $(NOTEBOOK)

run: install ## Exécute le notebook en non-interactif (reproductibilité)
	@echo "Exécution du notebook..."
	$(JUPYTER) nbconvert --to notebook --execute \
		--output 01_clustering_offres_emploi.ipynb \
		$(NOTEBOOK)
	@echo "Exécution terminée — sorties mises à jour."

# ---- Documentation ---------------------------------------------------------

docs: ## Compile la documentation LaTeX (docs/main.tex → main.pdf)
	cd docs && pdflatex -interaction=nonstopmode main.tex
	cd docs && pdflatex -interaction=nonstopmode main.tex
	@echo "Documentation compilée → docs/main.pdf"

# ---- Nettoyage -------------------------------------------------------------

clean: ## Supprime les fichiers temporaires (caches Python, checkpoints Jupyter)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	rm -f docs/*.aux docs/*.log docs/*.out docs/*.toc docs/*.fls docs/*.fdb_latexmk 2>/dev/null || true
	@echo "Fichiers temporaires supprimés."

clean-outputs: ## Supprime les sorties générées (outputs/)
	rm -f outputs/*.png
	@echo "Sorties supprimées (outputs/)."

# ---- Utilitaires -----------------------------------------------------------

tree: ## Affiche la structure utile du projet
	@tree -I 'venv|__pycache__|.ipynb_checkpoints|Données|.claude' \
		--dirsfirst -a --charset utf-8 2>/dev/null || \
		find . -path './venv' -prune -o \
		       -path './.claude' -prune -o \
		       -path './Données' -prune -o \
		       -name '__pycache__' -prune -o \
		       -name '.ipynb_checkpoints' -prune -o \
		       -name '*.pyc' -prune -o \
		       -print | sort
