from flask import Flask, jsonify, abort, request
from flashtext import KeywordProcessor
import wordlistloader as bl
import editdistance

import requests
import json

from timeit import default_timer as timer


app = Flask(__name__)

DEFAULT_KEYWORD_PROCESSOR = KeywordProcessor()
VALID_KEYWORD_PROCESSOR = KeywordProcessor()


def config_load():
    with open('data/config.json', 'r', encoding='utf-8-sig') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)


APIKEY = config_load()["token"]

for word in bl.loadDefaultBlacklist():
    DEFAULT_KEYWORD_PROCESSOR.add_keyword(word)

# for word in bl.loadDefaultValidWordlist():
#     VALID_KEYWORD_PROCESSOR.add_keyword(word)


blacklists = [
    {
        'id': 1,
        'name': 'default-blacklist'
    },
    {
        'id': 2,
        'name': 'extensive-blacklist'
    }
]

dictionary_cache = {}


@app.route('/mod-bot/api/v1.0/blacklists', methods=['GET'])
def get_tasks():
    return jsonify({'blacklists': blacklists})


@app.route('/mod-bot/api/v1.0/blacklists/<int:blacklist_id>', methods=['GET'])
def get_blacklist(blacklist_id):
    blacklist = [
        blacklist for blacklist in blacklists if blacklist['id'] == blacklist_id]
    if len(blacklist) == 0:
        abort(404)


@app.route('/mod-bot/api/v1.0/deep-check/<string:message>')
def deep_check(message):

    start = timer()
    '''
    Tokenizes message and checks substring of each token for a word in the blacklist.
    Compares hash of each token with hashmap of all blacklisted words.
    '''
    tokens = message.lower().split(' ')
    extractedKeywords = []
    subTokens = []

    # Sliding slicing of each token
    for token in tokens:
        # Number of letters to extract from the token
        for length in range(3, len(token) - 1):
            for startingIndex in range(0, len(token) - length):
                subToken = (token[startingIndex: length + startingIndex])

                # TODO: implement keyword_processor switch
                if length >= 4:
                    for word in bl.loadDefaultBlacklist():
                        if editdistance.eval(word, subToken) <= 1:
                            extractedKeywords.append(subToken)
                            print(
                                f'edit distance matched: {word} for {subToken}')

                item = DEFAULT_KEYWORD_PROCESSOR.extract_keywords(subToken)
                if len(item) > 0:
                    extractedKeywords.append(item)

        if len(extractedKeywords) == 0:
            print(f"skipping {token}. No match.")
            continue

        if len(extractedKeywords) > 0:
            print(f"found {extractedKeywords}")

            response = requests.get(
                f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{token}?key={APIKEY}')

            if response.status_code != 200:
                print("Exceded daily requests?")
                print(response.status_code)
            else:
                print(f"{response.status_code} succcess!")

            response_dict = json.loads(response.content)

            str_replaced_tokens = token.replace("\"", "").lower()
            # Expects id in "string:int" form or "string"

            if "meta" in response_dict[0]:

                if (response_dict[0]['meta']['id'].split(":")[0] == str_replaced_tokens
                        and response_dict[0]['meta']['offensive'] == True):
                    print("Bad word detected")
                    end = timer()
                    print(end - start)
                    return jsonify(True)
                else:
                    print(f"{token} determined to be non-offensive.")

            else:
                print("Meta keyword missing from payload.")
                if len(extractedKeywords) > 0:
                    end = timer()
                    print(start - end)
                    return jsonify(True)
                else:
                    end = timer()
                    print(end - start)
                    return jsonify(False)
    end = timer()
    print(end - start)
    return jsonify(False)


if __name__ == '__main__':
    app.run(debug=True)
