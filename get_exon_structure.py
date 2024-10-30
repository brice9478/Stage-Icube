import requests
import os
import re
import pickle
import threading
import time
from Bio import SeqIO
from io import StringIO

# Theoritically, it's working, but the weight of the exon_struct.picle file might be more than 500 MB...

with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)
if not os.path.exists("exon_struct.pickle") or os.path.getsize('exon_struct.pickle') == 0:
    exon_struct = []
    counter = 0
    for h_gene in range(0, len(total_data["genes"])):
        for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
            for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
                exon_struct.append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
                counter += 1
    exon_struct = list(set(exon_struct)) #remove duplicates
    exon_struct = [[item] for item in exon_struct]
    with open("exon_struct.pickle", "wb") as file:
        pickle.dump(exon_struct, file)
else:
    with open("exon_struct.pickle", "rb") as file:
        exon_struct = pickle.load(file)

def create_url(exon_struct, i, max):
    url = "https://www.ebi.ac.uk/proteins/api/coordinates?accession="
    for k in range(0, max):
        if i + k >= len(exon_struct) - 1:
            break
        if len(exon_struct[i + k]) > 1:
            continue
        url = url + exon_struct[i + k][0]
        if k < max - 1: #not necessary
            url = url + ","
    url = url + "&format=json"
    return url

def get_request(exon_struct, i, max):
    url = create_url(exon_struct, i, max)
    response = requests.get(url)
    data = ''.join(response.text)
    data = re.sub(r"[\n\t\"\{\}\[\]]", '', data)
    data = re.split(r"[:,]", data)
    for k in range(0, max):
        index = 0
        if len(exon_struct[i + k]) > 1:
            print(exon_struct[i + k][0], "---------- Checked ----------")
            continue
        while data[index] != exon_struct[i + k][0]:
            if index >= len(data) - 1:
                exon_struct[i + k].append("Aknown")
                break
            index += 1
        if index >= len(data) - 1:
            continue
        while data[index] != "exon":
            index += 1
            if index > len(data) - 1:
                break
            if data[index] == "nucleotideId":
                break
        index_new_array = 1
        while index <= len(data) - 1 and data[index] != "nucleotideId":
            while data[index] != "genomeLocation":
                index += 1
                if index > len(data) - 1:
                    break
                if data[index] == "nucleotideId":
                    break
            if index > len(data) - 1:
                break
            if data[index] == "nucleotideId":
                break
            index += 1
            exon_struct[i + k].append([data[index]])
            for values in range(1, 12):
                exon_struct[i + k][index_new_array].append(str(data[index + values]))
            index_new_array += 1
    for k in range(0, max):
        print(i + k, exon_struct[i + k])
    return exon_struct

def true_stop(stop):    #allows to stop the program when "enter" is pressed
    input()
    stop[0] = 1
    return stop

stop = []
stop.append(int(0))
stop[0] = 0 #just in case
# len(exon_struct) - 1
threading.Thread(target=true_stop, daemon=True, args=(stop,)).start()
for i in range(0, len(exon_struct) - 1, 100):
    max = 100
    if i + max > len(exon_struct) - 1:
        max = len(exon_struct) - i
    threading.Thread(target=get_request, daemon=True, args=(exon_struct, i, max)).start()
    print(threading.active_count())
    while threading.active_count() >= 31:
        time.sleep(0.1)
    with open("exon_struct.pickle", "wb") as file:
        pickle.dump(exon_struct, file)
    if stop[0] == 1:
        break
stop[0] = 0 #reset variable stop when "enter" is pressed
threading.Thread(target=true_stop, daemon=True, args=(stop,)).start()
while threading.active_count() > 2: #waiting for threads to finish their tasks before final pickle.dump
    if stop[0] == 1:
        break
    print(threading.active_count())
    time.sleep(1)
time.sleep(1)
print("end")
with open("exon_struct.pickle", "wb") as file:
    pickle.dump(exon_struct, file)

with open("exon_struct.pickle", "rb") as file:  #just in case
    print(pickle.load(file))
