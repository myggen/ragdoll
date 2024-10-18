#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## Setup your configuration here. 

# The docs currently need to be in html format or plain text, either from web or from disk. Edit the list with the docs you want.

#dataserver = "http://192.168.1.156:8000/"
dataserver = "http://10.30.1.0:8000/"

#ollama_service = 'https://ollama-test.met.no/'
ollama_service='http://10.30.1.0:11434'

html_refs = [
                dataserver + "EtiskeretningslinjerforforskningvedMET.html", 
                dataserver + "RetningslinjeforgrunnsikringavITtjenester.html", 
                dataserver + "Retningslinjeforreiserv2.1.html",
                dataserver + "RetningslinjeforITbruker.html"
                ]

# Number of sentences for each chunk of text that gets vectorized/embedded.
# A smaller chunk size means the embeddings are more precise, while a larger
# chunk size means that the embeddings may be more general, but can miss fine-grained details
chunk_size = 2048

# Number of sentences that overlap between chunks.
# When you chunk data, overlapping a small amount of text between chunks can help preserve context.
# We recommend starting with an overlap of approximately 10%. For example, given a fixed chunk 
# size of 256 tokens, you would begin testing with an overlap of 25 tokens.

overlap = 200

# Number of chunks to include as context in the prompt.
prompt_context_chunks = 30

# Set True to run query with and without context
non_context_run = True

# Show context data beforing running the query
print_context_data = True

# The question you want to ask
#query =  "How should I structure my NetCDF file at MET Norway and create an MMD document with metadata about that NETCDF file?"
#query = "Kan du noe Norsk ?"
#query = 'Please answer the following in Norwegian. Can you give a short summary version of the guidelines at MET for informasjons security in projects'
#query = 'Please answer the following in Norwegian. Can you give a short summary version of the guidelines at MET for informasjons security in projects. Please include some references'
#query = 'Please answer the following in Norwegian. Give me a list of the guidelines/"Retningslinje" at MET("Retningslinjer in Norwegian). Please include some references to original documents. Also please translate the questen I gave you to Norwegian :-)'
#query = 'Please give me a list of the retningslinjer documents at MET . Add a short summary to each document in the list . Preferably with an URL to each document.'
query = 'Provide a short version of guidelines for business trips at MET ? Also provide refrences or urls'

#query = 'Whats the headlines at https://vg.no today ? '
#query = 'Please visit https://vg.no and make a short summary of todays headings '
##query = 'Kan du gi meg en liste med retningslinjedokmentene på  MET . Vennlist svar på norsk'

#query = "Do you have a summary of a short version of the guidelines for research ethics at MET (Meteorological Institute) in Norwegian ?"
#query = "Can you give me a short version of the guidelines at MET in norwegian ?"
# The url to the ollama service you want to use.



# In[ ]:


import os
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from pypdf import PdfReader
import nltk
nltk.download('punkt_tab')

def is_url(ref)->bool:
    return urlparse(ref).scheme in ["http", "https"]

def text_from_files(files:list[str])->list[str]:
    docs = []
    for filename in files:
        with open(filename, 'r') as file:
            docs.append(file.read())
    
    return docs

def text_from_web(urls:list[str])->list[str]:
    web_docs = []
    for url in urls:
        resp = requests.get(url)

        if resp.status_code != 200:
            raise Exception(f"request {url} failed with status code {resp.status_code}")
        
        web_docs.append(resp.text)

    return web_docs

def text_from_pdf_files(files:list[str])->list[str]:
    docs = []
    for file in files:
        doc = ""
        reader = PdfReader(file)
        for page in reader.pages:
            doc += page.extract_text()
        docs.append(doc)
        print(doc)
    return docs
        
def html2chunks(html_docs:list[str])->list[str]:
    chunks:list[str] = []
    for doc in html_docs:
        sentences = html2sentences(doc)

        chunks.extend(sentences2chunks(sentences))

    return chunks

def text_docs2chunks(text_docs:list[str])->list[str]:
    chunks:list[str] = []
    for doc in text_docs:
        sentences = sent_tokenize(doc,language='english')
        chunks.extend(sentences2chunks(sentences))
    return chunks

def html2sentences(web_doc:str)->list[str]:
    soup = BeautifulSoup(web_doc, 'html.parser')    
    text = soup.get_text()

    return sent_tokenize(text,language='english')

def sentences2chunks(sentences:list[str], chunk_size=chunk_size, overlap=overlap)->list[str]:
    # Split the sentences into chunks with overlap
    chunks = [sentences[i:i+chunk_size] for i in range(0, len(sentences), chunk_size-overlap)]

    return [' '.join(chunk) for chunk in chunks]


# In[ ]:


import ollama
import chromadb

from llama_index.llms.ollama import Ollama
chromedb_client = chromadb.Client()
collection = chromedb_client.create_collection(name="metnorway") 

ollama_client = ollama.Client(host=ollama_service)

# Extract sentences from all documents and create chunks out of those sentences.
html_docs = []
for html_ref in html_refs:
    if is_url(html_ref):
        html_docs.extend(text_from_web([html_ref]))
    else:
        html_docs.extend(text_from_files([html_ref]))
chunks = html2chunks(html_docs)

#model = "mxbai-embed-large:latest"
model="llama3.1:latest"
# Loop through chunks, vectorize each one, and add them to the vector database.
for i, d in enumerate(chunks):  
    response = ollama_client.embeddings(model=model, prompt=d)
    #response = ollama_client.embeddings(model="phi3", prompt=d)

    embedding = response["embedding"]
    collection.add(
        ids=[str(i)],
        embeddings=[embedding],
        documents=[d]
    )


# In[ ]:


# vectorize query and retrieve the most relevant doc
response = ollama_client.embeddings(
    prompt=query,
    model=model
)

results = collection.query(
    query_embeddings=[response["embedding"]],
    n_results=prompt_context_chunks
)

data = ""
for r in results['documents']:
    for c in r:
        data += c        

if print_context_data:
    print(f"CONTEXT DATA:\n{data}")


# In[ ]:


#system_type = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>You are an expert at IT and meteorology at a Meteorological Institute<|eot_id|>"
system_type = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>I am a chat boot at Meteorologisk institutt (MET.NO) who have read all guidelines at  MET<|eot_id|>"

# generate a response with just the prompt.
if non_context_run:
    prompt = f"{system_type}.<|start_header_id|>user<|end_header_id|>{query}"
    output = ollama_client.generate(
        model="llama3:8b",
        prompt=prompt
    )
    print("WITHOUT CONTEXT DATA:\n")
    print(output['response'])
    #print("\n\n")

# generate a response with context data and prompt.
prompt = f"{system_type}.<|start_header_id|>user<|end_header_id|>Using this data: {data}. Respond to this prompt: {query}"
output = ollama_client.generate(
    model="llama3:8b",
    prompt=prompt
)
print("WITH CONTEXT DATA:\n")
print(output['response'])

