import pandas as pd
import os
import json

# def process_dataset(dataset_name, n=5):
#     answers = []
#     if dataset_name=='triviaQA':
#         path = os.getcwd()+'/data/triviaQA_subset.xlsx'
#         df = pd.read_excel(path)
#         for i, q in enumerate(df['Question'][:n]):
#             answers.append(df.iloc[i][2])
#             questions.append(q)



#     return questions, answers

df = pd.read_excel('/Users/nicolemeister/Desktop/STANFORD/carlos/triviaQA_subset.xlsx')
data = []

for i, question in enumerate(df['Question']):
    answer = df.iloc[i][2]
    data.append({'question': question, 'answer': answer})

with open('triviaQA.json', 'w') as fp:
    json.dump(data, fp)
