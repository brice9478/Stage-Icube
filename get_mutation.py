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

def findex(data, str):
    for i in range(len(data) - 1):
        if data[i] == str:
            return i
    return -1

def findexstr(data, str):
    positions = [i for i, x in enumerate(data) if x == str and data[i + 1] == "description"]
    return positions

def divide_and_conquer(total_data, count, error):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=" + str(total_data[count][0]) + "&retmode=fasta&BARULI9478"
    try:
        response = requests.get(url)
    except:
        if error >= 5:
            total_data[count].append(["Aknown"])
            return
        divide_and_conquer(total_data, count, error + 1)
        return
    data = ''.join(response.text)
    data = re.sub(r"[\n \t]", '', data)
    data = re.split(r"[><]", data)
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

def good_or_evil(total_data, count):
    if len(total_data[count]) == 1:
        return
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id="
    for i in range(1, len(total_data[count]) - 1):
        url = url + str(total_data[count][i][1])
        if i < len(total_data[count]) - 2:
            url = url + ", "
    url = url + "&retmode=fasta&BARULI9478"
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
    positions = findexstr(data, "germline_classification")
    for glc in range(len(positions) - 1):
        if len(total_data[count][glc + 1]) > 2:
            continue
        total_data[count][glc + 1].append(data[positions[glc] + 2])


def good_or_evil_recheck(total_data, count):
    if len(total_data[count]) == 1:
        return
    for i in range(1, len(total_data[count])):
        if len(total_data[count][i]) >= 3:
            continue
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=" + str(total_data[count][i][1]) + "&retmode=fasta&BARULI9478"
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
        positions = findexstr(data, "germline_classification")
        total_data[count][i].append(data[positions[0] + 2])




excel_file = load_workbook("GenoDENT_genes.xlsx")
content = excel_file.active
total_data = []
if os.path.exists("gen_mutation.pickle"):
    with open("gen_mutation.pickle", "rb") as file:
        total_data = pickle.load(file)
else:
    for i in range(len(content['B']) - 1):
        total_data.append([content['B' + str(i + 2)].value])


for count in range(len(total_data) - 1):
    print(len(total_data[count]), total_data[count])
    if len(total_data[count]) > 1:
        continue
    threading.Thread(target=divide_and_conquer, daemon=False, args=(total_data, count, 0)).start()
    while threading.active_count() >= 4:
        time.sleep(0.1)

print(total_data)
iferror = 0
while threading.active_count() > 1 and iferror < 10:    #security mesure
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(1)

with open("gen_mutation.pickle", "wb") as file:
        pickle.dump(total_data, file)

for count in range(len(total_data) - 1):
    if len(total_data[count]) <= 1:
        continue
    threading.Thread(target=good_or_evil, daemon=False, args=(total_data, count)).start()
    while threading.active_count() >= 4:
        time.sleep(0.1)

for count in range(len(total_data) - 1):
    if len(total_data[count]) <= 1:
        continue
    threading.Thread(target=good_or_evil_recheck, daemon=False, args=(total_data, count)).start()
    while threading.active_count() >= 4:
        time.sleep(0.1)

while threading.active_count() > 1 and iferror < 10:    #security mesure
    iferror = iferror + 1
    print("threads:", threading.active_count())
    time.sleep(1)
time.sleep(3)
print(total_data)
with open("gen_mutation.pickle", "wb") as file:
        pickle.dump(total_data, file)
