import requests
import os
import pickle
import threading
import time
from Bio import SeqIO
from io import StringIO

# ---------- Multiple request test --------------
# url = "https://rest.uniprot.org/uniprotkb/search?query=(accession:A0A8C8A9S5+OR+accession:A0A4W5LUS1+OR+accession:A0A3Q1BRX0)&format=fasta"
# url = "https://rest.uniprot.org/unisave/H2QA49?format=fasta"
# response = requests.get(url)
# data=''.join(response.text)
# print(data)
# Seq=StringIO(data)
# protSeq=list(SeqIO.parse(Seq,'fasta'))

# print("Protein ? --> sequence :", str(protSeq[0].seq), "\n")

# exit(0)





# ------- Very first try ----------
# with open("testprot.txt", 'r') as file:
#     content = file.read()
# print(content)
# content = content.split('\n')
# print(content)
# print("---------")



# for i in range(len(content) - 1):
#     id=content[i]

# base_url="http://www.uniprot.org/uniprot/"
# currentUrl=base_url+"A0A8C9MHB7%2CA0A8C8A9S5"+".fasta"
# response = requests.get(currentUrl)
# data=''.join(response.text)

# print(data)
# Seq=StringIO(data)
# protSeq=list(SeqIO.parse(Seq,'fasta'))
# # print(protSeq)
# # print("Protein", id, "--> sequence :", protSeq[0].seq, "\n")
# print(len(protSeq))
# if len(protSeq) == 0:
#     currentUrl = "http://rest.uniprot.org/unisave/A0A8C1B4C5%2CA0A8C8A9S5?format=fasta"
#     response = requests.get(currentUrl)
#     data=''.join(response.text)
# print(data)
# Seq=StringIO(data)
# protSeq=list(SeqIO.parse(Seq,'fasta'))
# print("Protein A0A8C1B4C5 --> sequence :", str(protSeq[0].seq), "\n")





# ------------- get total_data -------------
with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)

if not os.path.exists("gen_seq.pickle"):
    gen_seq = []
    # gen_seq[0] = "MOTHER", "FUDGER"
    # print(gen_seq)
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

# print(gen_seq)
print(len(gen_seq))
print(gen_seq[len(gen_seq) - 1])


# ------------- threading + multiple requests -----------------
# if os.path.exists("sequences.pickle"):
#     os.remove("sequences.pickle")
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
    # print(url)
    response = requests.get(url)
    data = ''.join(response.text)
    Seq = StringIO(data)
    protSeq = list(SeqIO.parse(Seq,'fasta'))
    # if len(protSeq) == 0:
    #     url = "http://rest.uniprot.org/unisave/" + gen_seq[i] + "?format=fasta"
    #     response = requests.get(url)
    #     data = ''.join(response.text)
    #     Seq = StringIO(data)
    #     protSeq = list(SeqIO.parse(Seq,'fasta'))
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




    # print(result)
    # with open("sequences.pickle", "ab") as file:
    #     # file.write(result)
    #     pickle.dump(result, file)


for i in range(0, len(gen_seq), 25):
    # base_url = "http://www.uniprot.org/uniprot/"
    # url = base_url + gen_seq[i] + ".fasta"
    max = 25
    threading.Thread(target=get_request, daemon=False, args=(gen_seq, i, max)).start()
    time.sleep(0.05)
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

    # Seq = StringIO(data)
    # protSeq = list(SeqIO.parse(Seq,'fasta'))
    # sequences.append(protSeq[0].seq)
    # print(sequences[i])
