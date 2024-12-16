import pickle

with open("orthologues.pickle", "rb") as file:
    total_data = pickle.load(file)
counter = 0
list_ortho = []
list_h_gene_to_ortho = []
for h_gene in range(0, len(total_data["genes"])):
    list_h_gene_to_ortho.append([h_gene + 1])
    list_h_gene_to_ortho[h_gene].append(list(total_data["genes"][h_gene].keys())[0])
    for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
        for access in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2])):
            list_ortho.append([counter + 1])
            list_ortho[counter].append(h_gene + 1)
            list_ortho[counter].append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][2][access])
            counter += 1
with open("table_orthologs.pickle", "wb") as file:
    pickle.dump(list_ortho, file)
with open("table_human_genes_to_orthologs.pickle", "wb") as file:
    pickle.dump(list_h_gene_to_ortho, file)
