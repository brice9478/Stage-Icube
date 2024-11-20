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
from sys import argv
import threading



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

def get_request(gen_accession, total_data, nb, error):
        print(gen_accession)
        base_url="https://lbgi.fr/api/orthoinspector/Eukaryota2023/protein/"
        complete_url = base_url + str(gen_accession) + "/orthologs"
        try:
            response = requests.get(complete_url, timeout=10)
        except:
            if error >= 5:
                off = 0
                while rps[off][1] != False:
                    off += 1
                rps[off][1] = count_time[0]
                print("Request : all attempts failed.")
                return
            print("/!\ ---------> loop ? Connection error. Request sent again with url :", complete_url)
            time.sleep(1) #waiting a little bit before sending the request again
            get_request(gen_accession, total_data, nb, error + 1)
            return
        try:
            data = json.loads(response.text)
            # print(data)
            counter = 0
            for i in range(len(data["data"])):
                for check_ids in range(len(ids_list) - 1):
                    if data["data"][i]["species"] == int(ids_list[check_ids]):
                        total_data["genes"][nb][gen_accession].append({"specie": ""})
                        total_data["genes"][nb][gen_accession][counter]["specie"] = names_list[check_ids], ids_list[check_ids], data["data"][i]["orthologs"]
                        counter += 1
        except:
            if error >= 5:
                total_data["genes"][nb][gen_accession].append("Aknown")
                off = 0
                while rps[off][1] != False:
                    off += 1
                rps[off][1] = count_time[0]
                print("Request : all attempts failed.")
                return
            get_request(gen_accession, total_data, nb, error + 1)
            return
        # print()
        try:
            off = 0
            while rps[off][1] != False:
                off += 1
            rps[off][1] = count_time[0]
        except:
            return
        return

def timer(count_time, start_time):
    count_second = 0
    while True:
        if count_time[0] >= count_second + 1:
            count_second += 1
        count_time[0] = time.time() - start_time[0]

def true_stop(stop):    #allows to stop the program when "enter" is pressed
    input()
    print("/!\\ -- Stop request received. The program will end shortly. -- /!\\")
    stop[0] = 1

if len(argv) > 2:
    print("retry with -h for sole argument")
    exit(84)

if len(argv) == 2 and argv[1] == "-h":
    print("-----------------------------------------------------------------------------------------------------------------------")
    print("python3 get_orthologues.py [file.txt]")
    print("file.txt : a file that contains a list of human genes' accession all separated by a \\n")
    print("The program will generate a pickle file named orthologues.pickle.")
    print("If a file with the name \"orthologues.pickle\" already exists, new information will be added to the already existing one.")
    print("If you wish to stop the program while it is still running and save what's already been done, you can press 'enter'.")
    print("note : if no file is given as argument, the program will automatically use the default orthologues.pickle")
    print("Info : if you have a doubt on any result, please try :")
    print("https://www.ebi.ac.uk/proteins/api/coordinates?accession=[?]&format=json \n\\--> replace [?] by the gene's accession")
    print("-----------------------------------------------------------------------------------------------------------------------")
    exit(0)

start_time = [time.time()]
count_time = [0]
threading.Thread(target=timer, daemon=True, args=(count_time, start_time)).start()
rps = []

stop = []
stop.append(int(0))
stop[0] = 0 #just in case
threading.Thread(target=true_stop, daemon=True, args=(stop,)).start()

names_list, ids_list = get_vertebrata_id()
ids_list = ids_list.split(';')
names_list = names_list.split(';')

if len(argv) == 1:
    excel_file = load_workbook("GenoDENT_genes.xlsx")
    content = excel_file.active
    if not os.path.exists("orthologues.pickle"):
        total_data = {
            "genes": []
        } #that is a dict
    else:
        with open("orthologues.pickle", "rb") as file:
            total_data = pickle.load(file)
    original_len = len(total_data["genes"])
    for nb in range(original_len, original_len + len(content['B']) - 1):
        cell = 'B' + str(nb + 2 - original_len)
        print(cell)
        gen_accession = content[cell].value
        rps.append([count_time[0], False])
        total_data["genes"].append({gen_accession: []})
        threading.Thread(target=get_request, daemon=True, args=(gen_accession, total_data, nb, 0)).start()
        while len(rps) >= 20:
            if rps[0][1] != False and count_time[0] - rps[0][1] > 1:
                break
            time.sleep(0.1)
        try:
            if rps[0][1] != False:
                del rps[0]
        except:
            lets_continue = 1
        if stop[0] == 1:
            break

if len(argv) == 2:
    list = []
    with open(argv[1], 'r') as file:
        for line in file:
            if line == '\n':
                continue
            list.append(line.strip())
    if not os.path.exists("orthologues.pickle"):
        total_data = {
            "genes": []
        } #that is a dict
    else:
        with open("orthologues.pickle", "rb") as file:
            total_data = pickle.load(file)
    original_len = len(total_data["genes"])
    for nb in range(original_len, original_len + len(list)):
        print(nb)
        gen_accession = list[nb - original_len]
        rps.append([count_time[0], False])
        total_data["genes"].append({gen_accession: []})
        threading.Thread(target=get_request, daemon=True, args=(gen_accession, total_data, nb, 0)).start()
        while len(rps) >= 20:
            if rps[0][1] != False and count_time[0] - rps[0][1] > 1:
                break
            time.sleep(0.1)
        try:
            if rps[0][1] != False:
                del rps[0]
        except:
            lets_continue = 1
        if stop[0] == 1:
            break

stop[0] = 0 #reset variable stop when "enter" is pressed
while threading.active_count() > 3: #waiting for threads to finish their tasks before final pickle.dump
    if stop[0] == 1:
        break
    print("threads still active :", threading.active_count())
    time.sleep(1)
time.sleep(1)
print("end")
with open("orthologues.pickle", "wb") as file:
    pickle.dump(total_data, file)
