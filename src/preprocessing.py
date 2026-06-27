"""
Nom : src/preprocessing.py
Rôle : Fonctions de nettoyage et de préparation des textes avant vectorisation.
Auteur : Maxime BRONNY
Version : V1
Cadre : UE Fouille de données textuelles - Master 1 Informatique Big Data - Université Paris 8
Usage : Module importé par le notebook principal (et le script de figures) pour préparer le corpus textuel.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

STOP_WORDS = set(stopwords.words('english'))
LEMMATIZER = WordNetLemmatizer()

# Patterns de boilerplate légal/RH récurrents dans les offres d'emploi.
# Ces blocs de texte sont communs à de nombreuses annonces et ne sont pas
# discriminants pour le clustering par métier.
BOILERPLATE_PATTERNS = [
    r'equal\s+opportunity\s+employer.*?(?:\.\s|\n|$)',
    r'we\s+are\s+an?\s+equal.*?(?:\.\s|\n|$)',
    r'(?:regardless|irrespective)\s+of\s+race.*?(?:\.\s|\n|$)',
    r'affirmative\s+action.*?(?:\.\s|\n|$)',
    r'protected\s+veterans?.*?(?:\.\s|\n|$)',
    r'reasonable\s+accommodations?.*?(?:\.\s|\n|$)',
    r'drug[- ]free\s+workplace.*?(?:\.\s|\n|$)',
    r'e\.?o\.?e\.?\s*(?:m/f/d/v|m/f|minorities|employer)?',
    r'this\s+(?:job\s+)?posting\s+is\s+not\s+(?:intended\s+)?(?:to\s+be\s+)?an?\s+(?:exhaustive|all[- ]inclusive).*?(?:\.\s|\n|$)',
    r'(?:all\s+)?qualified\s+(?:applicants?|candidates?)\s+will\s+receive\s+consideration.*?(?:\.\s|\n|$)',
    r'we\s+(?:do\s+not\s+)?discriminat.*?(?:\.\s|\n|$)',
    r'(?:race|color|religion|sex|sexual\s+orientation|gender\s+identity|national\s+origin|disability|age|veteran)(?:\s*,\s*(?:race|color|religion|sex|sexual\s+orientation|gender\s+identity|national\s+origin|disability|age|veteran|marital\s+status|citizenship|genetic\s+information|pregnancy|ethnicity|creed|ancestry|protected\s+status|military\s+status))+',
    r'(?:diverse|inclusive|diversity\s+and\s+inclusion).*?(?:workplace|environment|organization).*?(?:\.\s|\n|$)',
    r'background\s+check.*?(?:\.\s|\n|$)',
    r'pre[- ]?employment.*?(?:screening|test|drug).*?(?:\.\s|\n|$)',
]
_BOILERPLATE_RE = re.compile('|'.join(BOILERPLATE_PATTERNS), re.IGNORECASE | re.DOTALL)

# Mots-clés typiques du boilerplate EEO qui ne sont pas discriminants
# pour le clustering par métier. Ajoutés aux stopwords du domaine.
EEO_STOPWORDS = {
    'gender', 'race', 'religion', 'sex', 'orientation', 'origin',
    'disability', 'veteran', 'ethnicity', 'creed', 'ancestry',
    'marital', 'citizenship', 'pregnancy', 'discrimination',
    'discriminate', 'nondiscrimination', 'eeo', 'eoe',
    'affirmative', 'accommodation', 'protected',
}
STOP_WORDS = STOP_WORDS | EEO_STOPWORDS


def clean_html(text):
    """Supprime les balises HTML et les entités courantes d'un texte.

    Args:
        text: Texte brut extrait d'une offre d'emploi.

    Returns:
        Texte sans balises ni entités HTML.
    """
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    return text


def remove_boilerplate(text):
    """Retire les blocs de texte juridique et RH récurrents (boilerplate non discriminant).

    Args:
        text: Texte d'une offre d'emploi.

    Returns:
        Texte débarrassé de ces mentions standardisées.
    """
    return _BOILERPLATE_RE.sub(' ', text)


def clean_text(text):
    """Applique le pipeline de nettoyage complet à un texte d'offre.

    Enchaîne la suppression du HTML, le passage en minuscules, le retrait du
    boilerplate, la suppression des caractères non alphabétiques, le filtrage des
    stopwords (anglais et propres au domaine) et la lemmatisation.

    Args:
        text: Texte brut (titre et description concaténés).

    Returns:
        Texte nettoyé prêt pour la vectorisation, ou chaîne vide si l'entrée est invalide.
    """
    if not isinstance(text, str) or len(text.strip()) == 0:
        return ""

    text = clean_html(text)
    text = text.lower()
    text = remove_boilerplate(text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = text.split()
    tokens = [LEMMATIZER.lemmatize(t) for t in tokens
              if t not in STOP_WORDS and len(t) >= 3]
    return ' '.join(tokens)


def build_corpus_text(row):
    """Construit le texte à vectoriser à partir du titre et de la description d'une offre.

    Le titre est répété pour renforcer son poids dans la représentation.

    Args:
        row: Ligne du DataFrame (offre) contenant les champs 'title' et 'description'.

    Returns:
        Texte consolidé de l'offre.
    """
    title = str(row.get('title', '')) if row.get('title') is not None else ''
    description = str(row.get('description', '')) if row.get('description') is not None else ''
    return f"{title} {title} {description}".strip()
