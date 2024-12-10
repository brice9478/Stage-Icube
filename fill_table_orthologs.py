import pickle

with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)
list_ortho = []
list_verify_double = []
counter = 0
for h_gene in range(0, len(total_data["genes"])):
    for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
        for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
            if counter % 1000 == 0:
                print(counter)
            if not total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access] in list_verify_double:
                list_ortho.append([counter + 1])
                list_verify_double.append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
                list_ortho[counter].append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
                list_ortho[counter].append(list(total_data["genes"][h_gene].keys())[0])
                counter += 1
            else:
                accession = total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access]
                index_map = {value: idx for idx, value in enumerate(list_verify_double)}
                if accession in index_map:
                    i = index_map[accession]
                    list_ortho[i][len(list_ortho[i]) - 1] = list_ortho[i][len(list_ortho[i]) - 1] + ";" + list(total_data["genes"][h_gene].keys())[0]
with open("table_orthologs.pickle", "wb") as file:
    pickle.dump(list_ortho, file)
