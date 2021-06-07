import json
import sys
import logging
from flask import Flask, request
from flask_restful import Resource, Api
from gevent.pywsgi import WSGIServer
import random
import time
import requests
import ast
import re
from pymongo import MongoClient
import pprint

from peerTrust import *
from producer import *
from trustInformationTemplate import *
import consumer
from datetime import datetime
#logging.basicConfig(level=logging.INFO)

from gevent import monkey
monkey.patch_all()

app = Flask(__name__)
api = Api(app)

producer = Producer()
peerTrust = PeerTrust()

client = MongoClient(host='mongodb', port=27017, username='5gzorro', password='password')
db = client.rptutorials
mongoDB = db.tutorial

class start_data_collection(Resource):
    """ This method is responsible for creating a kafka topic for each offer.
     After creating the Kafka Topics the gatherInformation method will be instantiated """
    def post(self):
        req = request.data.decode("utf-8")
        dict_product_offers = json.loads(req)

        """ Retrieve the Trustor DID """
        trustor_acquired = False
        trustorDID = ""

        """ Adding a set of minimum interactions between entities that compose the trust model """
        peerTrust.minimumTrustValuesDLT(producer)

        trust_scores = []

        for trustee in dict_product_offers:
            if trustor_acquired == False:
                trustorDID = next(iter(dict_product_offers.values()))
                topic_trustorDID = trustorDID.split(":")[2]
                trustor_acquired = True
            else:
                for offer in dict_product_offers[trustee]:
                    """ Retrieve last part of DIDs to generate a unique kafka topic """
                    topic_offerDID = offer.split(":")[2]
                    topic_trusteeDID = trustee.split(":")[2]

                    """ Generating kafka topic where all interactions with a trustee are registered """
                    registered_offer_interaction = topic_trusteeDID + "-" + topic_offerDID
                    producer.createTopic(topic_trusteeDID)
                    """ Generating kafka topic where all trustor's interactions with a trustee are registered """
                    provider_topic_name = topic_trustorDID+"-"+topic_trusteeDID
                    result = producer.createTopic(provider_topic_name)
                    """ Generating kafka topic where all trustor's interactions with a trustee and 
                    an particular offer are registered """
                    full_topic_name = topic_trustorDID+"-"+topic_trusteeDID+"-"+topic_offerDID
                    result = producer.createTopic(full_topic_name)

                    if result == 1:
                        """ we generated initial trust information to avoid the cold start"""
                        peerTrust.generateHistoryTrustInformation(producer, trustorDID, trustee, offer, provider_topic_name, full_topic_name, topic_trusteeDID,registered_offer_interaction,3)

                        """Change if we consider a higher offer number"""
                        if list(dict_product_offers).index(trustee) == 1:
                            peerTrust.setTrustee1Interactions(producer, trustee)
                        elif list(dict_product_offers).index(trustee) == 2:
                            peerTrust.setTrustee2Interactions(producer, trustee)
                        elif list(dict_product_offers).index(trustee) == 3:
                            peerTrust.setTrustee3Interactions(producer, trustee)
                        else:
                            peerTrust.setTrustee4Interactions(producer, trustee)

                        """ Retrieve information from trustor and trustee """
                        data = {"trustorDID": trustorDID, "trusteeDID": trustee, "offerDID": offer, "topicName": full_topic_name}
                        response = requests.post("http://localhost:5002/gather_information", data=json.dumps(data).encode("utf-8"))
                        response = json.loads(response.text)
                        trust_scores.append(response)
                    else:
                        logging.info("Error generating a Kafka topic")
        client.close()
        return response


    """def getTrusteeSatisfactionDLT(self, trusteeDID):
        return None"""

class gather_information(Resource):
    def post(self):
        """ This method will retrieve information from the DataLake (kafka topic direct trust) +
        search for supplier/offer interactions in the simulated DLT to retrieve recommendations from
        other kafka topics (indirect trust). Currently there is no interaction with DataLake, we generate our
        internal Kafka topics """

        """ Retrieve parameters from post request"""
        req = request.data.decode("utf-8")
        parameter = json.loads(req)

        trustorDID = parameter["trustorDID"]
        trusteeDID = parameter["trusteeDID"]
        offerDID = parameter["offerDID"]
        topic_name = parameter["topicName"]

        """Read last value registered in Kafka"""
        last_trust_value = consumer.readLastTrustValue(topic_name)
        #print("LAST VALUES ------->",last_trust_value, topic_name)

        """Read interactions related to a Trustee"""
        interactions = self.getInteractionTrustee(trusteeDID)
        #print("TRUSTEEDID interactions ---->", trusteeDID, "\n" ,interactions)

        """ Retrieve information from trustor and trustee """
        trust_information = []
        current_offer = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID, "topicName": topic_name, "lastValue": last_trust_value, "trusteeInteractions": json.dumps(interactions)}
        trust_information.append(current_offer)

        response = requests.post("http://localhost:5002/compute_trust_level", data=json.dumps(trust_information).encode("utf-8"))

        response = json.loads(response.text)

        return response

    def getInteractionTrustee(self, trusteeDID):
        """ This method retrieves all interactions related to a Trustee"""
        interactions = []

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = peerTrust.stringToDictionaryList()

            for i in new_interaction_list:
                if i["trustorDID"] == trusteeDID:
                    interactions.append(i)

        return interactions

class compute_trust_level(Resource):
    def post(self):
        """This method retrieves the last value of the Trustor for a particular Trustee and the Trustee's interactions.
        It will then do the summation from its last computed value to the recent one by updating it trust value over
        the trustee """

        """ Retrieve parameters from post request"""
        req = request.data.decode("utf-8")
        parameter = json.loads(req)

        print("Compute Parameters --->", parameter)

        for i in parameter:
            current_trustee = i['trusteeDID']
            trustorDID = i['trustorDID']
            offerDID = i['offerDID']

            """ Recovering the last trust information """
            last_trustee_interaction_registered = i['lastValue']['totalInteractionNumber']
            last_satisfaction = i['lastValue']['trusteeSatisfaction']
            last_credibility = i['lastValue']['credibility']
            last_transaction_factor = i['lastValue']['transactionFactor']
            last_community_factor = i['lastValue']['communityFactor']
            last_interaction_number = i['lastValue']['interaction_number']
            last_trust_value = i['lastValue']['trust_value']

            response = {"trustorDID": trustorDID, "trusteeDID": {"trusteeDID": current_trustee, "offerDID": offerDID}, "trust_value": i['lastValue']["trust_value"], "evaluation_criteria": "Inter-domain", "initEvaluationPeriod": i['lastValue']["initEvaluationPeriod"],"endEvaluationPeriod": i['lastValue']["endEvaluationPeriod"]}

            """ Retrieving new trustee's interactions """
            current_trustee_interactions = i['trusteeInteractions']
            current_trustee_interactions = current_trustee_interactions.replace("[", "")
            current_trustee_interactions = current_trustee_interactions.replace("]", "")
            current_trustee_interactions = re.findall(r'{.*?}', current_trustee_interactions)

            new_satisfaction = 0.0
            new_credibility = 0.0
            new_transaction_factor = 0.0
            new_community_factor = 0.0
            counter_new_interactions = 0

            """Obtaining the last interaction registered by the Trustee in the DLT """
            last_interaction_DLT = current_trustee_interactions[len(current_trustee_interactions)-1]
            last_interaction_DLT = ast.literal_eval(last_interaction_DLT)

            if last_interaction_DLT['currentInteractionNumber'] > last_trustee_interaction_registered:
                for new_interaction in current_trustee_interactions:
                    topic_name = current_trustee.split(":")[2]+"-"+ast.literal_eval(new_interaction)['trusteeDID'].split(":")[2]
                    new_trustee_interaction = consumer.readLastTrustValues(topic_name, last_trustee_interaction_registered, ast.literal_eval(new_interaction)['currentInteractionNumber'])
                    print("Previous values --->",new_trustee_interaction, "--->", topic_name)
                    for i in new_trustee_interaction:
                        new_satisfaction = new_satisfaction + i['trusteeSatisfaction']
                        new_credibility = new_credibility + peerTrust.credibility(current_trustee, ast.literal_eval(new_interaction)['trusteeDID'])
                        new_transaction_factor = new_transaction_factor + peerTrust.transactionContextFactor(current_trustee, ast.literal_eval(new_interaction)['trusteeDID'], ast.literal_eval(new_interaction)['offerDID'])
                        new_community_factor = new_community_factor + peerTrust.communityContextFactor(current_trustee, ast.literal_eval(new_interaction)['trusteeDID'])
                        counter_new_interactions += 1

                """ Updating the last value with the summation of new interactions"""
                print("NEW VALUES --->", new_satisfaction/counter_new_interactions, new_credibility/counter_new_interactions, new_transaction_factor/counter_new_interactions, new_community_factor/counter_new_interactions)
                new_satisfaction = round(((new_satisfaction/counter_new_interactions) + last_satisfaction)/2, 3)
                new_credibility = round(((new_credibility/counter_new_interactions) + last_credibility)/2, 3)
                new_transaction_factor = round(((new_transaction_factor/counter_new_interactions) + last_transaction_factor)/2, 3)
                new_community_factor = round(((new_community_factor/counter_new_interactions) + last_community_factor)/2, 3)
                print("UPDATE VALUES --->", new_satisfaction, new_credibility, new_transaction_factor, new_community_factor)

                trustInformationTemplate = TrustInformationTemplate()
                information = trustInformationTemplate.trustTemplate()
                information["trustee"]["trusteeDID"] = current_trustee
                information["trustee"]["offerDID"] = offerDID
                information["trustee"]["trusteeSatisfaction"] = new_satisfaction
                information["trustor"]["trustorDID"] = trustorDID
                information["trustor"]["trusteeDID"] = current_trustee
                information["trustor"]["offerDID"] = offerDID
                information["trustor"]["credibility"] = new_credibility
                information["trustor"]["transactionFactor"] = new_transaction_factor
                information["trustor"]["communityFactor"] = new_community_factor
                information["trustor"]["direct_parameters"]["userSatisfaction"] = round((round(random.uniform(0.75, 0.95), 3) + i["userSatisfaction"])/2, 3)
                direct_weighting = round(random.uniform(0.6, 0.7),2)
                information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
                information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting
                information["trustor"]["direct_parameters"]["interactionNumber"] = last_interaction_number+1
                information["trustor"]["direct_parameters"]["totalInteractionNumber"] = peerTrust.getLastTotalInteractionNumber(current_trustee)
                information["trust_value"] = round(direct_weighting*(new_satisfaction*new_credibility*new_transaction_factor)+(1-direct_weighting)*new_community_factor,3)
                information["currentInteractionNumber"] = peerTrust.getCurrentInteractionNumber(trustorDID)
                information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
                information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

                response = {"trustorDID": trustorDID, "trusteeDID": {"trusteeDID": current_trustee, "offerDID": offerDID}, "trust_value": information["trust_value"], "currentInteractionNumber": information["currentInteractionNumber"],"evaluation_criteria": "Inter-domain", "initEvaluationPeriod": information["initEvaluationPeriod"],"endEvaluationPeriod": information["endEvaluationPeriod"]}

                print("Previous Trust score --->", last_trust_value, "NEW trust score --->", information["trust_value"])

                registered_offer_interaction = current_trustee.split(":")[2] + "-" + offerDID.split(":")[2]
                producer.createTopic(registered_offer_interaction)
                provider_topic_name = trustorDID.split(":")[2]+"-"+current_trustee.split(":")[2]
                producer.createTopic(provider_topic_name)
                full_topic_name = trustorDID.split(":")[2]+"-"+current_trustee.split(":")[2]+"-"+offerDID.split(":")[2]
                producer.createTopic(full_topic_name)

                message = {"interaction": trustorDID+" has interacted with "+current_trustee}
                producer.sendMessage(current_trustee.split(":")[2], registered_offer_interaction, message)
                producer.sendMessage(provider_topic_name, provider_topic_name, information)
                producer.sendMessage(full_topic_name, full_topic_name, information)

                data = "}\\n{\\\"trustorDID\\\": \\\""+trustorDID+"\\\", \\\"trusteeDID\\\": \\\""+current_trustee+"\\\", \\\"offerDID\\\": \\\""+offerDID+"\\\",\\\"userSatisfaction\\\": "+str(information["trustor"]["direct_parameters"]["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information["trustor"]["direct_parameters"]["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information["trustor"]["direct_parameters"]["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information["currentInteractionNumber"])+"}\""
                previous_file = ""

                with open('DLT.json', 'r') as file:
                    file.seek(0)
                    previous_file = file.read()
                    file.close()

                with open('DLT.json', 'w') as file:
                    new_file = previous_file.replace("}\"", data)
                    file.write(new_file)
                    file.close()

                requests.post("http://localhost:5002/store_trust_level", data=json.dumps(information).encode("utf-8"))

        return response

class store_trust_level(Resource):
    def post(self):
        """ This method is employed to register direct trust in our internal database """
        req = request.data.decode("utf-8")
        information = json.loads(req)

        mongoDB.insert_one(information)
        #pprint.pprint(mongoDB.find_one({"trustorDID": trustorDID}))
        #mongoDB.insert_many([tutorial2, tutorial1])
        #for doc in mongoDB.find():
        #pprint.pprint(doc)

        return 200

class update_trust_level(Resource):
    def post(self):
        """ This method updates a trust score based on certain SLA events. More events need to be considered,
        it is only an initial version"""

        req = request.data.decode("utf-8")
        information = json.loads(req)

        slaBreachPredictor_topic = information["SLABreachPredictor"]
        topic_key = information["key"]

        notifications = consumer.readSLANotification(slaBreachPredictor_topic, topic_key)
        print("Nofitications: ", notifications)

        positive_notification = "was able to manage the SLA violation successfully"
        negative_notification = "was not able to manage the SLA violation successfully"
        first_range_probability = 0.25
        second_range_probability = 0.50
        third_range_probability = 0.75
        fourth_range_probability = 1.0

        new_trust_score = 0.0

        for notification in notifications:
            current_notification = notification["notification"]
            likehood = notification["notification"].split("probability of")[1].split("\n")[0]
            likehood = float(likehood)

            last_trust_score = consumer.readAllInformationTrustValue(topic_key)

            if positive_notification in current_notification:
                if likehood <= first_range_probability:
                    new_trust_score = last_trust_score["trust_value"] + last_trust_score["trust_value"]*0.075
                elif likehood <= second_range_probability:
                    new_trust_score = last_trust_score["trust_value"] + last_trust_score["trust_value"]*0.10
                elif likehood <= third_range_probability:
                    new_trust_score = last_trust_score["trust_value"] + last_trust_score["trust_value"]*0.125
                elif likehood <= fourth_range_probability:
                    new_trust_score = last_trust_score["trust_value"] + last_trust_score["trust_value"]*0.15
            elif negative_notification in current_notification:
                if likehood <= first_range_probability:
                    new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.075
                elif likehood <= second_range_probability:
                    new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.10
                elif likehood <= third_range_probability:
                    new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.125
                elif likehood <= fourth_range_probability:
                    new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.15

            if new_trust_score > 1.0:
                new_trust_score = 1.0
            elif new_trust_score < 0.0:
                new_trust_score = 0.0

            print("Previous Trust Score --->", last_trust_score ["trust_value"], "Updated Trust Score -->", new_trust_score)
            last_trust_score["trust_value"] = round(new_trust_score, 3)
            last_trust_score["endEvaluationPeriod"] = datetime.timestamp(datetime.now())
            producer.sendMessage(topic_key, topic_key, last_trust_score)

        return 200

def launch_server_REST(port):
    api.add_resource(start_data_collection, '/start_data_collection')
    api.add_resource(gather_information, '/gather_information')
    api.add_resource(compute_trust_level, '/compute_trust_level')
    api.add_resource(store_trust_level, '/store_trust_level')
    api.add_resource(update_trust_level, '/update_trust_level')
    http_server = WSGIServer(('0.0.0.0', port), app)
    http_server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Usage: python3 trustManagementFramework.py [port]")
    else:
        port = int(sys.argv[1])
        launch_server_REST(port)