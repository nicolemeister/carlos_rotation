import openai
import os

def model_q(question, mode='no_rewrite'):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    if mode=='no_rewrite':
        query = question
    elif mode=='rewrite':
        openai_qa_response = openai.Completion.create(model="text-davinci-003", prompt='Rewrite this question into a search query that captures all the information: '+question, max_tokens=500, temperature=0.2)
        query = openai_qa_response["choices"][0].text
    # TO DO: MULTI-HOP
    
    return query