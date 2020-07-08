import json
DEFUALTBLACKLIST = 'short_wordblacklist'
DEFUALTVALIDWORDLIST = 'valid_words'


def loadDefaultBlacklist():
    # Load the default blacklist
    with open(f'data/{DEFUALTBLACKLIST}.json') as wordlist:
        return json.load(wordlist)


def loadDefaultValidWordlist():
    # Load the default blacklist
    with open(f'data/{DEFUALTVALIDWORDLIST}.json') as wordlist:
        return json.load(wordlist)
