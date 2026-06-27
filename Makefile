# Nom : Makefile
# Rôle : Commandes principales pour installer, exécuter et nettoyer le projet.
# Auteur : Maxime BRONNY
# Version : V1
# Cadre : UE Fouille de données textuelles - Master 1 Informatique Big Data - Université Paris 8
# Usage : Exécuter les commandes avec make depuis la racine du projet.

PYTHON     = venv/bin/python
PIP        = venv/bin/pip
JUPYTER    = venv/bin/jupyter
NOTEBOOK   = notebooks/01_clustering_offres_emploi_executed.ipynb

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
		echo "OK - venv créé." ; \
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
		--output 01_clustering_offres_emploi_executed.ipynb \
		$(NOTEBOOK)
	@echo "Exécution terminée - sorties mises à jour."

# ---- Documentation ---------------------------------------------------------

# Documents LaTeX à compiler : un docs/<nom>/main.tex par document.
# (présentation et cahier des charges exclus : pas de chaîne main.tex → IED ici)
DOC_DIRS = rapport technique utilisateur

docs: ## Compile les documents LaTeX (rapport, technique, utilisateur) en PDF
	@for d in $(DOC_DIRS); do \
		echo "Compilation de docs/$$d ..." ; \
		( cd docs/$$d && \
		  pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && \
		  pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null ) \
		  || { echo "  ÉCHEC - voir docs/$$d/main.log" ; exit 1 ; } ; \
		ied=$$(ls docs/$$d/IED-M1-*.pdf 2>/dev/null | head -n1) ; \
		if [ -n "$$ied" ]; then \
			cp -f docs/$$d/main.pdf "$$ied" ; \
			echo "  OK → $$ied" ; \
		else \
			echo "  OK → docs/$$d/main.pdf (aucun livrable IED-M1-*.pdf à mettre à jour)" ; \
		fi ; \
	done
	@echo "Documentation compilée."

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
