import dsp


import openai
import requests


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



def retrieve(query: str, k: int) -> list[str]:
    """Retrieves passages from the RM for the query and returns the top k passages."""
    if not dsp.settings.rm:
        raise AssertionError("No RM is loaded.")
    passages = dsp.settings.rm(query, k=k)
    print('passages1: ', passages)
    passages = [psg.long_text for psg in passages]
    print('passages2: ', passages)

    return passages


def retrieveEnsemble(queries: list[str], k: int, by_prob: bool = True) -> list[str]:
    """Retrieves passages from the RM for each query in queries and returns the top k passages
    based on the probability or score.
    """
    if not dsp.settings.rm:
        raise AssertionError("No RM is loaded.")

    queries = [q for q in queries if q]

    passages = {}
    for q in queries:
        for psg in dsp.settings.rm(q, k=k * 3):
            if by_prob:
                passages[psg.long_text] = passages.get(psg.long_text, 0.0) + psg.prob
            else:
                passages[psg.long_text] = passages.get(psg.long_text, 0.0) + psg.score

    passages = [(score, text) for text, score in passages.items()]
    passages = sorted(passages, reverse=True)[:k]
    passages = [text for _, text in passages]

    return passages
