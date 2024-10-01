import requests

url = "https://discord.com/api/v9/channels/"id"/messages" #the big number is the ID of the channel

content = {
    "content" : "Je teste un truc : envoyer un message via un programme python"
}

headers = {
    "authorization" : "ODI4ODk1NDYxMTQxNjQzMjk1.Gc3Tb1.ogtZROqMam7UsfTiTUIvp5m-Y3nHB3BVNiTKJY"
}

requests.post(url, content, headers=headers)

# This program mustn't be used too often
