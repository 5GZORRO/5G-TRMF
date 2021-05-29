import json
import requests
import glob


#Load JSON files to simulate SRSD information regarding to product offers
list_product_offers = sorted(glob.glob('./RAN*.json'))
ran_offers = []

trustor_DID = {"trustorDID":"did:5gzorroTrustor:rotsurT"}
ran_offers.append(trustor_DID)

for file_name in list_product_offers:
    with open(file_name, 'r') as file:
        file.seek(0)
        ran_offers.append(json.load(file))
        file.close()

response = requests.post("http://localhost:5001/request_trust_scores", data=json.dumps(ran_offers).encode("utf-8"))

if response.status_code == 200:
    req = json.loads(response.text)
    print ("Simulated SRSD: ", req)
else:
    print (response)