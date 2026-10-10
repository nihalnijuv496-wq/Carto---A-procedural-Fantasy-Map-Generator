import random

prefixes = ["Ash", "Kael", "Thorn", "Eld", "Bran", "Gal", "Myr", "Sil", "Dun", "Vael"]
middles = ["a", "en", "or", "ith", "ad", "ol", "an", "ir", ""]
suffixes = [
    "ford",
    "helm",
    "wick",
    "dor",
    "gard",
    "moor",
    "stead",
    "ridge",
    "haven",
    "fell",
]

clean = lambda name: name[0].upper() + name[1:] if name else name


def dedupeLetters(text):
    # remove doubled letters at syllable ends
    result = []
    for ch in text:
        if result and result[-1].lower() == ch.lower():
            continue
        result.append(ch)
    return "".join(result)


def generateName(rng=None):
    r = rng or random
    raw = r.choice(prefixes) + r.choice(middles) + r.choice(suffixes)
    return clean(dedupeLetters(raw))


def generateUniqueNames(count, seed=None):
    r = random.Random(seed)
    seen = set()
    produced = 0

    while produced < count:
        name = generateName(rng=r)
        if name not in seen:
            seen.add(name)
            yield name
            produced += 1
