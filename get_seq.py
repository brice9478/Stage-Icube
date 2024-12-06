import requests
import os
import pickle
import threading
import time
from Bio import SeqIO
from io import StringIO
from sys import argv
from openpyxl import Workbook, load_workbook

def get_request(gen_seq, i, max, error):
    url = "https://rest.uniprot.org/uniprotkb/search?query=("
    for k in range(0, max):
        url = url + "accession:"
        url = url + str(gen_seq[i + k][0])
        if k < max - 1:
            url = url + "+OR+"
    url = url + ")&format=fasta"
    try:
        response = requests.get(url, timeout=10)
    except:
        if error >= 5:
            gen_seq[i].append("Aknown")
            off = 0
            while rps[off][1] != False:
                off += 1
            rps[off][1] = count_time[0]
            print("Request : all attempts failed.")
            return
        print("/!\ ---------> loop ? Error connection. Request sent again.", url)
        get_request(gen_seq, i, max, error + 1)
        return
    data = ''.join(response.text)
    Seq = StringIO(data)
    protSeq = list(SeqIO.parse(Seq,'fasta'))
    not_found = 0
    for k in range(0, max):
        if not "|" + gen_seq[i + k][0] + "|" in data:
            gen_seq[i + k].append("Aknown")
            not_found += 1
            seq_not_found.append(gen_seq[i + k][0])
            continue
        try:
            gen_seq[i + k].append(str(protSeq[k - not_found].seq))
        except:
            #this next part isn't really usefull now but whatever
            print("-----Error. Requesting backup-----")
            if len(gen_seq[i + k]) == 2:
                continue
            url = "http://rest.uniprot.org/unisave/" + gen_seq[i + k][0] + "?format=fasta"
            response = requests.get(url)
            data = ''.join(response.text)
            Seq = StringIO(data)
            protSeq = list(SeqIO.parse(Seq,'fasta'))
            try:
                gen_seq[i + k].append(str(protSeq[k - not_found].seq))
            except:
                print("-----/!\\ ERROR ON BACKUP SYSTEM /!\\-----")
                print("-----/!\\ Problematic element : ", gen_seq[i + k][0], "/!\\-----")
                gen_seq[i + k].append("Aknown")
            time.sleep(0.1)
    try:
        off = 0
        while rps[off][1] != False:
            off += 1
        rps[off][1] = count_time[0]
    except:
        return

def retry_aknowns(gen_seq, i, error):
    print(gen_seq[i][0], "at", i)
    url = "http://rest.uniprot.org/unisave/" + gen_seq[i][0] + "?format=fasta"
    try:
        response = requests.get(url, timeout=10)
    except:
        if error >= 5:
            if len(gen_seq[i]) == 1:
                gen_seq[i].append("Aknown")
            else:
                gen_seq[i][1] = "Aknown"
            off = 0
            while rps[off][1] != False:
                off += 1
            rps[off][1] = count_time[0]
            print("Request : all attempts failed.")
            return
        print("/!\ ---------> loop ? Connection error. Request sent again with url :", url)
        retry_aknowns(gen_seq, i, error + 1)
        return
    data = ''.join(response.text)
    Seq = StringIO(data)
    protSeq = list(SeqIO.parse(Seq,'fasta'))
    try:
        if len(gen_seq[i]) == 1:
            gen_seq[i].append(str(protSeq[0].seq))
        else:
            gen_seq[i][1] = str(protSeq[0].seq)
    except:
        if len(gen_seq[i]) == 1:
            gen_seq[i].append("Aknown")
        else:
            gen_seq[i][1] = "Aknown"
        print(gen_seq[i][0], ": sequence couldn't be found.")
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
    print("The program will generate a pickle file named gen_seq.pickle.")
    print("If a file with the name \"gen_seq.pickle\" already exists, new information will be added to the already existing one.")
    print("note : if no file is given as argument, the program will automatically use the default orthologues.pickle")
    print("Info : if you have a doubt on any result try :")
    print("https://rest.uniprot.org/uniprotkb/[?].fasta \n\\--> replace [?] by the gene's accession")
    print("-----------------------------------------------------------------------------------------------------------------------")
    exit(0)
if len(argv) == 1:
    if not os.path.exists("orthologues.pickle"):
        print("file orthologues.pickle not found. Please try again with -h as argument.")
        exit(84)
    with open("orthologues.pickle", "rb") as file:
        total_data = pickle.load(file)

    if not os.path.exists("gen_seq.pickle") or os.path.getsize('gen_seq.pickle') == 0:
        if not os.path.exists("GenoDENT_genes.xlsx"):
            print("File GenoDENT_genes.xlsx not found.")
            exit(84)
        excel_file = load_workbook("GenoDENT_genes.xlsx")
        content = excel_file.active
        gen_seq = []
        for i in range(len(content['B']) - 1):
            gen_seq.append(content['B' + str(i + 2)].value)
        counter = len(content['B']) - 1
        for h_gene in range(0, len(total_data["genes"])):
            for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
                for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
                    gen_seq.append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
                    counter += 1
        gen_seq = list(set(gen_seq)) #enlève les doublons
        gen_seq = [[item] for item in gen_seq]
    else:
        with open("gen_seq.pickle", "rb") as file:
            gen_seq = pickle.load(file)
if len(argv) == 2:
    gen_seq = []
    if not os.path.exists(argv[1]):
        print("The file named", argv[1], "can't be found.")
        exit(84)
    if os.path.exists("gen_seq.pickle"):
        print("/!\\ gen_seq.pickle already exists. New informations will be added to the existing one. /!\\")
        with open("gen_seq.pickle", "rb") as file:
            gen_seq = pickle.load(file)
    with open(argv[1], 'r') as file:
        for line in file:
            if line == "\n":
                continue
            gen_seq.append([line.strip()])

seq_not_found = []
start_time = [time.time()]
count_time = [0]
threading.Thread(target=timer, daemon=True, args=(count_time, start_time)).start()
rps = []
gen_seq = gen_seq
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
threading.Thread(target=get_request, daemon=True, args=(gen_seq, i, len(gen_seq) - i, 0)).start()
iferror = 0
while threading.active_count() > 2 and iferror < 10:    #security mesure --> waiting for all previous threads to finish
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(1)

if len(seq_not_found) > 0:
    print("No sequence found for:", seq_not_found, "\nWill retry with another url starting now.")

start_time[0] = time.time()
count_time[0] = 0
rps = []
for i in range(0, len(gen_seq)):
    if gen_seq[i][1] == "Aknown":
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

with open("gen_seq.pickle", "wb") as file:
    pickle.dump(gen_seq, file)
exit(0)
