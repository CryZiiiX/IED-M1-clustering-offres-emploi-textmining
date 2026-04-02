"""
Fonctions de prétraitement textuel pour le clustering d'offres d'emploi.

Module utilisé par le notebook principal pour nettoyer les textes
avant vectorisation TF-IDF et clustering.
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
    """Supprime les balises HTML et les entités HTML courantes."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    return text


def remove_boilerplate(text):
    """Supprime les blocs de texte boilerplate légal/RH non discriminants."""
    return _BOILERPLATE_RE.sub(' ', text)


def clean_text(text):
    """
    Pipeline de nettoyage textuel complet :
    1. Suppression du HTML et entités
    2. Suppression du boilerplate légal/RH
    3. Mise en minuscules
    4. Suppression des caractères non alphabétiques
    5. Tokenisation
    6. Suppression des stopwords
    7. Lemmatisation
    8. Suppression des tokens trop courts (< 3 caractères)
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
    """
    Construit le texte exploitable en concaténant titre et description.
    Le titre est répété pour renforcer son poids sémantique.
    """
    title = str(row.get('title', '')) if row.get('title') is not None else ''
    description = str(row.get('description', '')) if row.get('description') is not None else ''
    return f"{title} {title} {description}".strip()
