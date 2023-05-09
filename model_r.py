import os
import requests
from bs4 import BeautifulSoup as bs 
from bs4.element import Comment

import wikipedia
import urllib
# import dsp


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = bs(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)


def scrape_url(url):
    # load the projectpro webpage content 
    html = urllib.request.urlopen(url).read()
    text = text_from_html(html)
    return text


def scrape_wiki_url(wikiname):
    text= wikipedia.summary(wikiname)
    return text


# BING SEARCH
def bing(query, top_k_search_results, wiki_only, entire_doc):
    bing_keys = {"Ocp-Apim-Subscription-Key": os.getenv('BING_API_KEY')}
    bing_endpoint = "https://api.bing.microsoft.com/v7.0/search"

    docs = []
    if wiki_only: response = requests.get(bing_endpoint, headers=bing_keys, params={"q": query+'+site:wikipedia.org', "mkt": "en-US", "count": top_k_search_results})
    else: response = requests.get(bing_endpoint, headers=bing_keys, params={"q": query, "mkt": "en-US", "count": top_k_search_results})
    response.raise_for_status()
    if 'webPages' in response.json().keys(): 
        for result_index, result in enumerate(
            response.json()["webPages"]["value"], 1
        ):
            if entire_doc and wiki_only:
                if 'wikipedia' in result['url']: 
                    scraped_text = scrape_wiki_url(result['name'])
                    docs.append({'k': result_index, 'title': result['name'], 'snippet': result['snippet'], 'text': scraped_text})
            elif entire_doc and not wiki_only:
                scraped_text = scrape_url(result['url'])
                docs.append({'k': result_index, 'title': result['name'], 'snippet': result['snippet'], 'text': scraped_text})
            else: docs.append({'k': result_index, 'title': result['name'], 'snippet': result['snippet']})
    return docs


# # COLBERT
# def colbert(query, top_k_search_results):
#     colbert_server = 'http://ec2-44-228-128-229.us-west-2.compute.amazonaws.com:8893/api/search'
#     rm = dsp.ColBERTv2(url=colbert_server)
#     dsp.settings.configure(rm=rm)
#     passages = dsp.retrieve(query, k=top_k_search_results)
#     docs = []
#     for i, p in enumerate(passages):
#         text_splitup = p.split('|')
#         title = text_splitup[0]
#         text = ('').join(text_splitup[1:])
#         docs.append({'k': i, 'title': title, 'text': text})
#     return docs

# mode can RM, Bing, Google
def model_r(query, top_k_search_results, mode='RM', wiki_only=False, entire_doc=False):
    # if mode=='RM':
    #     docs = colbert(query, top_k_search_results)
    
    if mode=='bing':
        docs = bing(query, top_k_search_results, wiki_only, entire_doc)

    return docs



