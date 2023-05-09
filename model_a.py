import os
import openai

# docs is a dictionary with the following keys:
# ['k', 'title', 'snippet', 'text']
def model_a(query, docs, mode):

    qa_prompt = f"""Write an accurate and concise answer (1-5 words) for the given user question, using the provided contextual documents. 

    ---

    Question: Which award did the first book of Gary Zukav receive?
    Answer: U.S. National Book Award

    Question: The heir to the Du Pont family fortune sponsored what wrestling team?
    Answer: Foxcatcher

    Question: Who was the director of the 2009 movie featuring Peter Outerbridge as William Easton?
    Answer: Kevin Greutert

    Question: Who produced the album that included a re-recording of "Lithium"?
    Answer: Butch Vig

    Question: What city was the victim of Joseph Druces working in?
    Answer: Boston, Massachusetts

    Question: In what year was the star of To Hell and Back born?
    Answer: 1925

    ---

    Follow the following format.

    Question: $[the question to be answered]

    Context:
    $[sources that may contain relevant content]

    Answer: $[a short factoid answer]

    ---

    Question: {query}

    Search Results:
    """

    for doc in docs:
        qa_prompt += f"[{doc['k']}] Search Result Title: {doc['title']}\n"
        if 'snippet' in doc.keys():
            qa_prompt += f"[{doc['k']}] Search Result Summary: {doc['snippet']}\n"
        if 'text' in doc.keys():
            qa_prompt += f"[{doc['k']}] Search Result Text: {doc['text']}\n"
        qa_prompt += "\n\n --- \n\n"
    
    qa_prompt += "Answer:"
    openai.api_key = os.getenv('OPENAI_API_KEY')

    try: 
        openai_qa_response = openai.Completion.create(model="text-davinci-003", prompt=qa_prompt, max_tokens=100, temperature=0.2)
        answer = openai_qa_response["choices"][0].text 
    except:
        try: 
            openai_qa_response = openai.Completion.create(model="text-davinci-003", prompt=qa_prompt, max_tokens=100, temperature=0.2)
            answer = openai_qa_response["choices"][0].text 
        except: answer = "NO ANSWER"
    print(qa_prompt + answer)

    return answer 