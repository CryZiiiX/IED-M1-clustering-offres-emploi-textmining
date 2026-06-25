# Clustering d'offres d'emploi - Fouille de données textuelles

Projet de Master 1 Informatique, spécialisation Big Data - Université Paris 8.
UE Fouille de données textuelles.

**Maxime Bronny - 19009314**

## Présentation

Regroupement automatique d'offres d'emploi LinkedIn en catégories
cohérentes à partir de leur contenu textuel, sans labels préexistants.

Le pipeline repose sur une vectorisation TF-IDF, un clustering K-Means
(k=8) et une validation externe via les métadonnées LinkedIn (secteurs
d'activité et compétences).

Corpus : ~124 000 offres en anglais (~123 700 après filtrage), dont un
échantillon aléatoire de 30 000 offres est utilisé pour le clustering
(graine fixe pour la reproductibilité).
Temps d'exécution : environ 5 minutes.

## Structure du projet

```
.
├── notebooks/
│   └── 01_clustering_offres_emploi_executed.ipynb  # analyse complète
├── src/
│   ├── __init__.py
│   └── preprocessing.py            # nettoyage textuel
├── scripts/
│   └── generate_presentation_figures.py  # figures pour slides
├── Données/
│   ├── postings.csv                # dataset principal (non versionné)
│   ├── compagnies/                 # infos entreprises
│   ├── jobs/                       # industries, skills, salaires
│   └── mappings/                   # tables de référence
├── outputs/                        # figures PNG générées
├── docs/
│   ├── utilisateur/                # doc utilisateur (PDF)
│   ├── technique/                  # doc technique (PDF)
│   ├── rapport/                    # rapport de projet (PDF)
│   ├── cahier_des_charges/         # cahier des charges
│   └── cours_MOODLE_Paris8/        # support de cours
├── Makefile                        # automatisation
├── requirements.txt                # dépendances Python
└── README.md
```

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"
```

Ou via le Makefile :

```bash
make venv && make install
```

## Utilisation

```bash
make notebook
```

Ou directement :

```bash
jupyter notebook notebooks/01_clustering_offres_emploi_executed.ipynb
```

Exécution non interactive :

```bash
make run
```

### Autres commandes

| Commande | Description |
|----------|-------------|
| `make docs` | Compiler la doc LaTeX en PDF |
| `make clean` | Supprimer les fichiers temporaires |
| `make clean-outputs` | Supprimer les figures générées |
| `make tree` | Afficher l'arborescence du projet |

## Données

Le dataset principal (`postings.csv`) provient du dataset
*LinkedIn Job Postings (2023)* publié sur Kaggle
(https://www.kaggle.com/datasets/arshkon/linkedin-job-postings)
et n'est pas versionné (516 Mo).
Champs utilisés : `title` et `description`.

Fichiers de validation externe dans `Données/` :
- `jobs/job_industries.csv` + `mappings/industries.csv` - secteurs (~98.8%)
- `jobs/job_skills.csv` + `mappings/skills.csv` - compétences (~98.6%)

## Sorties

Le notebook produit 8 figures dans `outputs/` :

- `elbow_silhouette.png` - coude et silhouette
- `taille_clusters.png` - répartition des clusters
- `clusters_2d.png` - projection 2D (TruncatedSVD)
- `distribution_longueurs.png` - longueurs des textes
- `distribution_tokens.png` - nombre de tokens
- `experience_par_cluster.png` - expérience par cluster
- `industries_par_cluster.png` - secteurs par cluster
- `skills_par_cluster.png` - compétences par cluster

## Documentation

| Document | Dossier |
|----------|---------|
| Doc utilisateur | `docs/utilisateur/` |
| Doc technique | `docs/technique/` |
| Rapport | `docs/rapport/` |
| Cahier des charges | `docs/cahier_des_charges/` |
| Cours (support) | `docs/cours_MOODLE_Paris8/` |

## Dépendances

Python 3.10+, pandas, numpy, scikit-learn, nltk,
matplotlib, seaborn, jupyter.

Liste complète dans `requirements.txt`.
