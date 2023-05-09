#!/usr/bin/env python3
"""A minimal baseline for combining search + QA with text-davinci-003.

This script takes the query, uses it in a Bing API call, collects the
snippets of the top-k retrieved documents, and generates a response from them.

One could imagine adding a bunch of other features here (e.g., query
rewriting to break the input query into a series of search calls, asking
the model to correct its own output, etc.).

Running:

```
python scripts/predict_bing_openai.py \
    --openai-api-key '<put your openai API key here>' \
    --bing-api-key '<put your bing API key here>' \
    --query 'what is the difference between llamas and alpacas?'
```

Example Output:

```
Question: what is the difference between llamas and alpacas?

Answer: Llamas and alpacas are both members of the camelid family, but they have
several distinct differences. Llamas are larger than alpacas, typically weighing
between 113 and 250 kg (250 and 550 lbs) [1] and standing between 120 cm (47 in)
and 1.8 m (72 in) tall [2][3][4], while alpacas are smaller, usually weighing
between 55 and 65 kg (121 and 143 lbs) [1] and standing between 90 cm (35 in)
and 1.2 m (47 in) tall [2][3][4]. Alpacas have shaggy wool that is much finer
and softer than llamas [2][4], and their faces are covered in fur [2], while
llamas have less fur on the face and longer snouts [2]. Alpacas also tend to
have a shyer disposition and aren't typically used as pack animals [2], while
llamas are often used as pack animals [5]. The average lifespan of llamas is
20-25 years [5], while alpacas typically live 15-20 years [5].
```

"""
import argparse

import openai
import pandas as pd
import requests

import re
import string
def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    s = str(s)

    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def handle_punc(text):
        exclude = set(string.punctuation + "".join([u"‘", u"’", u"´", u"`"]))
        return ''.join(ch if ch not in exclude else ' ' for ch in text)

    def lower(text):
        return text.lower()

    def replace_underscore(text):
        return text.replace('_', ' ')

    return white_space_fix(remove_articles(handle_punc(lower(replace_underscore(s))))).strip()


def substring_match_score(output, ans):
  ans = normalize_answer(str(ans))
  output = normalize_answer(str(output))
  return (ans in output)

def substringmatch(prediction, answers_list):
  assert type(answers_list) == list
  
  return max(substring_match_score(prediction, ans) for ans in answers_list)



def answer(query, openai_api_key, bing_api_key, top_k_search_results):
    openai.api_key = openai_api_key
    bing_keys = {"Ocp-Apim-Subscription-Key": bing_api_key}
    bing_endpoint = "https://api.bing.microsoft.com/v7.0/search"


    openai_qa_response = openai.Completion.create(
        model="gpt-3.5-turbo", prompt='Rewrite this question into a search query that captures all the information: '+query, max_tokens=1000, temperature=0.2
    )
    rewritten_query = openai_qa_response["choices"][0].text
    

    qa_prompt = f"""Write an accurate and concise answer (1-5 words) for the given user question, using _only_ the provided summarized web search results. The answer should be correct, high-quality, and written by an expert using an unbiased and journalistic tone. The user's language of choice such as English, Français, Español, Deutsch, or 日本語 should be used. The answer should be informative, interesting, and engaging. The answer's logic and reasoning should be rigorous and defensible. Every sentence in the answer should be _immediately followed_ by an in-line citation to the search result(s). The cited search result(s) should fully support _all_ the information in the sentence. Search results need to be cited using [index]. When citing several search results, use [1][2][3] format rather than [1, 2, 3]. You can use multiple search results to respond comprehensively while avoiding irrelevant search results.

Question: {rewritten_query}

Search Results:
"""

    response = requests.get(bing_endpoint, headers=bing_keys, params={"q": query, "mkt": "en-US"})
    response.raise_for_status()
    for result_index, result in enumerate(
        response.json()["webPages"]["value"][:top_k_search_results], 1
    ):
        qa_prompt += f"[{result_index}] Original Search Query: {rewritten_query}\n"
        qa_prompt += f"[{result_index}] Search Result Title: {result['name']}\n"
        qa_prompt += f"[{result_index}] Search Result Summary: {result['snippet']}\n"
        qa_prompt += "\n"

    qa_prompt += "\nAnswer:"

    openai_qa_response = openai.Completion.create(
        model="gpt-3.5-turbo", prompt=qa_prompt, max_tokens=1000, temperature=0.2
    )
    print(qa_prompt + openai_qa_response["choices"][0].text)
    return openai_qa_response["choices"][0].text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--openai-api-key",
        type=str,
        required=True,
        help="OpenAI API Key.",
    )
    parser.add_argument(
        "--bing-api-key",
        type=str,
        required=True,
        help="Bing API Key.",
    )
    parser.add_argument(
        "--top-k-search-results",
        type=int,
        default=5,
        help="Number of search results to use for each query.",
    )
    args = parser.parse_args()
    df = pd.read_excel('/Users/nicolemeister/Desktop/STANFORD/carlos/triviaQA_subset.xlsx')
    dev = []
    match_num=0
    for i, question in enumerate(df['Question'][:50]):
        answer_gt = df.iloc[i][2]
        prediction = answer(question, args.openai_api_key, args.bing_api_key, args.top_k_search_results)
        print('prediction: ', prediction)
        match_num += substring_match_score(prediction, answer_gt)
    print(match_num/50)
