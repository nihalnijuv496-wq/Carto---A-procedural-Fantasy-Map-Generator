import random

# can add more
PREFIXES = ["Ash", "Kael", "Thorn", "Eld", "Bran", "Gal", "Myr", "Sil", "Dun", "Vael"]
MIDDLES = ["a", "en", "or", "ith", "ad", "ol", "an", "ir", ""]
SUFFIXES = [
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

# name (no accidental double letters at syllable joins, capitalized).
_clean = lambda name: name[0].upper() + name[1:] if name else name


def _dedupe_letters(text):
    """Collapse accidental doubled letters at syllable boundaries (e.g. 'Asshelm' -> 'Ashelm')."""
    result = []
    for ch in text:
        if result and result[-1].lower() == ch.lower():
            continue
        result.append(ch)
    return "".join(result)


def generate_name(rng=None):
    """
    Generate a single settlement name by joining a prefix, middle and suffix.
    """
    r = rng or random
    raw = r.choice(PREFIXES) + r.choice(MIDDLES) + r.choice(SUFFIXES)
    return _clean(_dedupe_letters(raw))


def generate_unique_names(count, seed=None):
    r = random.Random(seed)
    seen = set()
    produced = 0

    while produced < count:
        name = generate_name(rng=r)
        if name not in seen:
            seen.add(name)
            yield name
            produced += 1


if __name__ == "__main__":
    # Quick manual test
    print("Five random settlement names:")
    for n in generate_unique_names(5, seed=7):
        print(" -", n)
