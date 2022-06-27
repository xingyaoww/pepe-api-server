import spacy
nlp = spacy.load("en_core_web_sm")


def lemmatize(word):
    for i in nlp(word):
        return i.lemma_


def text_satisfy_constaint(text: str, filter_words: set) -> bool:
    if text is None:
        return False
    text = text.lower()
    # if text.startswith("http"):
    #     return False
    # splited_text = list(filter(
    #     lambda x: not x.startswith("http"),
    #     text.split()
    # ))
    # # comment has smaller than 4 words
    # if len(splited_text) < 4:
    #     return False
    # comment contains filter words
    lemmatized_text = list(map(lemmatize, text.split()))
    for word in lemmatized_text:
        if word in filter_words:
            return False
    return True
