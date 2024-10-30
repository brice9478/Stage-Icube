import requests
import os
import pickle
import threading
import time
from Bio import SeqIO
from io import StringIO

# ------------- get total_data -------------
with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)

if not os.path.exists("gen_seq.pickle"):
    gen_seq = []
    counter = 0
    for h_gene in range(0, len(total_data["genes"])):
        for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
            for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
                gen_seq.append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
                counter += 1
    gen_seq = list(set(gen_seq)) #enlève les doublons
    with open("gen_seq.pickle", "wb") as file:
        pickle.dump(gen_seq, file)
else:
    with open("gen_seq.pickle", "rb") as file:
        gen_seq = pickle.load(file)

print(len(gen_seq))
print(gen_seq[len(gen_seq) - 1])

sequences = gen_seq

def get_request(gen_seq, i, max):
    url = "https://rest.uniprot.org/uniprotkb/search?query=("
    for k in range(0, max):
        print(i + k, gen_seq[i + k])
        url = url + "accession:"
        url = url + gen_seq[i + k]
        if k < max - 1:
            url = url + "+OR+"
    url = url + ")&format=fasta"
    response = requests.get(url)
    data = ''.join(response.text)
    Seq = StringIO(data)
    protSeq = list(SeqIO.parse(Seq,'fasta'))
    try:
        str(protSeq[max - 1].seq)
        for k in range(0, max):
            sequences[i + k] = sequences[i + k] + ":" + str(protSeq[k].seq)
            sequences[i + k] = sequences[i + k].split(":")
    except:
        print("-----Error. Requesting backup-----")
        for backup in range(0, max):
            url = "http://rest.uniprot.org/unisave/" + gen_seq[i + backup] + "?format=fasta"
            response = requests.get(url)
            data = ''.join(response.text)
            Seq = StringIO(data)
            protSeq = list(SeqIO.parse(Seq,'fasta'))
            try:
                sequences[i + backup] = sequences[i + backup] + ":" + str(protSeq[0].seq)
                sequences[i + backup] = sequences[i + backup].split(":")
            except:
                print("-----/!\\ ERROR ON BACKUP SYSTEM /!\\-----")
                print("-----/!\\ Problematic element : ", gen_seq[i + backup], "/!\\-----")
                sequences[i + backup] = sequences[i + backup] + ":" + "Aknown"
                sequences[i + backup] = sequences[i + backup].split(":")
                print(sequences[i + backup])
            time.sleep(0.1)


for i in range(0, len(gen_seq), 25):
    max = 25
    threading.Thread(target=get_request, daemon=False, args=(gen_seq, i, max)).start()
    while threading.active_count() >= 31:
        time.sleep(0.1)
threading.Thread(target=get_request, daemon=False, args=(gen_seq, i, len(gen_seq) - i - 1)).start()
time.sleep(10)

for retry in range(0, len(gen_seq) - 1):
    if sequences[retry][1] == "Aknown":
        print(gen_seq[retry])
        url = "http://rest.uniprot.org/unisave/" + sequences[retry][0] + "?format=fasta"
        response = requests.get(url)
        data = ''.join(response.text)
        Seq = StringIO(data)
        protSeq = list(SeqIO.parse(Seq,'fasta'))
        sequences[retry][1] = str(protSeq[0].seq)

with open("sequences.pickle", "wb") as file:
    pickle.dump(sequences, file)
