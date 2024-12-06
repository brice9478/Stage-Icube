import pickle
import threading
import time
import os
from openpyxl import Workbook, load_workbook


def timer(count_time, start_time):
    count_second = 0
    while True:
        if count_time[0] >= count_second + 1:
            count_second += 1
        count_time[0] = time.time() - start_time[0]

def find_same_accession(accession, searched_list_array):
    position = -1
    for i in range(len(searched_list_array)):
        if searched_list_array[i][0] == accession:
            position = i
            break
    if i >= len(searched_list_array):
        position = -1
    return position


with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)
if not os.path.exists("GenoDENT_genes.xlsx"):
    print("File GenoDENT_genes.xlsx not found.")
    exit(84)
excel_file = load_workbook("GenoDENT_genes.xlsx")
content = excel_file.active
list_genes = []
for i in range(len(content['B']) - 1):
    list_genes.append([content['B' + str(i + 2)].value])
    list_genes[i].append("Homo sapiens")
counter = len(content['B']) - 1
for h_gene in range(0, len(total_data["genes"])):
    for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
        for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
            list_genes.append([total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access]])
            list_genes[counter].append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][0])
            counter += 1
list_genes = list({item[0]: item for item in list_genes}.values())
list_genes = sorted(list_genes, key=lambda x: x[0])
print(list_genes[0])


with open("gen_seq.pickle", "rb") as file:
    gen_seq = pickle.load(file)
    gen_seq = sorted(gen_seq, key=lambda x: x[0])
with open("gen_loc.pickle", "rb") as file:
    gen_loc = pickle.load(file)
    gen_loc = sorted(gen_loc, key=lambda x: x[0])
print(gen_loc[0])
print(gen_seq[0])

for i in range(len(list_genes)):
    if i % 1000 == 0:
        print(i)
    #add sequence
    if gen_seq[i][0] == list_genes[i][0]:
        position = i
    else:
        position = find_same_accession(list_genes[i][0], gen_seq)
    if position != -1:
        list_genes[i].append(gen_seq[position][1])
    else:
        list_genes[i].append("Aknown")
    #add genome location (chromosome, start & end)
    if gen_loc[i][0] == list_genes[i][0]:
        position = i
    else:
        position = find_same_accession(list_genes[i][0], gen_loc)
    if position != -1:
        if len(gen_loc[position]) == 1 or gen_loc[position][1] == "Aknown":
            for a in range(3):
                list_genes[i].append("Aknown")
        else:
            list_genes[i].append(gen_loc[position][2])
            list_genes[i].append(gen_loc[position][4])
            list_genes[i].append(gen_loc[position][6])

with open("table_genes.pickle", "wb") as file:
    pickle.dump(list_genes, file)

