import argparse

import openai
import pandas as pd
import requests

import re
import string
import dsp


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
    df = pd.read_excel('/Users/nicolemeister/Desktop/STANFORD/carlos/triviaQ\
A_subset.xlsx')
    dev = []
    match_num=0
    for i, question in enumerate(df['Question'][:50]):
        answer_gt = df.iloc[i][2]
        prediction = answer(question, args.openai_api_key, args.bing_api_key\
, args.top_k_search_results)
        print('prediction: ', prediction)
        match_num += substring_match_score(prediction, answer_gt)
    print(match_num/50)
    print('change')












