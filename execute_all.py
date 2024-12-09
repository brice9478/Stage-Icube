import os

needed = ["fill_table_exon_structure.py", "fill_table_genes.py", "fill_table_mutations.py", "fill_table_pdi.py", "GenoDENT_genes.xlsx", "get_exon_structure.py",
          "get_location.py", "get_mutation.py", "get_orthologues.py", "get_seq.py", "create_db.py"]
for i in range(len(needed)):
    if not os.path.exists(needed[i]):
        print("The file", needed[i], "needs to be in the current directory to execute this program.")
        exit(84)

print("This program will remove all .pickle and .db file related to the different programs. Do you want to continue ? [yes/no]")
print("(note : the program will be taking between 30 minutes and an hour to fully execute)")
print(">> ", end = '')
if input() != "yes":
    exit(0)

print("This porgram needs an Api key in order to execute get_mutations.py. Please insert it after the \"<<\"")
print("(Find the api key on : https://account.ncbi.nlm.nih.gov/settings/)")
print(">> ", end = '')
api_key = input()

removed = ["exon_struct.pickle", "gen_loc.pickle", "gen_mutation.pickle", "orthologues.pickle", "gen_seq.pickle", "mydata.db"]
for i in range(len(removed)):
    if os.path.exists(removed[i]):
        str = "rm " + removed[i]
        os.system(str)

execution = ["get_orthologues.py", "get_seq.py", "get_location.py", "get_exon_structure.py", "get_mutation.py", "fill_table_genes.py",
             "fill_table_exon_structure.py", "fill_table_mutations.py", "fill_table_pdi.py", "create_db.py"]
for i in range(len(execution)):
    print("---------------------- Executing", execution[i], "----------------------")
    if execution[i] == "get_mutation.py":
        str = "python3 " + execution[i] + " " + api_key
    else:
        str = "python3 " + execution[i]
    os.system(str)