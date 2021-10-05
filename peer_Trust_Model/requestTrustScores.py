import json
import sys
import requests

from flask import Flask, request
from flask_restful import Resource, Api
from gevent.pywsgi import WSGIServer

from gevent import monkey
monkey.patch_all()

app = Flask(__name__)
api = Api(app)

class request_trust_scores(Resource):
    def post(self):
        """ The POST method is triggered by the SRSD in order to compute the trust scores of a set of product offers """
        req = request.data.decode("utf-8")
        product_offers = json.loads(req)

        """Read a list of product offers and Trustor' DID """
        list_product_offers = {}
        trustor_acquired = False

        for i in product_offers:
            if trustor_acquired == False:
                list_product_offers['trustorDID'] = i['trustorDID']
                trustor_acquired = True
            else:
                """ Acquire both provider's DID and offer's DID """
                #did_provider = i['productSpecification']['relatedParty'][0]['href']
                #did_resource = i['productSpecification']['resourceSpecification'][0]['href']
                """ The current JSONs does not provide the DID in the href field but the ID field"""
                did_provider = i['productSpecification']['relatedParty'][0]['extendedInfo']
                did_resource = i['did']

                """ If the provider already exits, a list of offers will be added to the same key """
                if did_provider in list_product_offers:
                    list_product_offers[did_provider].append(did_resource)
                else:
                    list_product_offers[did_provider] = [did_resource]

        """ Initialize the process of requesting trust information of each offer and provider """
        response = requests.post("http://localhost:5002/start_data_collection", data=json.dumps(list_product_offers).encode("utf-8"))

        if response.status_code == 200:
            response = json.loads(response.text)
            """ Return a list of trust scores linked to the previous list of product offers """
            return response
        else:
            return response

def launch_server_REST(port):
    api.add_resource(request_trust_scores, '/request_trust_scores')
    http_server = WSGIServer(('0.0.0.0', port), app)
    http_server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Usage: python3 requestTrustScores.py [port]")
    else:
        port = int(sys.argv[1])
        launch_server_REST(port)