import json
import requests
import glob
import re
import ast

""" This file simulates a future request from the SRSD in order compute the trust score of a set of product offers. 
The request should contain both the requester's DID (5GZORRO Platform participant) and multiple offers.
Currently, we have employed the RAN product offer template available in Confluence, but this template is subject to 
change based on decisions taken in the SRSD. """

#Load JSON files to simulate SRSD information regarding to product offers
list_product_offers = sorted(glob.glob('./RAN*.json'))
ran_offers = []

trustor_DID = {"trustorDID":"did:5gzorro:domain-A"}
ran_offers.append(trustor_DID)

for file_name in list_product_offers:
    with open(file_name, 'r') as file:
        file.seek(0)
        ran_offers.append(json.load(file))
        file.close()

print("The Smart Resource and Service Discovery application needs to identify the most trustworthy offer for", trustor_DID["trustorDID"], "\n")
print("The available product offers are: \n\t- did:5gzorro:domain-B-RAN-1\n\t- did:5gzorro:domain-C-RAN-2\n\t- did:5gzorro:domain-D-RAN-1\n\t- did:5gzorro:domain-E-RAN-1")
response = requests.post("http://localhost:5001/request_trust_scores", data=json.dumps(ran_offers).encode("utf-8"))

if response.status_code == 200:
    req = json.loads(response.text)
    req = req.replace("[", "")
    req = req.replace("]", "")
    req = re.findall(r'{.+?}.*?}', req)

    print("\nTrust scores according to the previous product offers are:\n ")
    for respuesta in req:
        print("\t-",ast.literal_eval(respuesta)["trusteeDID"]["trusteeDID"],"new trust value --->", ast.literal_eval(respuesta)["trust_value"])
else:
    print("Error:", response)