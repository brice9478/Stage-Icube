import pickle
import openpyxl
import json
import os
import requests
from openpyxl import Workbook, load_workbook

def new_specie(total_data, data_list, i, j, gen_id):
    data_list.append({total_data["genes"][i][gen_id][j]["specie"][1] + " " + total_data["genes"][i][gen_id][j]["specie"][0]: []})
    return data_list

def verify_existing_gene(data_list, k, total_data, i, j, gen_id):
    for l in range(0, len(data_list[k][list(data_list[k].keys())[0]])):
        if data_list[k][list(data_list[k].keys())[0]][l] == total_data["genes"][i][gen_id][j]["specie"][] :
            return data_list
    data_list[k][list(data_list[k].keys())[0]].append(data["data"][0]["inparalogs"][0])
    return data_list

def get_gene(total_data, data_list, i, j, gen_id, k):
    data_list = verify_existing_gene(data_list, k, total_data, i, j, gen_id)
    return data_list

excel_file = load_workbook("GenoDENT_genes.xlsx")
content = excel_file.active
if not os.path.exists("list_species_and_genes.pickle"):
    data_list = [{
        "Human": []
    }]
else:
    with open("list_species_and_genes.pickle", "rb") as file:
        data_list = pickle.load(file)
for i in range(2, len(content['B'])):
    cell = 'B' + str(i)
    data_list[0]["Human"].append(content[cell].value)
print(list(data_list[0].keys())[0])

switch = False
with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)
for i in range(0, len(total_data["genes"])):
    cell = 'B' + str(i + 2)
    gen_id = content[cell].value
    for j in range(0, len(total_data["genes"][i][gen_id])):
        for k in range(0, len(data_list)):
            if total_data["genes"][i][gen_id][j]["specie"][1] + " " + total_data["genes"][i][gen_id][j]["specie"][0] == list(data_list[k].keys())[0]:
                switch = True
                data_list = get_gene(total_data, data_list, i, j, gen_id, k)
        if switch == False:
            data_list = new_specie(total_data, data_list, i, j, gen_id)
        else:
            switch = False
    with open("list_species_and_genes.pickle", "wb") as file:
        pickle.dump(data_list, file)
print(json.dumps(data_list, indent=3))
