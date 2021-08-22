import wikipediaapi
import re
import collections
import random
from functools import lru_cache
import traceback
from pathlib import Path

regex_non_word = re.compile(r"[^\s]*[^a-zA-Z\-\s]+[^\s]*")
regex_replace_blank = re.compile(r"\s+")


def test_regexps():
    assert not regex_non_word.fullmatch("asdf-As")
    assert regex_non_word.fullmatch("asdf-As_")
    assert (
        regex_non_word.sub("", "asdf ASDF a8sdf a-sdf a_b")
        == "asdf ASDF  a-sdf "
    )
    assert regex_replace_blank.sub(" ", "   ") == " "
    assert regex_replace_blank.sub(" ", "") == ""


def default_preproc_line(line):
    return regex_non_word.sub("", regex_replace_blank.sub(" ", line.lower()))


@lru_cache(100)
def get_wiki_text(searchterm: str, language="de"):
    ww = wikipediaapi.Wikipedia(
        language=language, extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    p = ww.page(searchterm)
    text = p.text
    if not text:
        raise ValueError("Page not found")
    return text


def csort(dct):
    return dict(sorted(dct.items(), key=lambda x: x[1], reverse=True))


def get_count_dict(text):
    words = default_preproc_line(text).split()
    c = collections.Counter(words)
    return csort(c)


def counts2freq(counts):
    norm = sum(counts.values())
    freqs = {key: count / norm for key, count in counts.items()}
    return csort(freqs)


@lru_cache(10)
def get_freqdict():
    wordrx = re.compile("[A-Za-zäüöß]+[A-Za-zäüöß\\-' ]+")
    freqdict = collections.defaultdict(int)
    p = Path(__file__).resolve().parent.parent / "data" / "germandict.txt"
    with p.open() as wordl:
        for line in wordl:
            splts = line.split("\t")
            if not wordrx.match(splts[0]):
                continue
            #             if not splts[2] == "NN":
            #                 continue
            freqdict[splts[0].lower()] += float(splts[-1])
    summed = sum(freqdict.values())
    return csort({key: value / summed for key, value in freqdict.items()})


@lru_cache(10)
def get_nouns():
    nouns = []
    wordrx = re.compile("[A-Za-zäüöß]+[A-Za-zäüöß\\-' ]+")
    p = Path(__file__).resolve().parent.parent / "data" / "germandict.txt"
    with p.open() as wordl:
        for line in wordl:
            splts = line.split("\t")
            if not wordrx.match(splts[0]):
                continue
            if splts[2] == "NN":
                nouns.append(splts[0].lower())
    return nouns


def nouns_only(dct):
    nouns = get_nouns()
    return csort({key: value for key, value in dct.items() if key in nouns})


def filter_min_occ(countdict, threshold=2):
    return {key: value for key, value in countdict.items() if value > threshold}


def filter_non_german(mydict, dictdict):
    return csort(
        {key: value for key, value in mydict.items() if key in dictdict}
    )


def remove_top_n(mydict, dictdict, n=100):
    to_remove = list(dictdict.keys())[:n]
    return csort(
        {key: value for key, value in mydict.items() if key not in to_remove}
    )


def top_n(dct, n=100):
    keys = list(dct.keys())[:n]
    return {key: dct[key] for key in keys}


def remove_similar(dct):
    words = list(dct.keys())
    words2 = words.copy()
    for word in words:
        for word2 in words:
            if (
                word[:5] in word2
                and len(word) < len(word2)
                and not word == word2
                and word2 in words2
            ):
                words2.remove(word2)
    return csort({key: dct[key] for key in words2})


def freq_ratio(freqs1, freqs2):
    return {key: value / freqs2[key] for key, value in freqs1.items()}


def opinionated_selection(counts):
    freqs = counts2freq(filter_min_occ(counts, 2))
    freqdict = get_freqdict()

    freqs = remove_similar(
        top_n(
            freq_ratio(
                nouns_only(
                    remove_top_n(
                        filter_non_german(freqs, freqdict), freqdict, 300
                    )
                ),
                freqdict,
            ),
            100,
        )
    )
    return freqs


def interpret_query(query):
    search_terms = query.split("+")
    selections = []
    for search_term in search_terms:
        search_term = search_term.strip()
        try:
            selections.append(
                opinionated_selection(get_count_dict(get_wiki_text(search_term)))
            )
        except:
            print("Problem with '" + search_term + "'")
            traceback.print_exc()
    all_words = []
    words = []
    for s in selections:
        all_words.extend(list(s.keys()))
        words.extend(list(s.keys())[: 25 // len(selections)])
    words = set(words)
    all_words = set(all_words)
    if len(all_words) < 25:
        raise ValueError("Not enough relevant words found")
    all_words -= words
    if len(words) < 25:
        additional = random.sample(all_words, 25 - len(words))
        our_words = random.sample(list(words) + additional, 25)
    else:
        our_words = random.sample(list(words), 25)
    return [w.capitalize() for w in our_words]
