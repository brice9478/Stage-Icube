import pickle


with open("gen_mutation.pickle", "rb") as file:
    list_mutations = pickle.load(file)
new_list = []
count = 0
for i in range(len(list_mutations)):
    if i % 100 == 0:
        print(i)
    if len(list_mutations[i]) <= 1 or list_mutations[i][1] == "Aknown":
        continue
    for k in range(1, len(list_mutations[i])):
        try:
            list_mutations[i][k][4]
        except:
            print("Lack of informations:", list_mutations[i][k])
            continue
        if isinstance(list_mutations[i][k][4], str):
            new_list.append([count + 1])
            new_list[count].append(list_mutations[i][k][4])
            new_list[count].append(list_mutations[i][k][6])
            new_list[count].append(list_mutations[i][k][8])
            new_list[count].append(list_mutations[i][k][1])
            count += 1
        else:
            print("/!\\ Multiple values:", list_mutations[i][k])
            for z in range(len(list_mutations[i][k][4])):
                new_list.append([count + 1])
                new_list[count].append(list_mutations[i][k][4][z])
                new_list[count].append(list_mutations[i][k][6][z])
                new_list[count].append(list_mutations[i][k][8][z])
                new_list[count].append(list_mutations[i][k][1])
                count += 1

with open("table_pdi.pickle", "wb") as file:
    pickle.dump(new_list, file)

