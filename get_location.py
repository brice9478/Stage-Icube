import requests
import os
import re
import pickle
import threading
import time
from Bio import SeqIO
from io import StringIO
from sys import argv
from openpyxl import Workbook, load_workbook


def create_url(gen_loc, i, max):
    url = "https://www.ebi.ac.uk/proteins/api/coordinates?accession="
    for k in range(0, max):
        if i + k >= len(gen_loc):
            break
        if len(gen_loc[i + k]) > 1:
            continue
        url = url + gen_loc[i + k][0]
        if k < max - 1: #not necessary
            url = url + ","
    url = url + "&format=json"
    return url

def get_request(gen_loc, i, max, error):
    url = create_url(gen_loc, i, max)
    try:
        response = requests.get(url, timeout=10)
    except:
        if error >= 5:
            gen_loc[i].append(["Unknown"])
            off = 0
            while rps[off][1] != False:
                off += 1
            rps[off][1] = count_time[0]
            print("Request : all attempts failed.")
            return
        print("/!\ ---------> loop ? Connection error. Request sent again with url :", url)
        time.sleep(1) #waiting a little bit before sending the request again
        get_request(gen_loc, i, max, error + 1)
        return
    data = ''.join(response.text)
    data = re.sub(r"[\n\t\"\{\}\[\]]", '', data)
    data = re.split(r"[:,]", data)
    for k in range(0, max): #loop to find key-words of every protein's accession
        index = 0
        if len(gen_loc[i + k]) > 1:
            print(gen_loc[i + k][0], "---------- Checked ----------")
            continue
        while data[index] != gen_loc[i + k][0]:
            if index >= len(data) - 1:
                gen_loc[i + k].append("Unknown")
                break
            index += 1
        if index >= len(data):
            continue
        save_index = index
        while data[index] != "chromosome":
            index += 1
            if index > len(data):
                index = save_index
                print("Alternative", gen_loc[i + k][0])
                while data[index] or data[index] == "accession":
                    if data[index] == "id" and data[index + 2] == "start":
                        gen_loc[i + k].append("chromosome")
                        gen_loc[i + k].append("Unknown")
                        for info in range(2, 6):
                            gen_loc[i + k].append(data[index + info])
            if index >= len(data):
                break
            if data[index] == "chromosome" and data[index + 2] != "start":
                index += 1
            if data[index] == "accession":
                gen_loc[i + k].append("Unknown")
                break
        if index >= len(data) - 1 or data[index] == "accession" or data[index + 2] != "start":
            continue
        for info in range(6):
            gen_loc[i + k].append(data[index + info])
    try:
        off = 0
        while rps[off][1] != False:
            off += 1
        rps[off][1] = count_time[0]
    except:
        return
    return

def true_stop(stop):    #allows to stop the program when "enter" is pressed
    input()
    print("/!\\ -- Stop request received. The program will end shortly. -- /!\\")
    stop[0] = 1


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
    print("python3 get_location.py [file.txt]")
    print("file.txt : a file that contains a list of human genes' accession all separated by a \\n")
    print("The program will generate a pickle file named gen_loc.pickle.")
    print("If a file with the name \"gen_loc.pickle\" already exists, new information will be added to the already existing one.")
    print("If you wish to stop the program while it is still running and save what's already been done, you can press 'enter'.")
    print("note : if no file is given as argument, the program will automatically use the default orthologues.pickle")
    print("Info : if you have a doubt on any result, please try :")
    print("https://www.ebi.ac.uk/proteins/api/coordinates?accession=[?]&format=json \n\\--> replace [?] by the gene's accession")
    print("-----------------------------------------------------------------------------------------------------------------------")
    exit(0)


if len(argv) == 1:
    with open("orthologues.pickle", "rb") as file:
        total_data = pickle.load(file)
    if not os.path.exists("gen_loc.pickle") or os.path.getsize('gen_loc.pickle') == 0:
        if not os.path.exists("GenoDENT_genes.xlsx"):
            print("File GenoDENT_genes.xlsx not found.")
            exit(84)
        excel_file = load_workbook("GenoDENT_genes.xlsx")
        content = excel_file.active
        gen_loc = []
        for i in range(len(content['B']) - 1):
            gen_loc.append(content['B' + str(i + 2)].value)
        counter = len(content['B']) - 1
        for h_gene in range(0, len(total_data["genes"])):
            for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
                for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
                    gen_loc.append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
                    counter += 1
        gen_loc = list(set(gen_loc)) #remove duplicates
        gen_loc = [[item] for item in gen_loc]
        with open("gen_loc.pickle", "wb") as file:
            pickle.dump(gen_loc, file)
    else:
        with open("gen_loc.pickle", "rb") as file:
            gen_loc = pickle.load(file)

if len(argv) == 2:
    gen_loc = []
    if not os.path.exists(argv[1]):
        print("The file named", argv[1], "can't be found.")
        exit(84)
    if os.path.exists("gen_loc.pickle"):
        print("/!\\ gen_loc.pickle already exists. New informations will be added to the existing one. /!\\")
        with open("gen_loc.pickle", "rb") as file:
            gen_loc = pickle.load(file)
    with open(argv[1], 'r') as file:
        for line in file:
            if line == '\n':
                continue
            gen_loc.append([line.strip()])

start_time = [time.time()]
count_time = [0]
threading.Thread(target=timer, daemon=True, args=(count_time, start_time)).start()
rps = []
stop = []
stop.append(int(0))
stop[0] = 0 #just in case
threading.Thread(target=true_stop, daemon=True, args=(stop,)).start()

for i in range(0, len(gen_loc), 100):
    max = 100
    if i + max > len(gen_loc):
        max = len(gen_loc) - i
    if i % 1000 == 0:
        print(i)
    rps.append([count_time[0], False])
    threading.Thread(target=get_request, daemon=True, args=(gen_loc, i, max, 0)).start()
    while len(rps) >= 30:
        if rps[0][1] != False and count_time[0] - rps[0][1] > 1:
            break
        time.sleep(0.1)
    try:
        if rps[0][1] != False:
            del rps[0]
    except: #louche
        with open("gen_loc.pickle", "wb") as file:
            pickle.dump(gen_loc, file)
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
with open("gen_loc.pickle", "wb") as file:
    pickle.dump(gen_loc, file)
