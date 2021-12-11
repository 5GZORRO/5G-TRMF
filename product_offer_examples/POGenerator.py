import json
import rstr

PO_base = ''

file = open("RAN_offer_domain_B.json", 'r')
file.seek(0)
PO_base = json.load(file)
file.close()

for i in range(100,1000,100):
    file = open(str(i)+'_POs/RAN_offer_domain_'+str(i)+'.json', mode='a')
    PO_base['productSpecification']['relatedParty'][0]['extendedInfo'] = rstr.xeger\
        ("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}")
    PO_base['did'] = rstr.xeger("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}")
    file.write(json.dumps(PO_base))