import requests
import os
import pickle
import threading
import time
from Bio import SeqIO
from io import StringIO
from sys import argv

def get_request(gen_seq, i, max, error):
    url = "https://rest.uniprot.org/uniprotkb/search?query=("
    for k in range(0, max):
        url = url + "accession:"
        if len(gen_seq[i + k]) == 2:
            url = url + str(gen_seq[i + k][0])
        else:
            url = url + str(gen_seq[i + k])
        if k < max - 1:
            url = url + "+OR+"
    url = url + ")&format=fasta"
    try:
        response = requests.get(url, timeout=10)
    except:
        if error >= 5:
            total_data[i].append(["Aknown"])
            off = 0
            while rps[off][1] != False:
                off += 1
            rps[off][1] = count_time[0]
            print("Request : all attempts failed.")
            return
        print("/!\ ---------> loop ? Error connection. Request sent again.", str(total_data[i][0]))
        get_request(total_data, i, max, error + 1)
        return
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
            if len(sequences[i + backup]) == 2:
                continue
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
            time.sleep(0.1)
    try:
        off = 0
        while rps[off][1] != False:
            off += 1
        rps[off][1] = count_time[0]
    except:
        return

def retry_aknowns(gen_seq, i, error):
    print(sequences[i][0], "at", i)
    url = "http://rest.uniprot.org/unisave/" + sequences[i][0] + "?format=fasta"
    try:
        response = requests.get(url, timeout=10)
    except:
        if error >= 5:
            total_data[i].append(["Aknown"])
            off = 0
            while rps[off][1] != False:
                off += 1
            rps[off][1] = count_time[0]
            print("Request : all attempts failed.")
            return
        print("/!\ ---------> loop ? Connection error. Request sent again with url :", url)
        get_request(total_data, i, max, error + 1)
        return
    data = ''.join(response.text)
    Seq = StringIO(data)
    protSeq = list(SeqIO.parse(Seq,'fasta'))
    try:
        sequences[i][1] = str(protSeq[0].seq)
    except:
        sequences[i][1] = "Aknown"
        print(sequences[i][0], ": sequence couldn't be found.")
    try:
        off = 0
        while rps[off][1] != False:
            off += 1
        rps[off][1] = count_time[0]
    except:
        return


def timer(count_time, start_time):
    count_second = 0
    while True:
        if count_time[0] >= count_second + 1:
            count_second += 1
        count_time[0] = time.time() - start_time[0]



if len(argv) > 2:
    print("retry with -h for sole argument")
    exit(84)
if len(argv) == 2 and argv[1] == "-h":
    print("-----------------------------------------------------------------------------------------------------------------------")
    print("python3 get_seq.py [file.txt]")
    print("file.txt : a file that contains a list of human genes' accession all separated by a \\n")
    print("The program will generate a pickle file named sequences.pickle.\nIf a file with the name \"sequences.pickle\" already exists, new information will be added to the already existing one.")
    print("note : if no file is given as argument, the program will automatically use the default orthologues.pickle")
    print("Info : if you have a doubt on any result try :")
    print("https://rest.uniprot.org/uniprotkb/[?].fasta \n\\--> replace [?] by the gene's accession")
    print("-----------------------------------------------------------------------------------------------------------------------")
    exit(0)
if len(argv) == 1:
    if not os.path.exists("orthologues.pickle"):
        print("file orthologues.pickle not found")
    with open("orthologues.pickle", "rb") as file:
        total_data = pickle.load(file)
    if not os.path.exists("sequences.pickle"):
        gen_seq = []
        counter = 0
        for h_gene in range(0, len(total_data["genes"])):
            for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
                for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
                    gen_seq.append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
                    counter += 1
        gen_seq = list(set(gen_seq)) #enlève les doublons
    else:
        with open("sequences.pickle", "rb") as file:
            gen_seq = pickle.load(file)
if len(argv) == 2:
    gen_seq = []
    if not os.path.exists(argv[1]):
        print("The file named", argv[1], "can't be found.")
        exit(84)
    if os.path.exists("sequences.pickle"):
        print("/!\\ sequences.pickle already exists. New informations will be added to the existing one. /!\\")
        with open("sequences.pickle", "rb") as file:
            gen_seq = pickle.load(file)
    with open(argv[1], 'r') as file:
        for line in file:
            gen_seq.append(line.strip())



start_time = [time.time()]
count_time = [0]
threading.Thread(target=timer, daemon=True, args=(count_time, start_time)).start()
rps = []
sequences = gen_seq
i = 0
for i in range(0, len(gen_seq), 25):
    max = 25
    if i + max >= len(gen_seq):
        break
    print(i)
    rps.append([count_time[0], False])
    threading.Thread(target=get_request, daemon=True, args=(gen_seq, i, max, 0)).start()
    while len(rps) >= 30:
        if rps[0][1] != False and count_time[0] - rps[0][1] > 1:
            break
        time.sleep(0.1)
    try:
        if rps[0][1] != False:
            del rps[0]
    except:
        continue
print("Number I :", i, "len gen seq :", len(gen_seq))
threading.Thread(target=get_request, daemon=True, args=(gen_seq, i, len(gen_seq) - i, 0)).start()
iferror = 0
while threading.active_count() > 2 and iferror < 10:    #security mesure --> waiting for all previous threads to finish
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(1)

start_time[0] = time.time()
count_time[0] = 0
rps = []
for i in range(0, len(gen_seq)):
    if sequences[i][1] == "Aknown":
        rps.append([count_time[0], False])
        threading.Thread(target=retry_aknowns, daemon=True, args=(gen_seq, i, 0)).start()
        while len(rps) >= 10:
            if rps[0][1] != False and count_time[0] - rps[0][1] > 1:
                break
            time.sleep(0.1)
    try:
        if rps[0][1] != False:
            del rps[0]
    except:
        continue

with open("sequences.pickle", "wb") as file:
    pickle.dump(sequences, file)
exit(0)
