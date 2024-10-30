import requests
import openpyxl
import time
import json
import pickle
import os
from curses.ascii import isdigit
from Bio import SeqIO
from io import StringIO
from openpyxl import Workbook, load_workbook
from math import *

def get_vertebrata_id():
    url="https://lbgi.fr/api/orthoinspector/Eukaryota2023/species"
    response = requests.get(url)
    data = json.loads(response.text)
    names_list = ''
    ids_list = ''
    for i in range(len(data["data"])):
        phylum = data["data"][i]["phylum"]
        phylum = phylum.split(';')
        for j in range(len(phylum)):
            if phylum[j] == "7742":
                names_list = str(names_list) + str(data["data"][i]["name"]) + ";"
                ids_list = str(ids_list) + str(data["data"][i]["id"]) + ";"
    return names_list, ids_list

excel_file = load_workbook("GenoDENT_genes.xlsx")
content = excel_file.active
names_list, ids_list = get_vertebrata_id()
ids_list = ids_list.split(';')
names_list = names_list.split(';')
if not os.path.exists("orthologues.pickle"):
    total_data = {
        "genes": []
    } #that is a dict
else:
    with open("orthologues.pickle", "rb") as file:
        total_data = pickle.load(file)
original_len = len(total_data["genes"])

for nb in range(original_len + 2, original_len + 102):
    if nb > len(content['B']):
        break
    cell = 'B' + str(nb)
    print(cell)
    gen_id = content[cell].value
    total_data["genes"].append({gen_id: []})
    print(gen_id)
    base_url="https://lbgi.fr/api/orthoinspector/Eukaryota2023/protein/"
    complete_url = base_url + str(gen_id) + "/orthologs"
    response = requests.get(complete_url)
    data = json.loads(response.text)

    counter = 0
    for i in range(len(data["data"])):
        for check_ids in range(len(ids_list) - 1):
            if data["data"][i]["species"] == int(ids_list[check_ids]):
                total_data["genes"][nb - 2][gen_id].append({"specie": ""})
                total_data["genes"][nb - 2][gen_id][counter]["specie"] = names_list[check_ids], ids_list[check_ids], data["data"][i]["orthologs"]
                counter += 1
    print()
    with open("orthologues.pickle", "wb") as file:
        pickle.dump(total_data, file)
