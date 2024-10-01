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
    # data=''.join(response.text)
    id = 0
    search = "Vertebrata"
    data = json.loads(response.text)
    # data = json.dumps(data, indent=3)
    # print(json.dumps(data["data"], indent=3))
    names_list = ''
    ids_list = ''
    # print(len(data["data"]))
    for i in range(len(data["data"])):
        phylum = data["data"][i]["phylum"]
        phylum = phylum.split(';')
        for j in range(len(phylum)):
            # print(phylum[j])
            if phylum[j] == "7742":
                names_list = str(names_list) + str(data["data"][i]["name"]) + ";"
                ids_list = str(ids_list) + str(data["data"][i]["id"]) + ";"
                # print(phylum[j + 1], phylum[j])
        # print(data["data"][i])
    return names_list, ids_list
    # for i in range(len(data)):
    #     if data[i] == 'V':
    #         for t in range(10):
    #             if search[t] != data[i + t]:
    #                 break
    #         if t == 9:
    #             j = 2
    #             while isdigit(data[i - j]) == True:
    #                 j += 1
    #             j -= 1
    #             while j >= 2:
    #                 id = id * 10 + int(data[i - j])
    #                 j -= 1
    #             return id

excel_file = load_workbook("GenoDENT_genes.xlsx")
content = excel_file.active
# print(content)
# print("---------")
names_list, ids_list = get_vertebrata_id()
# print(names_list)
# print(ids_list)
ids_list = ids_list.split(';')
names_list = names_list.split(';')
# exit(0)
# total_data = {
#     "genes": []
# } #that is a dict
if not os.path.exists("orthologues.pickle"):
    total_data = {
        "genes": []
    } #that is a dict
else:
    with open("orthologues.pickle", "rb") as file:
        total_data = pickle.load(file)
original_len = len(total_data["genes"])

# for nb in range(2, len(content['B'])):
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
    # print(json.dumps(total_data, indent=3))

    counter = 0
    for i in range(len(data["data"])):
        for check_ids in range(len(ids_list) - 1):
            # print(int(ids_list[check_ids]))
            if data["data"][i]["species"] == int(ids_list[check_ids]):
                total_data["genes"][nb - 2][gen_id].append({"specie": ""})
                # print(json.dumps(total_data, indent=3))
                total_data["genes"][nb - 2][gen_id][counter]["specie"] = names_list[check_ids], ids_list[check_ids], data["data"][i]["orthologs"]
                # for ortho in range(0, len(data["data"][i]["orthologs"])):
                #     print(data["data"][i]["orthologs"][ortho])
                #     print(total_data["genes"][nb - 2][gen_id][counter]["specie"])
                #     total_data["genes"][nb - 2][gen_id][counter]["specie"].add(str(data["data"][i]["orthologs"][ortho]))
                counter += 1
                # print(ids_list[check_ids], end=';')
    print()
    # total_data = str(total_data) + str(data) + ";"
    # print(data)
    with open("orthologues.pickle", "wb") as file:
        pickle.dump(total_data, file)
# print(json.dumps(total_data, indent=3))
# pickle_object = pickle.dumps(total_data)

# print(json.dumps(pickle.loads(pickle_object), indent=3))
# total_data = total_data.split(";")
# print(total_data)


# with open("orthologues.pickle", "rb") as file:
#     print(pickle.load(file))




# print(str_ids[ids_index], end='')
# print(str_ids)
# Seq=StringIO(data)
# protSeq=list(SeqIO.parse(Seq,'fasta'))


