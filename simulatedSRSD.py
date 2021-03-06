import json
import requests
import glob
import re
import ast
import rstr
import time

""" This file simulates a future request from the SRSD in order compute the trust score of a set of product offers. 
The request should contain both the requester's DID (5GZORRO Platform participant) and multiple offers.
Currently, we have employed the RAN product offer template available in Confluence, but this template is subject to 
change based on decisions taken in the SRSD. """

#Load JSON files to simulate SRSD information regarding to product offers
#list_product_offers = sorted(glob.glob('./product_offer_examples/100_POs/RAN*.json'))
list_product_offers = sorted(glob.glob('./product_offer_examples/new_product_offer/*.json'))
ran_offers = []

#trustor_DID = {"trustorDID": rstr.xeger("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}")}
trustor_DID = {"trustorDID": "88-lm6s88-jv84-ii57-qq53-6166qvw8l3zt"}

ran_offers.append(trustor_DID)

for file_name in list_product_offers:
    with open(file_name, 'r') as file:
        file.seek(0)
        ran_offers.append(json.load(file))
        file.close()

print("The Smart Resource and Service Discovery application needs to identify the most trustworthy offer for", trustor_DID["trustorDID"], "\n")
#print("The available product offers are: \n\t- did:5gzorro:domain-B-RAN-1\n\t- did:5gzorro:domain-C-RAN-2\n\t- did:5gzorro:domain-D-RAN-1\n\t- did:5gzorro:domain-E-RAN-1")

"""object = {"trustorDID": "99lm6s88-jv84-ii57-qq53-6166qvw8l3zt", "trusteeDID": "KjuJxYb9ycEstuWMHjZSZ5", "offerDID": "MzCciMdUNovcBSbUspeQHf"}
response = requests.post("http://172.28.3.126:31115/query_trust_level", data=json.dumps(object).encode("utf-8"))
if response.status_code == 200:
    req = json.loads(response.text)
    print(req)
else:
    print("Error:", response)"""

start_time = time.time()
"5GBarcelona"
response = requests.post("http://172.28.3.15:31113/request_trust_scores", data=json.dumps(ran_offers).encode("utf-8"))

"5TONIC"
#response = requests.post("http://10.4.2.110:31113/request_trust_scores", data=json.dumps(ran_offers).encode("utf-8"))
#response = requests.post("http://localhost:5001/request_trust_scores", data=json.dumps(ran_offers).encode("utf-8"))

best_offer = {}
max_trust_score = 0.0

if response.status_code == 200:
    req = json.loads(response.text)
    req = req.replace("[", "")
    req = req.replace("]", "")
    req = re.findall(r'{.+?}.*?}', req)

    print("\nTrust scores according to the previous product offers are:\n ")
    for respuesta in req:
        print("\t-TrusteeDID: ",ast.literal_eval(respuesta)["trusteeDID"]["trusteeDID"],", offerDID: ",ast.literal_eval(respuesta)["trusteeDID"]["offerDID"]," new trust value --->", ast.literal_eval(respuesta)["trust_value"])
        if max_trust_score <= float(ast.literal_eval(respuesta)["trust_value"]):
            max_trust_score = float(ast.literal_eval(respuesta)["trust_value"])
            best_offer = {"offerDID": ast.literal_eval(respuesta)["trusteeDID"]["offerDID"]}
    print("%s seconds" % (time.time()-start_time))
else:
    print("Error:", response)

"We are finishing all the trust establishments"

#time.sleep(3)
#response = requests.post("http://172.28.3.15:31113/notify_final_selection", data=json.dumps(best_offer).encode("utf-8"))
#if response.status_code == 200:
    #print("Finished")
    #time.sleep(10)
    #response = requests.post("http://172.28.3.15:31113/stop_trust_relationship", data=json.dumps(best_offer).encode("utf-8"))
    #if response.status_code == 200:
        #print("Finished")
    #else:
        #print("Error:", response)
#else:
    #print("Error:", response)
