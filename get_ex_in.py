import requests
import os
import pickle
import threading
import time
from Bio import SeqIO
from io import StringIO

# url = "https://rest.uniprot.org/unisave/A0A8C9DI72?format=fasta"
# response = requests.get(url)
# data=''.join(response.text)
# print(data)
# Seq=StringIO(data)
# protSeq=list(SeqIO.parse(Seq,'fasta'))
# print(protSeq)

# url = "https://rest.ensembl.org/lookup/id/A0A8C9DI72?expand=1"
# headers = {"Content-Type": "application/json"}

# response = requests.get(url, headers=headers)
# if response.status_code == 200:
#     data = response.json()
#     print(data)
# else:
#     print(f"Error: {response.status_code}")

# ----- Print sequences -----
# with open("sequences.pickle", "rb") as file:
#     sequences = pickle.load(file)
# for i in range(100):
#     print(sequences[i])



# gene_name = "A0A8C8A9S5"
# url = f"https://api.genome.ucsc.edu/getData/track?genome=hg38;track=knownGene;name={gene_name}"
# response = requests.get(url)

# if response.ok:
#     gene_info = response.json()
#     print(gene_info)
# else:
#     print("Erreur:", response.status_code)


gene_name = "A0A8C8A9S5"
species = "human"  # ou autre espèce comme 'mouse', 'zebrafish', etc.

url = f"https://rest.ensembl.org/query=(access:A0A8C8A9S5)&format=fasta"

# headers = { "Content-Type" : "application/json" }
response = requests.get(url)

data = ''.join(response.text)

# Affichage des résultats JSON
print(data)
