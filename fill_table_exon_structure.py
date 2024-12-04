import pickle


with open("exon_struct.pickle", "rb") as file:
    list_exon_struct = pickle.load(file)
new_list = []
count = 0
for i in range(len(list_exon_struct)):
    if i % 1000 == 0:
        print(i)
    if len(list_exon_struct[i]) <= 2:
        continue
    for k in range(1, len(list_exon_struct[i])):
        try:
            new_list.append([count + 1])
            new_list[count].append(list_exon_struct[i][k][11])
            new_list[count].append(list_exon_struct[i][k][2])
            new_list[count].append(list_exon_struct[i][k][4])
            new_list[count].append(list_exon_struct[i][k][7])
            new_list[count].append(list_exon_struct[i][k][9])
            new_list[count].append(list_exon_struct[i][0])
            count += 1
        except:
            print("Error with:", list_exon_struct[i])


with open("table_exon_struct.pickle", "wb") as file:
    pickle.dump(new_list, file)