# Clustering d'offres d'emploi par fouille de données textuelles

Projet de Master 1 Informatique, spécialisation Big Data, Université Paris 8.
UE Fouille de données textuelles.

Auteur : Maxime Bronny (19009314).

## Présentation du projet

L'objectif est de regrouper automatiquement des offres d'emploi en familles de
métiers à partir de leur seul contenu textuel, sans utiliser d'étiquettes
prédéfinies. Le projet met en oeuvre une démarche complète de fouille de données
textuelles : sélection d'un corpus, nettoyage du texte, représentation
vectorielle, clustering non supervisé, puis analyse et évaluation des groupes
obtenus.

Le travail est réalisé en Python, dans un notebook Jupyter unique accompagné d'un
module de prétraitement et d'un Makefile pour l'automatisation.

## Objectifs

- Construire un pipeline de bout en bout, de la donnée brute aux clusters interprétés.
- Regrouper les offres selon la proximité de leur vocabulaire (TF-IDF + K-Means).
- Évaluer la qualité du regroupement avec une métrique interne et un croisement
  avec les métadonnées du dataset (secteurs d'activité, compétences).
- Garder une démarche simple et reproductible, exécutable sur une machine personnelle.

## Données utilisées

Le corpus provient du dataset *LinkedIn Job Postings (2023)*, disponible sur Kaggle :
https://www.kaggle.com/datasets/arshkon/linkedin-job-postings

- Environ 124 000 offres en anglais (environ 123 700 après filtrage des
  descriptions trop courtes).
- Un échantillon aléatoire de 30 000 offres (graine fixe) est utilisé pour le
  clustering, ce qui offre un bon compromis entre couverture et temps de calcul.
- Champs exploités pour le clustering : `title` et `description`.

Le fichier principal `Données/postings.csv` (environ 500 Mo) n'est pas versionné
car il dépasse la limite de taille de GitHub. Il doit être téléchargé depuis
Kaggle et placé dans le dossier `Données/` avant l'exécution.

Les fichiers de validation externe, eux, sont versionnés et permettent de croiser
les clusters avec des catégories métier réelles :

- `jobs/job_industries.csv` + `mappings/industries.csv` : secteurs d'activité (couverture environ 98,9 %).
- `jobs/job_skills.csv` + `mappings/skills.csv` : catégories de compétences (couverture environ 98,6 %).

Les autres fichiers présents (`compagnies/`, salaires, avantages) ne sont pas
utilisés pour le clustering.

## Architecture du projet

```
.
  README.md
  Makefile                 # automatisation (install, run, docs, clean)
  requirements.txt         # dépendances Python
  notebooks/
    01_clustering_offres_emploi_executed.ipynb   # notebook principal (analyse complète)
  src/
    preprocessing.py       # nettoyage textuel (importé par le notebook)
    __init__.py
  scripts/
    generate_presentation_figures.py   # régénère certaines figures pour la présentation
  outputs/                 # figures PNG générées par le notebook
  Données/                 # postings.csv (non versionné) + jobs/ + mappings/ + compagnies/
  docs/
    rapport/               # rapport de projet (PDF)
    technique/             # documentation technique (PDF)
    utilisateur/           # documentation utilisateur (PDF)
    cahier_des_charges/    # cahier des charges (PDF)
    presentation/          # support de soutenance
```

Le notebook s'exécute depuis le dossier `notebooks/` : il utilise des chemins
relatifs vers `../Données/` et `../outputs/`.

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

## Exécution

Lancer le notebook en mode interactif :

```bash
make notebook
```

Ou directement :

```bash
jupyter notebook notebooks/01_clustering_offres_emploi_executed.ipynb
```

Exécuter le notebook de bout en bout sans interaction (utile pour la reproductibilité) :

```bash
make run
```

Autres commandes utiles :

| Commande | Description |
|----------|-------------|
| `make docs` | Compile la documentation LaTeX (rapport, technique, utilisateur) en PDF |
| `make clean` | Supprime les fichiers temporaires |
| `make clean-outputs` | Supprime les figures générées |
| `make tree` | Affiche l'arborescence du projet |

## Pipeline méthodologique

1. Chargement des données et échantillonnage de 30 000 offres (graine fixe).
2. Exploration statistique du corpus (longueurs, valeurs manquantes, niveaux d'expérience).
3. Prétraitement du texte (`src/preprocessing.py`) : suppression du HTML, retrait
   du boilerplate juridique et RH récurrent, passage en minuscules, suppression des
   caractères non alphabétiques, retrait des stopwords (NLTK + mots propres au
   domaine), puis lemmatisation.
4. Vectorisation TF-IDF : 10 000 termes, unigrammes et bigrammes, `min_df=50`, `max_df=0.85`.
5. Clustering K-Means avec k=8. Le nombre de clusters a été choisi à partir de la
   méthode du coude, du score silhouette et de l'interprétabilité des groupes, cette
   dernière étant déterminante car les indicateurs internes sont peu discriminants
   sur des données textuelles en haute dimension.
6. Comparaison avec DBSCAN (sur des données réduites par TruncatedSVD), conservée
   comme point de comparaison.
7. Analyse des clusters : termes dominants par groupe, offres les plus proches du
   centroïde, projection 2D par TruncatedSVD.
8. Évaluation : score silhouette, puis croisement des clusters avec les métadonnées
   LinkedIn (secteurs, compétences, niveau d'expérience).

Technologies : Python, pandas, numpy, scikit-learn, nltk, matplotlib, seaborn, Jupyter.

## Résultats principaux

Le pipeline produit 8 clusters. Plusieurs d'entre eux sont nettement
interprétables : santé et soins, informatique et ingénierie, commerce de détail,
management, et maintenance technique. Un cluster joue le rôle de groupe résiduel
et rassemble les offres au vocabulaire peu spécifique.

Le score silhouette global est faible (environ 0,01), ce qui est attendu pour du
clustering de texte en haute dimension : la distance euclidienne y est peu
discriminante. L'analyse des termes dominants et le croisement avec les secteurs
et compétences LinkedIn confirment néanmoins la cohérence de plusieurs groupes.

Les figures correspondantes sont enregistrées dans `outputs/` (courbe du coude et
silhouette, tailles des clusters, projection 2D, croisements avec les métadonnées).

## Limites du projet

- TF-IDF capture la similarité de vocabulaire, pas la sémantique : deux offres
  portant sur le même métier mais rédigées différemment peuvent être séparées.
- K-Means affecte chaque offre à un cluster sans possibilité de rejet, ce qui
  explique l'existence d'un cluster résiduel généraliste.
- Le score silhouette ne suffit pas à juger seul la qualité du clustering textuel ;
  l'analyse qualitative et le croisement avec les métadonnées le complètent.
- Le corpus est en anglais et le prétraitement est spécifique à cette langue.
- Le corpus n'est pas dédupliqué : quelques offres quasi identiques d'un même
  employeur peuvent former de petits groupes atypiques.

## Livrables

- Le notebook Jupyter dans `notebooks/`.
- Le rapport, la documentation technique, la documentation utilisateur et le cahier
  des charges (PDF dans `docs/`).
- Le support de présentation dans `docs/presentation/`.
- Les figures générées dans `outputs/`.

## Reproductibilité

- Une graine aléatoire fixe (42) contrôle l'échantillonnage et l'initialisation de K-Means.
- Les dépendances sont listées dans `requirements.txt` et installées dans un
  environnement virtuel.
- `make run` réexécute le notebook de bout en bout, sans intervention manuelle.
- Le fichier `postings.csv` doit être présent dans `Données/` (voir la section
  Données utilisées).

## Auteur

Maxime Bronny (19009314), Master 1 Informatique Big Data, Université Paris 8.
