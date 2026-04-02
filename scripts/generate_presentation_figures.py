"""
Génère des figures optimisées pour la projection en diaporama.
Polices plus grandes, meilleur contraste, meilleure lisibilité.

Usage (depuis la racine du projet, avec le venv activé) :
    python scripts/generate_presentation_figures.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from src.preprocessing import clean_text, build_corpus_text

# --- Style global pour présentation ---
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 13,
    'figure.dpi': 200,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

SEED = 42
N_SAMPLE = 30_000
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')
K_RANGE = range(2, 16)
BEST_K = 8


def load_and_prepare():
    """Charge et prépare les données (même pipeline que le notebook)."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'Données')

    print("Chargement des données...")
    df = pd.read_csv(os.path.join(data_dir, 'postings.csv'),
                     usecols=['job_id', 'title', 'description', 'formatted_experience_level'])
    df = df.dropna(subset=['title', 'description'])
    df = df[df['description'].str.len() >= 100]
    df = df.sample(n=N_SAMPLE, random_state=SEED).reset_index(drop=True)

    print("Prétraitement textuel...")
    df['corpus_text'] = df.apply(build_corpus_text, axis=1)
    df['clean_text'] = df['corpus_text'].apply(clean_text)
    df = df[df['clean_text'].str.len() > 0].reset_index(drop=True)

    return df


def vectorize(df):
    """Vectorisation TF-IDF."""
    print("Vectorisation TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=10_000,
        max_df=0.85,
        min_df=50,
        sublinear_tf=True,
        ngram_range=(1, 2),
    )
    X = vectorizer.fit_transform(df['clean_text'])
    return X, vectorizer


def compute_elbow_silhouette(X):
    """Calcule inertie et silhouette pour k = 2..15."""
    inertias, sil_scores = [], []
    for k in K_RANGE:
        print(f"  K-Means k={k}...")
        km = KMeans(n_clusters=k, n_init=10, max_iter=300, random_state=SEED)
        km.fit(X)
        inertias.append(km.inertia_)
        # Silhouette sur un sous-échantillon pour la vitesse
        idx = np.random.RandomState(SEED).choice(X.shape[0], min(10_000, X.shape[0]), replace=False)
        sil_scores.append(silhouette_score(X[idx], km.labels_[idx]))
    return inertias, sil_scores


def cluster_final(X, df):
    """Clustering final avec k=8."""
    print(f"Clustering final k={BEST_K}...")
    km = KMeans(n_clusters=BEST_K, n_init=10, max_iter=300, random_state=SEED)
    df['cluster'] = km.fit_predict(X)
    return km


def load_industries(df):
    """Charge les secteurs d'activité LinkedIn."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'Données')
    job_ind = pd.read_csv(os.path.join(data_dir, 'jobs', 'job_industries.csv'))
    ind_map = pd.read_csv(os.path.join(data_dir, 'mappings', 'industries.csv'))
    job_ind = job_ind.merge(ind_map, left_on='industry_id', right_on='industry_id', how='left')
    df = df.merge(job_ind[['job_id', 'industry_name']], on='job_id', how='left')
    return df


# --- FIGURES ---

def fig_elbow_silhouette(inertias, sil_scores):
    """Figure coude + silhouette, optimisée pour projection."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    axes[0].plot(list(K_RANGE), inertias, 'o-', color='#1a5276',
                 linewidth=2.5, markersize=8)
    axes[0].set_title('Méthode du coude (inertie)', fontweight='bold')
    axes[0].set_xlabel('Nombre de clusters (k)')
    axes[0].set_ylabel('Inertie')
    axes[0].set_xticks(list(K_RANGE))
    axes[0].axvline(x=BEST_K, color='#c0392b', linestyle='--', linewidth=1.5,
                    alpha=0.7, label=f'k = {BEST_K}')
    axes[0].legend(fontsize=14)

    axes[1].plot(list(K_RANGE), sil_scores, 'o-', color='#e67e22',
                 linewidth=2.5, markersize=8)
    axes[1].set_title('Score silhouette moyen', fontweight='bold')
    axes[1].set_xlabel('Nombre de clusters (k)')
    axes[1].set_ylabel('Silhouette')
    axes[1].set_xticks(list(K_RANGE))
    axes[1].axvline(x=BEST_K, color='#c0392b', linestyle='--', linewidth=1.5,
                    alpha=0.7, label=f'k = {BEST_K}')
    axes[1].legend(fontsize=14)

    plt.tight_layout(w_pad=3)
    path = os.path.join(OUTPUT_DIR, 'elbow_silhouette.png')
    plt.savefig(path)
    plt.close()
    print(f"  Sauvé : {path}")


def fig_taille_clusters(df):
    """Taille des clusters, optimisée."""
    cluster_names = {
        0: 'Terrain', 1: 'Maintenance', 2: 'Commerce',
        3: 'Résiduel', 4: 'Santé', 5: 'IT',
        6: 'Dir. comm.', 7: 'Management'
    }
    sizes = df['cluster'].value_counts().sort_index()
    colors = ['#2980b9'] * 8
    colors[3] = '#bdc3c7'  # résiduel en gris

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(8), sizes.values, color=colors, edgecolor='white', linewidth=1.5)

    for i, (bar, val) in enumerate(zip(bars, sizes.values)):
        label = f"{cluster_names[i]}\n({val:,})"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 80,
                label, ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_xlabel('Cluster')
    ax.set_ylabel("Nombre d'offres")
    ax.set_title('Répartition des 8 clusters', fontweight='bold')
    ax.set_xticks(range(8))
    ax.set_xticklabels([f'C{i}' for i in range(8)])
    ax.set_ylim(0, max(sizes.values) * 1.18)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'taille_clusters.png')
    plt.savefig(path)
    plt.close()
    print(f"  Sauvé : {path}")


def fig_industries(df):
    """Heatmap industries, optimisée pour lisibilité en projection."""
    top_industries = df['industry_name'].value_counts().head(10).index
    df_sub = df[df['industry_name'].isin(top_industries)]
    ct = pd.crosstab(df_sub['cluster'], df_sub['industry_name'])
    ct_pct = ct.div(ct.sum(axis=0), axis=1)

    # Noms de clusters lisibles
    cluster_labels = {
        0: 'C0 Terrain', 1: 'C1 Maintenance', 2: 'C2 Commerce',
        3: 'C3 Résiduel', 4: 'C4 Santé', 5: 'C5 IT',
        6: 'C6 Dir. comm.', 7: 'C7 Management'
    }
    ct_pct.index = [cluster_labels.get(i, f'C{i}') for i in ct_pct.index]

    # Noms de secteurs raccourcis pour lisibilité
    short_names = {
        'Hospitals and Health Care': 'Santé',
        'IT Services and IT Consulting': 'IT Services',
        'Staffing and Recruiting': 'Recrutement',
        'Retail': 'Commerce détail',
        'Manufacturing': 'Industrie',
        'Financial Services': 'Finance',
        'Construction': 'Construction',
        'Software Development': 'Logiciel',
        'Real Estate': 'Immobilier',
        'Administrative': 'Admin.',
    }
    ct_pct.columns = [short_names.get(c, c[:15]) for c in ct_pct.columns]

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.heatmap(ct_pct, annot=True, fmt='.0%', cmap='YlOrRd',
                linewidths=1, cbar_kws={'label': 'Proportion', 'shrink': 0.8},
                annot_kws={'size': 13, 'fontweight': 'bold'},
                ax=ax)
    ax.set_title("Répartition des secteurs d'activité par cluster",
                 fontweight='bold', pad=15)
    ax.set_xlabel('Secteur LinkedIn', labelpad=10)
    ax.set_ylabel('Cluster', labelpad=10)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right', fontsize=13)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=13)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'industries_par_cluster.png')
    plt.savefig(path)
    plt.close()
    print(f"  Sauvé : {path}")


# --- MAIN ---

def main():
    print("=" * 60)
    print("Génération des figures optimisées pour la présentation")
    print("=" * 60)

    df = load_and_prepare()
    X, vectorizer = vectorize(df)

    print("\nCalcul coude + silhouette...")
    inertias, sil_scores = compute_elbow_silhouette(X)

    cluster_final(X, df)

    print("\nGénération des figures...")
    fig_elbow_silhouette(inertias, sil_scores)
    fig_taille_clusters(df)  # avant merge industries (pas de duplication)

    df_with_ind = load_industries(df)
    fig_industries(df_with_ind)

    print("\nTerminé. Les figures ont été sauvées dans outputs/")


if __name__ == '__main__':
    main()
