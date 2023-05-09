import json
import os

def process_dataset(dataset_name, n=5):
    if dataset_name=='triviaQA':
        path = os.getcwd()+'/data/triviaQA.json'
    
    with open(path, 'r') as fp:
        data = json.load(fp)

    return data[:n]