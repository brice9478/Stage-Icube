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
            # print(data["data"][0]["inparalogs"][0])
            return data_list
    data_list[k][list(data_list[k].keys())[0]].append(data["data"][0]["inparalogs"][0])
    return data_list

def get_gene(total_data, data_list, i, j, gen_id, k):
    # print(list(total_data["genes"][i].keys())[0], str(total_data["genes"][i][gen_id][j]["specie"][1]))
    # url = "https://lbgi.fr/api/orthoinspector/Eukaryota2023/protein/" + list(total_data["genes"][i].keys())[0] + "/orthologs/" + str(total_data["genes"][i][gen_id][j]["specie"][1])
    # response = requests.get(url)
    # data = json.loads(response.text)
    # print(data)
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
# data_list.append({"Human": []})
# print(data_list)
for i in range(2, len(content['B'])):
    cell = 'B' + str(i)
    data_list[0]["Human"].append(content[cell].value)
# print(json.dumps(data_list, indent=3))
print(list(data_list[0].keys())[0])

switch = False
with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)
# print(len(total_data["genes"]))
# print(total_data["genes"][0]["Q9NRG9"])
for i in range(0, len(total_data["genes"])):
    cell = 'B' + str(i + 2)
    gen_id = content[cell].value
    for j in range(0, len(total_data["genes"][i][gen_id])):
        # print(len(total_data["genes"][i][gen_id]))
        for k in range(0, len(data_list)):
            # print(len(data_list))
            # first_letter = data_list[k].keys()
            # first_letter = list(data_list[k].keys())[0][0]
            # if total_data["genes"][i][gen_id][j]["specie"][0][0] == first_letter:
            # print("hrere",total_data["genes"][i][gen_id][j]["specie"][0], list(data_list[k].keys())[0])
            if total_data["genes"][i][gen_id][j]["specie"][1] + " " + total_data["genes"][i][gen_id][j]["specie"][0] == list(data_list[k].keys())[0]:
                switch = True
                data_list = get_gene(total_data, data_list, i, j, gen_id, k)
                # print(json.dumps(data_list, indent=3))
                # print(total_data["genes"][i][gen_id][j]["specie"][0], list(data_list[k].keys())[0])
                # if total_data["genes"][i][gen_id][j]["specie"][0] == list(data_list[k].keys())[0]:
                #     data_list = verify_existing_gene(total_data, data_list, i, j, gen_id, k)
                # else:
                #     data_list = new_specie(total_data, data_list, i, j, gen_id)
        if switch == False:
            data_list = new_specie(total_data, data_list, i, j, gen_id)
            # data_list = verify_existing_gene(total_data, data_list, i, j, gen_id, k + 1)
        else:
            switch = False
    with open("list_species_and_genes.pickle", "wb") as file:
        pickle.dump(data_list, file)
print(json.dumps(data_list, indent=3))
