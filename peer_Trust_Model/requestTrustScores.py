import json
import sys
import requests

from flask import Flask, request
from flask_restful import Resource, Api
from gevent.pywsgi import WSGIServer
#from trustManagementFramework import *

from gevent import monkey
monkey.patch_all()

app = Flask(__name__)
api = Api(app)

class request_trust_scores(Resource):

    def post(self):
        """ The POST method is triggered by the SRSD in order to compute the trust scores of a set of product offers """
        req = request.data.decode("utf-8")
        product_offers = json.loads(req)

        """Read the Trustor' DID and a list of product offers """
        list_product_offers = {}
        type_offer_list = {}
        trustor_acquired = False

        for i in product_offers:
            if trustor_acquired == False:
                list_product_offers['trustorDID'] = i['trustorDID']
                trustor_acquired = True
            else:
                """ Acquire both provider's DID and offer's DID """
                #did_provider = i['productSpecification']['relatedParty'][0]['extendedInfo']
                #did_resource = i['did']
                did_provider = i['offer_object']['productSpecification']['relatedParty'][0]['extendedInfo']
                did_resource = i['offer_did']
                type_offer_list[did_resource] = i['offer_category']

                """ If the provider already exits, a list of offers will be added to the same key """
                if did_provider in list_product_offers:
                    list_product_offers[did_provider].append(did_resource)
                else:
                    list_product_offers[did_provider] = [did_resource]


        requests.post("http://localhost:5002/initialise_offer_type", data=json.dumps(type_offer_list).encode("utf-8"))


        """ Initialize the process of requesting trust information of each offer and provider """
        response = requests.post("http://localhost:5002/start_data_collection", data=json.dumps(list_product_offers).encode("utf-8"))

        if response.status_code == 200:
            response = json.loads(response.text)
            """ Return a list of trust scores linked to the previous list of product offers """
            return response
        else:
            return response


class stop_trust_relationship(Resource):
    def post(self):
        """This method stops a trust relationship"""
        req = request.data.decode("utf-8")
        offerDID = json.loads(req)
        response = requests.post("http://localhost:5002/stop_relationship", data=json.dumps(offerDID).encode("utf-8"))

        if response.status_code == 200:
            response = json.loads(response.text)
            return response
        else:
            return response

class query_trust_info(Resource):
    def post(self):
        """ This method will request a recommendation to a given recommender after looking in the interactions in the Data Lake"""
        req = request.data.decode("utf-8")
        information = json.loads(req)

        response = requests.post("http://localhost:5002/query_trust_information", data=json.dumps(information).encode("utf-8"))

        if response.status_code == 200:
            response = json.loads(response.text)
            """ Return a list of trust scores linked to the previous list of product offers """
            return response
        else:
            return response


class query_trust_level(Resource):
    def post(self):
        """ This method will request a recommendation to a given recommender after looking in the interactions in the Data Lake"""
        req = request.data.decode("utf-8")
        information = json.loads(req)

        response = requests.post("http://localhost:5002/query_trust_score", data=json.dumps(information).encode("utf-8"))

        if response.status_code == 200:
            response = json.loads(response.text)
            """ Return a list of trust scores linked to the previous list of product offers """
            return response
        else:
            return response

class query_satisfaction_value(Resource):
    def post(self):
        """ This method will request a recommendation to a given recommender after looking in the interactions in the Data Lake"""
        req = request.data.decode("utf-8")
        information = json.loads(req)

        response = requests.post("http://localhost:5002/query_satisfaction_score", data=json.dumps(information).encode("utf-8"))

        if response.status_code == 200:
            response = json.loads(response.text)
            """ Return a list of trust scores linked to the previous list of product offers """
            return response
        else:
            return response

class notify_final_selection(Resource):
    def post(self):
        """ This method will inform to the 5G-TRMF about the best PO considered by ISSM-WFM """
        req = request.data.decode("utf-8")
        information = json.loads(req)

        response = requests.post("http://localhost:5002/notify_selection", data=json.dumps(information).encode("utf-8"))

        if response.status_code == 200:
            response = json.loads(response.text)
            """ Return a list of trust scores linked to the previous list of product offers """
            return response
        else:
            return response


def launch_server_REST(port):
    api.add_resource(request_trust_scores, '/request_trust_scores')
    api.add_resource(stop_trust_relationship, '/stop_trust_relationship')
    api.add_resource(query_trust_info, '/query_trust_info')
    api.add_resource(query_trust_level, '/query_trust_level')
    api.add_resource(query_satisfaction_value, '/query_satisfaction_value')
    api.add_resource(notify_final_selection, '/notify_final_selection')
    http_server = WSGIServer(('0.0.0.0', port), app)
    http_server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Usage: python3 requestTrustScores.py [port]")
    else:
        port = int(sys.argv[1])
        launch_server_REST(port)