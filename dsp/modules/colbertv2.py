import functools
from typing import Optional, Union, Any
import requests

from dsp.modules.cache_utils import CacheMemory, NotebookCacheMemory
from dsp.utils import dotdict

import argparse

import openai
import requests


# TODO: Ideally, this takes the name of the index and looks up its port.



# query = ""
# bing_api_key = '5fd5ca2ea3b543078fecffce0b5a9b7e'
# openai_api_key = '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'
# top_k_search_results=5
# answer(query, openai_api_key, bing_api_key, top_k_search_results)

'''
def answer(query, openai_api_key, bing_api_key, top_k_search_results):
    openai.api_key = openai_api_key
    bing_keys = {"Ocp-Apim-Subscription-Key": bing_api_key}
    bing_endpoint = "https://api.bing.microsoft.com/v7.0/search"

    qa_prompt = f"""Write an accurate and concise answer for the given user question, using _only_ the provided summarized web search results. The answer should be correct, high-quality, and written by an expert using an unbiased and journalistic tone. The user's language of choice such as English, Français, Español, Deutsch, or 日本語 should be used. The answer should be informative, interesting, and engaging. The answer's logic and reasoning should be rigorous and defensible. Every sentence in the answer should be _immediately followed_ by an in-line citation to the search result(s). The cited search result(s) should fully support _all_ the information in the sentence. Search results need to be cited using [index]. When citing several search results, use [1][2][3] format rather than [1, 2, 3]. You can use multiple search results to respond comprehensively while avoiding irrelevant search results.

Question: {query}

Search Results:
"""

    response = requests.get(bing_endpoint, headers=bing_keys, params={"q": query, "mkt": "en-US"})
    response.raise_for_status()
    for result_index, result in enumerate(
        response.json()["webPages"]["value"][:top_k_search_results], 1
    ):
        qa_prompt += f"[{result_index}] Original Search Query: {query}\n"
        qa_prompt += f"[{result_index}] Search Result Title: {result['name']}\n"
        qa_prompt += f"[{result_index}] Search Result Summary: {result['snippet']}\n"
        qa_prompt += "\n"

    qa_prompt += "\nAnswer:"

    openai_qa_response = openai.Completion.create(
        model="text-davinci-003", prompt=qa_prompt, max_tokens=1000, temperature=0.2
    )
    print(qa_prompt + openai_qa_response["choices"][0].text)
    return openai_qa_response["choices"][0].text


'''
class ColBERTv2:
    """Wrapper for the ColBERTv2 Retrieval."""

    def __init__(
        self,
        url: str = "http://0.0.0.0",
        port: Optional[Union[str, int]] = None,
        post_requests: bool = False,
    ):
        self.post_requests = post_requests
        self.url = f"{url}:{port}" if port else url

    def __call__(
        self, query: str, k: int = 10, simplify: bool = False
    ) -> Union[list[str], list[dotdict]]:
        if self.post_requests:
            topk: list[dict[str, Any]] = colbertv2_post_request(self.url, query, k)
        else:
            topk: list[dict[str, Any]] = colbertv2_get_request(self.url, query, k)

        if simplify:
            return [psg["long_text"] for psg in topk]

        print('topk: ', topk)
        for psg in topk:
            print('psg: ', psg)
            print('dotdict(psg): ', dotdict(psg))
        return [dotdict(psg) for psg in topk]


@CacheMemory.cache
def colbertv2_get_request_v2(url: str, query: str, k: int):
    assert (
        k <= 100
    ), "Only k <= 100 is supported for the hosted ColBERTv2 server at the moment."

    payload = {"query": query, "k": k}
    res = requests.get(url, params=payload, timeout=10)

    topk = res.json()["topk"][:k]
    topk = [{**d, "long_text": d["text"]} for d in topk]
    return topk[:k]


@functools.lru_cache(maxsize=None)
@NotebookCacheMemory.cache
def colbertv2_get_request_v2_wrapped(*args, **kwargs):
    return colbertv2_get_request_v2(*args, **kwargs)


colbertv2_get_request = colbertv2_get_request_v2_wrapped


@CacheMemory.cache
def colbertv2_post_request_v2(url: str, query: str, k: int):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {"query": query, "k": k}
    res = requests.post(url, json=payload, headers=headers, timeout=10)

    return res.json()["topk"][:k]


@functools.lru_cache(maxsize=None)
@NotebookCacheMemory.cache
def colbertv2_post_request_v2_wrapped(*args, **kwargs):
    return colbertv2_post_request_v2(*args, **kwargs)


colbertv2_post_request = colbertv2_post_request_v2_wrapped
