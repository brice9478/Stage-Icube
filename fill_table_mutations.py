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
            new_list.append([count + 1])
            new_list[count].append(list_mutations[i][k][1])
            try: #really strange shit like Error with: list_mutations[i][k] = ['id', '64843']
                new_list[count].append(list_mutations[i][k][2])
            except:
                new_list[count].append("Aknown")
            new_list[count].append(list_mutations[i][0])
            count += 1
        except:
            print("Error with:", list_mutations[i][k])


with open("table_mutations.pickle", "wb") as file:
    pickle.dump(new_list, file)

