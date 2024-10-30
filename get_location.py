import requests
import os
import re
import pickle
import threading
import time
from Bio import SeqIO
from io import StringIO





with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)
if not os.path.exists("gen_loc.pickle") or os.path.getsize('gen_loc.pickle') == 0:
    gen_loc = []
    counter = 0
    for h_gene in range(0, len(total_data["genes"])):
        for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
            for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
                gen_loc.append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
                counter += 1
    gen_loc = list(set(gen_loc)) #remove duplicates
    gen_loc = [[item] for item in gen_loc]
    with open("gen_loc.pickle", "wb") as file:
        pickle.dump(gen_loc, file)
else:
    with open("gen_loc.pickle", "rb") as file:
        gen_loc = pickle.load(file)

def create_url(gen_loc, i, max):
    url = "https://www.ebi.ac.uk/proteins/api/coordinates?accession="
    for k in range(0, max):
        if i + k >= len(gen_loc) - 1:
            break
        if len(gen_loc[i + k]) > 1:
            continue
        url = url + gen_loc[i + k][0]
        if k < max - 1: #not necessary
            url = url + ","
    url = url + "&format=json"
    return url

def get_request(gen_loc, i, max):
    url = create_url(gen_loc, i, max)
    response = requests.get(url)
    data = ''.join(response.text)
    data = re.sub(r"[\n\t\"\{\}\[\]]", '', data)
    data = re.split(r"[:,]", data)
    for k in range(0, max): #loop to find key-words of every protein's accession
        index = 0
        if len(gen_loc[i + k]) > 1:
            print(gen_loc[i + k][0], "---------- Checked ----------")
            continue
        while data[index] != gen_loc[i + k][0]:
            if index >= len(data) - 1:
                gen_loc[i + k].append("Aknown")
                break
            index += 1
        if index >= len(data) - 1:
            continue
        save_index = index
        while data[index] != "chromosome":
            index += 1
            if index > len(data) - 1:
                index = save_index
                print("Alternative", gen_loc[i + k][0])
                while data[index] or data[index] == "accession":
                    if data[index] == "id" and data[index + 2] == "start":
                        gen_loc[i + k].append("chromosome")
                        gen_loc[i + k].append("Aknown")
                        for info in range(2, 6):
                            gen_loc[i + k].append(data[index + info])
            if index >= len(data) - 1:
                break
            if data[index] == "chromosome" and data[index + 2] != "start":
                index += 1
            if data[index] == "accession":
                gen_loc[i + k].append("Aknown")
                break
        if index >= len(data) - 1 or data[index] == "accession" or data[index + 2] != "start":
            continue
        for info in range(6):
            gen_loc[i + k].append(data[index + info])
    for k in range(0, max):
        print(i + k, gen_loc[i + k])
    return gen_loc

def true_stop(stop):    #allows to stop the program when "enter" is pressed
    input()
    stop[0] = 1
    return stop

stop = []
stop.append(int(0))
stop[0] = 0 #just in case

threading.Thread(target=true_stop, daemon=True, args=(stop,)).start()
for i in range(0, len(gen_loc) - 1, 100):
    max = 100
    if i + max > len(gen_loc) - 1:
        max = len(gen_loc) - i
    threading.Thread(target=get_request, daemon=True, args=(gen_loc, i, max)).start()
    print(threading.active_count())
    while threading.active_count() >= 31:
        time.sleep(0.1)
    with open("gen_loc.pickle", "wb") as file:
        pickle.dump(gen_loc, file)
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
with open("gen_loc.pickle", "wb") as file:
    pickle.dump(gen_loc, file)

with open("gen_loc.pickle", "rb") as file:  #just in case
    print(pickle.load(file))
