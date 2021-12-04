from typing import Dict, Optional
from heapq import nlargest
import random
import requests

from KerbalStuff.str_similarity import meaningful_words, words_similarity


class ComparableMod:
    r"""
    NOTE: This is not a real test to be run during builds!
          Rather it is a script/utility intended to be run by a developer
          to exercise the string similarity algorithm with production data
          instead of a local database.

    USAGE: C:\Users\Me\github\SpaceDock> python3
           >>> from tests.test_mod_similarity import ComparableMod
           >>> ComparableMod.similar_mods_test()

           Mods will be retrieved one at a time via the SD API and compared
           to all previously retrieved mods.
           For each mod, the 6 most similar mods seen so far will be printed.
           As more mods are retrieved, the likelihood of a good match increases.
           If all mods have been retreived, then the mods printed will be the
           same as the ones shown on the mod page.
           To quit on Windows: Ctrl-Break
           To quit on Linux: pkill python3
    """

    STRING_PROPS = ['name', 'short_description', 'description']
    MOD_CACHE: Dict[int, Optional['ComparableMod']] = {}
    # Increase this to the current highest mod id to see mods created
    # after this script was written
    MAX_ID = 2927

    @classmethod
    def get(cls, mod_id: int) -> Optional['ComparableMod']:
        if mod_id not in cls.MOD_CACHE:
            try:
                cls.MOD_CACHE[mod_id] = ComparableMod(mod_id)
            except:
                cls.MOD_CACHE[mod_id] = None
        return cls.MOD_CACHE[mod_id]

    def __init__(self, mod_id: int) -> None:
        self.mod_id = mod_id
        api_data = requests.get(
            f'https://spacedock.info/api/mod/{mod_id}').json()
        self.name = api_data['name']
        self.authors = {
            api_data['author'],
            *(a['username'] for a in api_data['shared_authors'])}
        self.prop_words = {
            prop: meaningful_words(api_data[prop])
            for prop in self.STRING_PROPS}

    def similarity(self, other: 'ComparableMod') -> float:
        return (0.1 * words_similarity(self.authors, other.authors)
                + sum(words_similarity(words, other.prop_words[prop])
                      for prop, words in self.prop_words.items()))

    def __repr__(self) -> str:
        return f'{self.mod_id:4}  {self.name}'

    @classmethod
    def similar_mods_test(cls) -> None:
        while True:
            id1 = random.randint(1, cls.MAX_ID)
            mod1 = cls.get(id1)
            if mod1:
                print(f'{mod1}:')
                to_display = dict(sorted(
                    nlargest(6, ((mod1.similarity(mod2), mod2)
                                 for id2, mod2 in cls.MOD_CACHE.items()
                                 if id1 != id2 and mod2),
                             key=lambda rating_id: rating_id[0]),
                    key=lambda pair: pair[0],
                    reverse=True))
                rows = 0
                for rating, mod2 in to_display.items():
                    if rating == 0.0:
                        break
                    rows = rows + 1
                    print(f"\t {rows}. {rating:.2f}  {mod2}")
