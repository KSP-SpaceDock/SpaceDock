from heapq import nlargest
from typing import List

from .objects import Mod, ModSimilarity


def find_most_similar(mod: Mod, how_many: int = 6) -> List[ModSimilarity]:
    get_sim = lambda mod_sim: mod_sim.similarity
    return sorted(nlargest(how_many,
                           # Zero similarity means nothing at all in common, so skip those
                           filter(lambda mod_sim: mod_sim.similarity > 0,
                                  (ModSimilarity(mod, other_mod)
                                   for other_mod in
                                   Mod.query.filter(Mod.published,
                                                    Mod.game_id == mod.game_id,
                                                    Mod.id != mod.id))),
                           key=get_sim),
                  key=get_sim,
                  reverse=True)


def update_similar_mods(mod: Mod, how_many: int = 6) -> None:
    if not mod.published:
        mod.similarities = []
    else:
        most_similar = find_most_similar(mod, how_many)
        # Remove rows for mods that are no longer among the most similar
        for mod_sim in mod.similarities:
            if not any(mod_sim.other_mod_id == other_sim.other_mod_id
                       for other_sim in most_similar):
               ModSimilarity.query\
                   .filter(ModSimilarity.main_mod_id == mod_sim.main_mod_id,
                           ModSimilarity.other_mod_id == mod_sim.other_mod_id)\
                   .delete()
        for mod_sim in most_similar:
            match = [other_sim for other_sim in mod.similarities
                     if mod_sim.other_mod_id == other_sim.other_mod_id]
            if match:
                # Update existing rows for mods that are still similar
                match[0].similarity = mod_sim.similarity
                # Update the row with swapped IDs, if any
                for other_sim in match[0].other_mod.similarities:
                    if other_sim.other_mod_id == mod_sim.main_mod_id:
                        other_sim.similarity = mod_sim.similarity
            else:
                # Add new rows for newly similar mods
                mod.similarities.append(mod_sim)
