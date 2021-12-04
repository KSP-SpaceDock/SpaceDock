import re
from typing import Set, Iterable


# Split words on one or more non-alphanumerics
WORD_SPLIT = re.compile(r'[^a-zA-Z0-9]+')

# Split up pieces of StudlyCapsStrings
STUDLY_SPLIT = re.compile(r'(?=[A-Z])')

# English words that do not convey meaning about the context
# We care about things like "rocket" and "propellant" and "deltaV"
MEANINGLESS = {
    'the', 'an', 'this', 'these', 'that', 'those',
    'and', 'or', 'but', 'however',
    'as', 'such', 'than', 'there',
    'me', 'my', 'we', 'us', 'our',
    'you', 'your', 'he', 'him', 'she', 'her', 'it',
    'they', 'them',
    'to', 'from', 'in', 'on', 'for', 'with', 'of', 'into', 'at', 'by',
    'what', 'because', 'then',
    'is', 'be', 'been', 'are', 'get', 'getting', 'has', 'have', 'come',
    'do', 'does',
    'will', 'make', 'work', 'also', 'more',
    'should', 'so', 'some', 'like', 'likely', 'can', 'seems',
    'really', 'very', 'each', 'yup', 'which',
    've', 're',
    'accommodate', 'manner', 'therefore', 'ever', 'probably', 'almost',
    'something',
    'mod', 'pack', 'contains', 'ksp',
    'http', 'https', 'www', 'youtube', 'imgur', 'com',
    'github', 'githubusercontent',
    'forum', 'kerbalspaceprogram', 'index', 'thread', 'topic', 'php',
    'kerbal', 'space', 'continued', 'revived', 'updated', 'redux',
    'inc', 'plus',
}


def split_with_acronyms(s: str) -> Iterable[str]:
    words = WORD_SPLIT.split(s)
    yield from words
    for w in words:
        yield from STUDLY_SPLIT.split(w)


def meaningful_words(s: str) -> Set[str]:
    return set(map(lambda w: w.lower(),
                   filter(lambda w: len(w) > 1 and not w.isnumeric(),
                          split_with_acronyms(s)))) - MEANINGLESS


def words_similarity(words1: Set[str], words2: Set[str]) -> float:
    in_both = words1.intersection(words2)
    all_words = words1 | words2
    return len(in_both) / len(all_words) if all_words else 0
