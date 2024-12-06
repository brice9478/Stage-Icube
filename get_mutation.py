import requests
import openpyxl
import time
import json
import pickle
import os
import threading
import re
from curses.ascii import isdigit
from Bio import SeqIO
from io import StringIO
from openpyxl import Workbook, load_workbook
from math import *
from requests.adapters import HTTPAdapter, Retry
from sys import argv


# Generate API key --> https://account.ncbi.nlm.nih.gov/settings/


def findex(data, str):
    for i in range(len(data) - 1):
        if data[i] == str:
            return i
    return -1

def findex_description(data, str):
    positions = [i for i, x in enumerate(data) if x == str and data[i + 1] == "description"]
    return positions

def findexstr(data, str):
    positions = [i for i, x in enumerate(data) if x == str]
    return positions

def check_multiple_pdi(pdi, data, positions, total_data, count):
    ends_doc_sum = findexstr(data, "/DocumentSummary")
    nb_pdi = 0
    prev_nb_pdi = 0
    for n in range(len(ends_doc_sum)):
        prev_nb_pdi = nb_pdi
        while positions[nb_pdi] < ends_doc_sum[n]:
            nb_pdi += 1
            if nb_pdi >= len(positions):
                break
        if nb_pdi - prev_nb_pdi > 1:
            for i in range(0, nb_pdi - prev_nb_pdi):
                temp = re.split(r"[:]", data[positions[i + prev_nb_pdi] + 1]) # /!\ ex: DATA canonical_spdi NC_000015.10:58679183::CTCTG --> there can be multiple canonical_spdi --> ex: id 88839
                del temp[0]
                for j in range(len(temp)):
                    if temp[j] == '':
                        temp[j] = "none"
                if i == 0:
                    pdi.append([[temp[0]]])
                    pdi[n].append([temp[1]])
                    pdi[n].append([temp[2]])
                else:
                    pdi[n][0].append(temp[0])
                    pdi[n][1].append(temp[1])
                    pdi[n][2].append(temp[2])
        else:
            temp = re.split(r"[:]", data[positions[prev_nb_pdi] + 1]) # /!\ ex: DATA canonical_spdi NC_000015.10:58679183::CTCTG --> there can be multiple canonical_spdi --> ex: id 88839
            del temp[0]
            for i in range(len(temp)):
                if temp[i] == '':
                    temp[i] = "none"
            pdi.append(temp)
    return pdi

def divide_and_conquer(total_data, count, error, rps):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=" + str(total_data[count][0]) + "&retmode=fasta"
    try:
        params = {'api_key': argv[1]} # /!\
        response = requests.get(url, timeout=10, params=params)
    except:
        if error >= 5:
            total_data[count].append(["Aknown"])
            off = 0
            while rps[off][1] != False:
                off += 1
            rps[off][1] = count_time[0]
            return
        print("/!\ ---------> loop ? Connection error. Request sent again with url :", url)
        divide_and_conquer(total_data, count, error + 1, rps)
        return
    off = 0
    while rps[off][1] != False:
        off += 1
    rps[off][1] = count_time[0]
    data = ''.join(response.text)
    data = re.sub(r"[\n \t]", '', data)
    data = re.split(r"[><]", data)
    for i in range(len(data)):
        if data[i] == '':
            del data[i]
            if i == len(data) - 2:
                break
    for i in range(int(data[findex(data, "Count") + 1])):
        total_data[count].append(["id"])
        total_data[count][i + 1].append(data[findex(data, "IdList") + (i * 3 + 2)])
        if data[findex(data, "IdList") + (i * 3 + 2) + 2] == "/IdList":
            break



def good_or_evil(total_data, count, error):
    if len(total_data[count]) == 1:
        return
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id="
    for i in range(1, len(total_data[count])):
        url = url + str(total_data[count][i][1])
        if i < len(total_data[count]) - 1:
            url = url + ", "
    url = url + "&retmode=fasta"
    print(url)
    try:
        params = {'api_key': argv[1]} # /!\
        response = requests.get(url, timeout=10, params=params)
    except:
        if error >= 5:
            total_data[count].append(["Aknown"])
            off = 0
            while rps[off][1] != False:
                off += 1
            rps[off][1] = count_time[0]
            return
        print("/!\ ---------> loop ? Connection error. Request sent again with url :", url)
        good_or_evil(total_data, count, error + 1)
        return
    off = 0
    while rps[off][1] != False:
        off += 1
    rps[off][1] = count_time[0]
    data = ''.join(response.text)
    data = re.sub(r"[\n\t]", '', data)
    data = re.split(r"[><]", data)
    for i in range(len(data) - 1):
        if data[i] == '':
            del data[i]
            if i == len(data) - 2:
                break
    positions = findex_description(data, "germline_classification")
    for glc in range(len(positions)):
        if len(total_data[count][glc + 1]) > 2:
            continue
        if data[positions[glc] + 2] == "/description": #sometimes, germline_classification doesn't have a description. Ex : id 3257758
            total_data[count][glc + 1].append("Aknown")
        else:
            total_data[count][glc + 1].append(data[positions[glc] + 2])

    positions = findexstr(data, "canonical_spdi")
    pdi = []
    if len(positions) > len(findexstr(data, "/DocumentSummary")):
        print("|||||||||||||||||||||||||||||||||||||||||||||\n/!\ MULTIPLE MUTATIONS DETECTED at", total_data[count], "\n|||||||||||||||||||||||||||||||||||||||||||||")
        pdi = check_multiple_pdi(pdi, data, positions, total_data, count)
    else:
        for i in range(0, len(positions)): #/!\ if positions = [1, 10] --> len(positions) = 2 --> repeat 0, 1 but not 2 it's a bit different from C
            temp = re.split(r"[:]", data[positions[i] + 1]) # /!\ ex: DATA canonical_spdi NC_000015.10:58679183::CTCTG --> there can be multiple canonical_spdi --> ex: id 88839
            del temp[0]
            for j in range(len(temp)):
                if temp[j] == '':
                    temp[j] = "none"
            pdi.append(temp)
    for i in range(len(pdi)):
        total_data[count][i + 1].append("position(s)") # i + 1 'cause total_data[count][0] = accession (which is a string)
        total_data[count][i + 1].append(pdi[i][0])
        total_data[count][i + 1].append("deletion(s)")
        total_data[count][i + 1].append(pdi[i][1])
        total_data[count][i + 1].append("insertion(s)")
        total_data[count][i + 1].append(pdi[i][2])



def timer(count_time, start_time):
    while True:
        count_time[0] = time.time() - start_time[0]


if len(argv) == 1 or len(argv) > 3:
    print("retry with -h for sole argument")
    exit(84)
if argv[1] == "-h":
    print("-----------------------------------------------------------------------------------------------------------------------")
    print("This program needs 2 arguments :")
    print("python3 get_mutation.py [api key] [file.txt]")
    print("api key : find it on https://account.ncbi.nlm.nih.gov/settings/")
    print("file.txt : a file that contains a list of human genes' accession all separated by a \\n")
    print("The program will generate a pickle file named gen_mutation.pickle.\nIf a file with the name \"gen_mutation.pickle\" already exists, new information will be added to the already existing one.")
    print("note : if no file is given as argument, the program will automatically use the default excel file GenoDENT_genes.xlsx")
    print("Info : if you have a doubt on any result try :")
    print("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=[?]&retmode=fasta \n\\--> replace [?] by the gene's accession to get the id")
    print("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=[?]&retmode=fasta \n\\--> replace [?] by the id to get information on the mutation")
    print("-----------------------------------------------------------------------------------------------------------------------")
    exit(0)
if len(argv) == 2:
    if not os.path.exists("GenoDENT_genes.xlsx"):
        print("File GenoDENT_genes.xlsx not found.")
        exit(84)
    excel_file = load_workbook("GenoDENT_genes.xlsx")
    content = excel_file.active
    total_data = []
    if os.path.exists("gen_mutation.pickle"):
        with open("gen_mutation.pickle", "rb") as file:
            total_data = pickle.load(file)
    else:
        for i in range(len(content['B']) - 1):
            total_data.append([content['B' + str(i + 2)].value])
if len(argv) == 3:
    total_data = []
    if not os.path.exists(argv[2]):
        print("The file named", argv[2], "can't be found.")
        exit(84)
    if os.path.exists("gen_mutation.pickle"):
        print("/!\\ gen_mutation.pickle already exists. New informations will be added to the existing one. /!\\")
        with open("gen_mutation.pickle", "rb") as file:
            total_data = pickle.load(file)
    with open(argv[2], 'r') as file:
        for line in file:
            if line == "\n":
                continue
            total_data.append([line.strip()])





start_time = [time.time()]
count_time = [0]
threading.Thread(target=timer, daemon=True, args=(count_time, start_time)).start()
rps = []
print("threads", threading.active_count())
for count in range(len(total_data)):
    print(count, total_data[count][0])
    if len(total_data[count]) > 1: # > 1
        continue
    rps.append([count_time[0], False])
    threading.Thread(target=divide_and_conquer, daemon=True, args=(total_data, count, 0, rps)).start()
    while len(rps) >= 10:
        if rps[0][1] != False and count_time[0] - rps[0][1] > 1:
            break
        time.sleep(0.1)
    if rps[0][1] != False:
        del rps[0]
    with open("gen_mutation.pickle", "wb") as file:
        pickle.dump(total_data, file)
iferror = 0
while threading.active_count() > 2 and iferror < 10:    #security mesure --> waiting for all previous threads to finish
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(0.5)
with open("gen_mutation.pickle", "wb") as file:
        pickle.dump(total_data, file)



start_time[0] = time.time()
count_time[0] = 0
rps = []
for count in range(len(total_data)):
    print(count, total_data[count][0])
    if len(total_data[count]) <= 1:
        continue
    rps.append([count_time[0], False])
    threading.Thread(target=good_or_evil, daemon=True, args=(total_data, count, 0)).start()
    while len(rps) >= 10:
        if rps[0][1] != False and count_time[0] - rps[0][1] > 1:
            break
        time.sleep(0.1)
    if rps[0][1] != False:
        del rps[0]
while threading.active_count() > 2 and iferror < 10:    #security mesure
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(0.5)


time.sleep(3)
with open("gen_mutation.pickle", "wb") as file:
    pickle.dump(total_data, file)
