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



def divide_and_conquer(total_data, count, error, rps):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=" + str(total_data[count][0]) + "&retmode=fasta"
    try:
        params = {'api_key': "?"} #personnal
        response = requests.get(url, timeout=5, params=params)
    except:
        if error >= 5:
            total_data[count].append(["Aknown"])
            if len(rps) >= 10:
                del rps[0]
            return
        print("/!\ ---------> loop ?", str(total_data[count][0]))
        divide_and_conquer(total_data, count, error + 1, rps)
        return
    if len(rps) >= 10:
        del rps[0]
    data = ''.join(response.text)
    data = re.sub(r"[\n \t]", '', data)
    data = re.split(r"[><]", data)
    print("DATA SUCCESSFULLY CREATED", str(total_data[count][0]))
    for i in range(len(data) - 1):
        if data[i] == '':
            del data[i]
            if i == len(data) - 2:
                break
    print(data)
    print("--------------------------------------")
    for i in range(int(data[findex(data, "Count") + 1])):
        total_data[count].append(["id"])
        total_data[count][i + 1].append(data[findex(data, "IdList") + (i * 3 + 2)])
        if data[findex(data, "IdList") + (i * 3 + 2) + 2] == "/IdList":
            break
    print("RESULT :", total_data[count], "\n--------------------------------------")
    print("END : thread :", threading.active_count(), "accession :", str(total_data[count][0]))



def good_or_evil(total_data, count):
    if len(total_data[count]) == 1:
        return
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id="
    for i in range(1, len(total_data[count]) - 1):
        url = url + str(total_data[count][i][1])
        if i < len(total_data[count]) - 2:
            url = url + ", "
    url = url + "&retmode=fasta"
    print(url)
    response = requests.get(url)
    data = ''.join(response.text)
    data = re.sub(r"[\n\t]", '', data)
    data = re.split(r"[><]", data)
    for i in range(len(data) - 1):
        if data[i] == '':
            del data[i]
            if i == len(data) - 2:
                break
    print("_____________________________________________________")
    positions = findex_description(data, "germline_classification")
    for glc in range(len(positions) - 1):
        if len(total_data[count][glc + 1]) > 2:
            continue
        total_data[count][glc + 1].append(data[positions[glc] + 2])
    positions = findexstr(data, "canonical_spdi")
    total_data[count][positions[0]].append(data[positions[0] + 1])



def good_or_evil_recheck(total_data, count):
    if len(total_data[count]) == 1:
        return
    for i in range(1, len(total_data[count])):
        if len(total_data[count][i]) >= 3:
            continue
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=" + str(total_data[count][i][1]) + "&retmode=fasta"
        print(url)
        response = requests.get(url)
        data = ''.join(response.text)
        data = re.sub(r"[\n\t]", '', data)
        data = re.split(r"[><]", data)
        for k in range(len(data) - 1):
            if data[k] == '':
                del data[k]
                if k == len(data) - 2:
                    break
        print("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
        positions = findex_description(data, "germline_classification")
        total_data[count][i].append(data[positions[0] + 2])
    positions = findexstr(data, "canonical_spdi")
    total_data[count][positions[0]].append(data[positions[0] + 1])

def timer(count_time):
    while True:
        time.sleep(0.1)
        count_time[0] += 0.1


if len(argv) == 1:
    excel_file = load_workbook("GenoDENT_genes.xlsx")
    content = excel_file.active
    total_data = []
    if os.path.exists("gen_mutation.pickle"):
        with open("gen_mutation.pickle", "rb") as file:
            total_data = pickle.load(file)
    else:
        for i in range(len(content['B']) - 1):
            total_data.append([content['B' + str(i + 2)].value])
else:
    print("This program needs a simple array of genes' accession to work.")
    exit(0)





count_time = [0]
threading.Thread(target=timer, daemon=True, args=(count_time,)).start()
rps = []
print("threads", threading.active_count())
for count in range(len(total_data) - 1):
    print(len(total_data[count]), total_data[count])
    if len(total_data[count]) > 0: # > 1
        continue
    print("time :", count_time[0])
    rps.append(count_time[0])
    threading.Thread(target=divide_and_conquer, daemon=True, args=(total_data, count, 0, rps)).start()
    # print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy RPS :", rps)
    while count_time[0] - rps[0] <= 1.0 or len(rps) >= 10:
        time.sleep(0.1)
        # print("============================== RPS :", rps)
    with open("gen_mutation.pickle", "wb") as file:
        pickle.dump(total_data, file)
print(total_data)
iferror = 0
while threading.active_count() > 2 and iferror < 10:    #security mesure
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(0.5)
with open("gen_mutation.pickle", "wb") as file:
        pickle.dump(total_data, file)



count_time[0] = 0
rps = []
for count in range(len(total_data) - 1):
    if len(total_data[count]) <= 1:
        continue
    rps.append(count_time[0])
    threading.Thread(target=good_or_evil, daemon=False, args=(total_data, count)).start()
    while count_time[0] - rps[0] <= 1.0 or len(rps) >= 10:
        time.sleep(0.1)
while threading.active_count() > 2 and iferror < 10:    #security mesure
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(0.5)


count_time[0] = 0
rps = []
for count in range(len(total_data) - 1):
    if len(total_data[count]) <= 1:
        continue
    rps.append(count_time[0])
    threading.Thread(target=good_or_evil_recheck, daemon=False, args=(total_data, count)).start()
    while count_time[0] - rps[0] <= 1.0 or len(rps) >= 10:
        time.sleep(0.1)

while threading.active_count() > 2 and iferror < 10:    #security mesure
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(0.5)
time.sleep(3)
print(total_data)
with open("gen_mutation.pickle", "wb") as file:
        pickle.dump(total_data, file)
