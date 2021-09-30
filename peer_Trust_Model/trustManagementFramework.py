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
import csv

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

dlt_headers = ["trustorDID","trusteeDID", "offerDID", "userSatisfaction","interactionNumber","totalInteractionNumber", "currentInteractionNumber"]
dlt_file_name = 'DLT.csv'

provider_list = []


def find_by_column(filename, column, value):
    list = []
    with open(filename) as f:
        reader = csv.DictReader(f)
        for item in reader:
            if item[column] == value:
                list.append(item)
    return list


def write_data_to_csv(filename, rows):
    with open(filename, 'a', encoding='UTF8', newline='') as dlt_data:
        writer = csv.DictWriter(dlt_data, fieldnames=dlt_headers)
        writer.writerows(rows)

def write_only_row_to_csv(filename, row):
    with open(filename, 'a', encoding='UTF8', newline='') as dlt_data:
        writer = csv.DictWriter(dlt_data, fieldnames=dlt_headers)
        writer.writerow(row)

class start_data_collection(Resource):
    """ This method is responsible for creating a kafka topic for each offer.
     After creating the Kafka Topics the gatherInformation method will be instantiated """
    def post(self):
        req = request.data.decode("utf-8")
        dict_product_offers = json.loads(req)

        """ Retrieve the Trustor DID """
        trustor_acquired = False
        trustorDID = ""

        if not os.path.exists(dlt_file_name):
            with open(dlt_file_name, 'w', encoding='UTF8', newline='') as dlt_data:
                writer = csv.DictWriter(dlt_data, fieldnames=dlt_headers)
                writer.writeheader()

            """ Adding a set of minimum interactions between entities that compose the trust model """
            minimum_data = peerTrust.minimumTrustValuesDLT(producer, dict_product_offers)
            write_data_to_csv(dlt_file_name, minimum_data)

        trust_scores = []

        for trustee in dict_product_offers:
            if trustor_acquired == False:
                trustorDID = next(iter(dict_product_offers.values()))
                #topic_trustorDID = trustorDID.split(":")[2]
                topic_trustorDID = trustorDID
                trustor_acquired = True
            else:
                for offer in dict_product_offers[trustee]:
                    """ Retrieve last part of DIDs to generate a unique kafka topic """
                    #topic_offerDID = offer.split(":")[2]
                    #topic_trusteeDID = trustee.split(":")[2]
                    topic_offerDID = offer
                    topic_trusteeDID = trustee

                    provider_list.append(trustee)

                    """ Generating kafka topic where all interactions with a trustee are registered """
                    registered_offer_interaction = topic_trusteeDID + "-" + topic_offerDID
                    producer.createTopic(topic_trusteeDID)
                    """ Generating kafka topic where all trustor's interactions with a trustee are registered """
                    provider_topic_name = topic_trustorDID+"-"+topic_trusteeDID
                    print("\nIf it does not exist, a Kafka topic will be generated to retrieve and register trust information between "+trustorDID+" and "+trustee)
                    print("\tKafka Topic name --->", provider_topic_name, "\n")
                    result = producer.createTopic(provider_topic_name)
                    """ Generating kafka topic where all trustor's interactions with a trustee and 
                    an particular offer are registered """
                    full_topic_name = topic_trustorDID+"-"+topic_trusteeDID+"-"+topic_offerDID
                    print("If it does not exist, a Kafka topic will be generated to retrieve and register trust information between "+trustorDID+" and a particular product offer ("+offer+")")
                    print("\tKafka Topic name --->", full_topic_name, "\n")
                    result = producer.createTopic(full_topic_name)

                    if result == 1:
                        """ we generated initial trust information to avoid the cold start"""
                        print("$$$$$$$$$$$$$$ Starting cold start procces on ",trustee, " $$$$$$$$$$$$$$\n")

                        #start_time_collection = time.time()
                        peerTrust.generateHistoryTrustInformation(producer, trustorDID, trustee, offer, provider_topic_name, full_topic_name, topic_trusteeDID,registered_offer_interaction,3)

                        """ Establish two new interactions per each provider"""
                        peerTrust.setTrusteeInteractions(producer, trustee, 2)

                        print("$$$$$$$$$$$$$$ Ending cold start procces on ",trustee, " $$$$$$$$$$$$$$\n")

                        """ Retrieve information from trustor and trustee """
                        data = {"trustorDID": trustorDID, "trusteeDID": trustee, "offerDID": offer, "topicName": full_topic_name}
                        #print("%s seconds during Cold Start process" % (time.time()-start_time_collection), "\n")
                        response = requests.post("http://localhost:5002/gather_information", data=json.dumps(data).encode("utf-8"))
                        response = json.loads(response.text)
                        trust_scores.append(response)
                    else:
                        logging.info("Error generating a Kafka topic")
        client.close()
        return json.dumps(trust_scores)


class gather_information(Resource):
    def post(self):
        """ This method will retrieve information from the DataLake (kafka topic direct trust) +
        search for supplier/offer interactions in the simulated DLT to retrieve recommendations from
        other kafka topics (indirect trust). Currently there is no interaction with DataLake, we generate our
        internal Kafka topics """

        """ Retrieve parameters from post request"""
        req = request.data.decode("utf-8")
        parameter = json.loads(req)

        counter_consumer_130 = 0

        trustorDID = parameter["trustorDID"]
        trusteeDID = parameter["trusteeDID"]
        offerDID = parameter["offerDID"]
        topic_name = parameter["topicName"]

        print("$$$$$$$$$$$$$$ Starting data collection procces on ",trusteeDID, " $$$$$$$$$$$$$$\n")
        #start_time_gather = time.time()

        """Read last value registered in Kafka"""
        last_trust_value = consumer.readLastTrustValue(topic_name)
        counter_consumer_130+=1

        print("\nThe latest trust interaction (history) of "+trustorDID+" with "+trusteeDID+" was:\n",last_trust_value, "\n")

        """Read interactions related to a Trustee"""
        interactions = self.getInteractionTrustee(trusteeDID)
        print("Public information from "+trusteeDID+" interactions registered in the DLT:\n", interactions, "\n")

        print("$$$$$$$$$$$$$$ Ending data collection procces on ",trusteeDID, " $$$$$$$$$$$$$$\n")
        #print("%s seconds during Gather Information process" % (time.time()-start_time_gather), "\n")

        """ Retrieve information from trustor and trustee """
        trust_information = []
        current_offer = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID, "topicName": topic_name, "lastValue": last_trust_value, "trusteeInteractions": interactions}
        trust_information.append(current_offer)

        response = requests.post("http://localhost:5002/compute_trust_level", data=json.dumps(trust_information).encode("utf-8"))

        response = json.loads(response.text)

        print("Total 130:", counter_consumer_130)

        return response

    def getInteractionTrustee(self, trusteeDID):
        """ This method retrieves all interactions related to a Trustee"""

        return find_by_column(dlt_file_name, "trustorDID", trusteeDID)

class compute_trust_level(Resource):
    def post(self):
        """This method retrieves the last value of the Trustor for a particular Trustee and the Trustee's interactions.
        It will then do the summation from its last computed value to the recent one by updating it trust value over
        the trustee """

        """ Retrieve parameters from post request"""
        req = request.data.decode("utf-8")
        parameter = json.loads(req)

        counter_consumer_130 = 0

        for i in parameter:

            print("$$$$$$$$$$$$$$ Starting trust computation procces on ",i['trusteeDID'], " $$$$$$$$$$$$$$\n")
            #start_time_compute = time.time()
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
            print("Checking if "+current_trustee+" has had new interactions from last time we interacted with it\n")
            print("The last time "+trustorDID+" interacted with "+current_trustee+", it had had "+str(last_trustee_interaction_registered)+" interactions in total\n")

            current_trustee_interactions = i['trusteeInteractions']

            new_satisfaction = 0.0
            new_credibility = 0.0
            new_transaction_factor = 0.0
            new_community_factor = 0.0
            counter_new_interactions = 0

            """Obtaining the last interaction registered by the Trustee in the DLT """
            last_interaction_DLT = current_trustee_interactions[len(current_trustee_interactions)-1]
            print("Currently, "+current_trustee+" has "+str(last_interaction_DLT['currentInteractionNumber'])+" interactions in total\n")

            if int(last_interaction_DLT['currentInteractionNumber']) > last_trustee_interaction_registered:
                print(int(last_interaction_DLT['currentInteractionNumber'])-last_trustee_interaction_registered, " new interactions should be contemplated to compute the new trust score on "+current_trustee+"\n")
                print("%%%%%%%%%%%%%% Principal PeerTrust equation %%%%%%%%%%%%%%\n")
                print("\tT(u) = α * ((∑ S(u,i) * Cr(p(u,i) * TF(u,i)) / I(u)) + β * CF(u)\n")

                for new_interaction in current_trustee_interactions:
                    #topic_name = current_trustee.split(":")[2]+"-"+new_interaction['trusteeDID'].split(":")[2]
                    topic_name = current_trustee+"-"+new_interaction['trusteeDID']
                    new_trustee_interaction = consumer.readLastTrustValues(topic_name, last_trustee_interaction_registered, new_interaction['currentInteractionNumber'])
                    counter_consumer_130+=1

                    for i in new_trustee_interaction:
                        print(new_interaction['trustorDID']," had an interaction with ", new_interaction['trusteeDID'],"\n")
                        print("\tS(u,i) ---> ", i['trusteeSatisfaction'])
                        new_satisfaction = new_satisfaction + i['trusteeSatisfaction']
                        current_credibility = peerTrust.credibility(current_trustee, new_interaction['trusteeDID'])
                        print("\tCr(p(u,i)) ---> ", round(current_credibility, 3))
                        new_credibility = new_credibility + current_credibility
                        current_transaction_factor = peerTrust.transactionContextFactor(current_trustee, new_interaction['trusteeDID'], new_interaction['offerDID'])
                        print("\tTF(u,i) ---> ", current_transaction_factor)
                        new_transaction_factor = new_transaction_factor + current_transaction_factor
                        current_community_factor = peerTrust.communityContextFactor2(current_trustee, new_interaction['trusteeDID'])
                        print("\tCF(u) ---> ", current_community_factor, "\n")
                        new_community_factor = new_community_factor + current_community_factor
                        counter_new_interactions += 1

                """ Updating the last value with the summation of new interactions"""
                new_satisfaction = round(((new_satisfaction/counter_new_interactions) + last_satisfaction)/2, 3)
                new_credibility = round(((new_credibility/counter_new_interactions) + last_credibility)/2, 3)
                new_transaction_factor = round(((new_transaction_factor/counter_new_interactions) + last_transaction_factor)/2, 3)
                new_community_factor = round(((new_community_factor/counter_new_interactions) + last_community_factor)/2, 3)

                trustInformationTemplate = TrustInformationTemplate()
                information = trustInformationTemplate.trustTemplate2()
                information["trustee"]["trusteeDID"] = current_trustee
                information["trustee"]["offerDID"] = offerDID
                information["trustee"]["trusteeSatisfaction"] = round(new_satisfaction, 3)
                information["trustor"]["trustorDID"] = trustorDID
                information["trustor"]["trusteeDID"] = current_trustee
                information["trustor"]["offerDID"] = offerDID
                information["trustor"]["credibility"] = round(new_credibility, 3)
                information["trustor"]["transactionFactor"] = round(new_transaction_factor, 3)
                information["trustor"]["communityFactor"] = round(new_community_factor, 3)
                #information["trustor"]["direct_parameters"]["userSatisfaction"] = round((round(random.uniform(0.75, 0.95), 3) + i["userSatisfaction"])/2, 3)
                direct_weighting = round(random.uniform(0.6, 0.7),2)
                information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
                information["trustor"]["indirect_parameters"]["recommendation_weighting"] = round(1-direct_weighting, 3)
                information["trustor"]["direct_parameters"]["interactionNumber"] = last_interaction_number+1
                information["trustor"]["direct_parameters"]["totalInteractionNumber"] = peerTrust.getLastTotalInteractionNumber(current_trustee)
                information["trustor"]["direct_parameters"]["feedbackNumber"] = peerTrust.getTrusteeFeedbackNumberDLT(current_trustee)
                information["trustor"]["direct_parameters"]["feedbackOfferNumber"] = peerTrust.getOfferFeedbackNumberDLT(current_trustee, offerDID)
                information["trust_value"] = round(direct_weighting*(new_satisfaction*new_credibility*new_transaction_factor)+(1-direct_weighting)*new_community_factor,3)
                information["currentInteractionNumber"] = peerTrust.getCurrentInteractionNumber(trustorDID)
                information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
                information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

                """ These values should be requested from other 5GZORRO components in future releases"""
                if provider_list[0] in current_trustee:
                    provider_reputation = peerTrust.providerReputation(3, 5, 3, 3, 22, 24, 1, 1)
                    information["trustor"]["direct_parameters"]["availableAssets"] = 3
                    information["trustor"]["direct_parameters"]["totalAssets"] = 5
                    information["trustor"]["direct_parameters"]["availableAssetLocation"] = 3
                    information["trustor"]["direct_parameters"]["totalAssetLocation"] = 3
                    information["trustor"]["direct_parameters"]["managedViolations"] = 22
                    information["trustor"]["direct_parameters"]["predictedViolations"] = 24
                    information["trustor"]["direct_parameters"]["executedViolations"] = 1
                    information["trustor"]["direct_parameters"]["nonPredictedViolations"] = 1
                    offer_reputation = peerTrust.offerReputation(5, 6, 2, 4, 7, 8, 1, 0)
                    information["trustor"]["direct_parameters"]["consideredOffers"] = 5
                    information["trustor"]["direct_parameters"]["totalOffers"] = 6
                    information["trustor"]["direct_parameters"]["consideredOfferLocation"] = 2
                    information["trustor"]["direct_parameters"]["totalOfferLocation"] = 4
                    information["trustor"]["direct_parameters"]["managedOfferViolations"] = 7
                    information["trustor"]["direct_parameters"]["predictedOfferViolations"] = 8
                    information["trustor"]["direct_parameters"]["executedOfferViolations"] = 1
                    information["trustor"]["direct_parameters"]["nonPredictedOfferViolations"] = 0
                elif provider_list[1] in current_trustee:
                    provider_reputation = peerTrust.providerReputation(2, 4, 1, 1, 10, 14, 1, 2)
                    information["trustor"]["direct_parameters"]["availableAssets"] = 2
                    information["trustor"]["direct_parameters"]["totalAssets"] = 4
                    information["trustor"]["direct_parameters"]["availableAssetLocation"] = 1
                    information["trustor"]["direct_parameters"]["totalAssetLocation"] = 1
                    information["trustor"]["direct_parameters"]["managedViolations"] = 10
                    information["trustor"]["direct_parameters"]["predictedViolations"] = 14
                    information["trustor"]["direct_parameters"]["executedViolations"] = 2
                    information["trustor"]["direct_parameters"]["nonPredictedViolations"] = 2
                    offer_reputation = peerTrust.offerReputation(2, 5, 1, 1, 5, 5, 0, 0)
                    information["trustor"]["direct_parameters"]["consideredOffers"] = 2
                    information["trustor"]["direct_parameters"]["totalOffers"] = 5
                    information["trustor"]["direct_parameters"]["consideredOfferLocation"] = 1
                    information["trustor"]["direct_parameters"]["totalOfferLocation"] = 1
                    information["trustor"]["direct_parameters"]["managedOfferViolations"] = 5
                    information["trustor"]["direct_parameters"]["predictedOfferViolations"] = 5
                    information["trustor"]["direct_parameters"]["executedOfferViolations"] = 0
                    information["trustor"]["direct_parameters"]["nonPredictedOfferViolations"] = 0
                elif provider_list[2] in current_trustee:
                    provider_reputation = peerTrust.providerReputation(4, 4, 2, 2, 10, 18, 6, 2)
                    information["trustor"]["direct_parameters"]["availableAssets"] = 4
                    information["trustor"]["direct_parameters"]["totalAssets"] = 4
                    information["trustor"]["direct_parameters"]["availableAssetLocation"] = 2
                    information["trustor"]["direct_parameters"]["totalAssetLocation"] = 2
                    information["trustor"]["direct_parameters"]["managedViolations"] = 10
                    information["trustor"]["direct_parameters"]["predictedViolations"] = 18
                    information["trustor"]["direct_parameters"]["executedViolations"] = 6
                    information["trustor"]["direct_parameters"]["nonPredictedViolations"] = 2
                    offer_reputation = peerTrust.offerReputation(7, 8, 3, 4, 4, 8, 4, 4)
                    information["trustor"]["direct_parameters"]["consideredOffers"] = 7
                    information["trustor"]["direct_parameters"]["totalOffers"] = 8
                    information["trustor"]["direct_parameters"]["consideredOfferLocation"] = 3
                    information["trustor"]["direct_parameters"]["totalOfferLocation"] = 4
                    information["trustor"]["direct_parameters"]["managedOfferViolations"] = 4
                    information["trustor"]["direct_parameters"]["predictedOfferViolations"] = 8
                    information["trustor"]["direct_parameters"]["executedOfferViolations"] = 4
                    information["trustor"]["direct_parameters"]["nonPredictedOfferViolations"] = 4
                elif provider_list[3] in current_trustee:
                    provider_reputation = peerTrust.providerReputation(6, 8, 4, 5, 19, 19, 0, 0)
                    information["trustor"]["direct_parameters"]["availableAssets"] = 6
                    information["trustor"]["direct_parameters"]["totalAssets"] = 8
                    information["trustor"]["direct_parameters"]["availableAssetLocation"] = 4
                    information["trustor"]["direct_parameters"]["totalAssetLocation"] = 5
                    information["trustor"]["direct_parameters"]["managedViolations"] = 19
                    information["trustor"]["direct_parameters"]["predictedViolations"] = 19
                    information["trustor"]["direct_parameters"]["executedViolations"] = 0
                    information["trustor"]["direct_parameters"]["nonPredictedViolations"] = 0
                    offer_reputation = peerTrust.offerReputation(3, 4, 1, 1, 4, 6, 1, 1)
                    information["trustor"]["direct_parameters"]["consideredOffers"] = 3
                    information["trustor"]["direct_parameters"]["totalOffers"] = 4
                    information["trustor"]["direct_parameters"]["consideredOfferLocation"] = 1
                    information["trustor"]["direct_parameters"]["totalOfferLocation"] = 1
                    information["trustor"]["direct_parameters"]["managedOfferViolations"] = 4
                    information["trustor"]["direct_parameters"]["predictedOfferViolations"] = 6
                    information["trustor"]["direct_parameters"]["executedOfferViolations"] = 1
                    information["trustor"]["direct_parameters"]["nonPredictedOfferViolations"] = 1

                provider_satisfaction = peerTrust.providerSatisfaction(trustorDID, current_trustee, provider_reputation)
                offer_satisfaction = peerTrust.offerSatisfaction(trustorDID, current_trustee, offerDID, offer_reputation)
                ps_weighting = round(random.uniform(0.4, 0.6),2)
                information["trustor"]["direct_parameters"]["providerSatisfaction"] = round(provider_satisfaction, 3)
                ps_weighting = round(random.uniform(0.4, 0.6),2)
                information["trustor"]["direct_parameters"]["PSWeighting"] = ps_weighting
                information["trustor"]["direct_parameters"]["offerSatisfaction"] = round(offer_satisfaction, 3)
                os_weighting = 1-ps_weighting
                information["trustor"]["direct_parameters"]["OSWeighting"] = os_weighting
                information["trustor"]["direct_parameters"]["providerReputation"] = round(provider_reputation, 3)
                information["trustor"]["direct_parameters"]["offerReputation"] = round(offer_reputation, 3)
                information["trustor"]["direct_parameters"]["userSatisfaction"] = round(peerTrust.satisfaction(ps_weighting, os_weighting, provider_satisfaction, offer_satisfaction), 3)

                response = {"trustorDID": trustorDID, "trusteeDID": {"trusteeDID": current_trustee, "offerDID": offerDID}, "trust_value": information["trust_value"], "currentInteractionNumber": information["currentInteractionNumber"],"evaluation_criteria": "Inter-domain", "initEvaluationPeriod": information["initEvaluationPeriod"],"endEvaluationPeriod": information["endEvaluationPeriod"]}

                print("\nNew Trust values after considering new interactions of "+current_trustee+":")
                print("\tα ---> ", direct_weighting)
                print("\tS(u,i) ---> ", new_satisfaction)
                print("\tCr(p(u,i)) ---> ", new_credibility)
                print("\tTF(u,i) ---> ", new_transaction_factor)
                print("\tβ ---> ", round(1-direct_weighting, 3))
                print("\tCF(u) ---> ", new_community_factor)

                print("\nPrevious Trust score of "+trustorDID+" on "+current_trustee+" --->", last_trust_value, " -- New trust score --->", information["trust_value"])

                #registered_offer_interaction = current_trustee.split(":")[2] + "-" + offerDID.split(":")[2]
                registered_offer_interaction = current_trustee + "-" + offerDID
                producer.createTopic(registered_offer_interaction)
                #provider_topic_name = trustorDID.split(":")[2]+"-"+current_trustee.split(":")[2]
                provider_topic_name = trustorDID+"-"+current_trustee
                producer.createTopic(provider_topic_name)
                #full_topic_name = trustorDID.split(":")[2]+"-"+current_trustee.split(":")[2]+"-"+offerDID.split(":")[2]
                full_topic_name = trustorDID+"-"+current_trustee+"-"+offerDID
                producer.createTopic(full_topic_name)

                message = {"interaction": trustorDID+" has interacted with "+current_trustee}
                #producer.sendMessage(current_trustee.split(":")[2], registered_offer_interaction, message)
                producer.sendMessage(current_trustee, registered_offer_interaction, message)
                producer.sendMessage(provider_topic_name, provider_topic_name, information)
                producer.sendMessage(full_topic_name, full_topic_name, information)


                data = {"trustorDID": trustorDID, "trusteeDID": current_trustee, "offerDID": offerDID,
                        "userSatisfaction": information["trustor"]["direct_parameters"]["userSatisfaction"],
                        "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                        "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                        "currentInteractionNumber": information["currentInteractionNumber"]}

                write_only_row_to_csv(dlt_file_name, data)

                print("\n$$$$$$$$$$$$$$ Ending trust computation procces on ",i['trusteeDID'], " $$$$$$$$$$$$$$\n")
                #print("%s seconds during the Trust Computation Process" % (time.time()-start_time_compute), "\n")
                requests.post("http://localhost:5002/store_trust_level", data=json.dumps(information).encode("utf-8"))

        print("Total 130:", counter_consumer_130)

        return response

class store_trust_level(Resource):
    def post(self):
        """ This method is employed to register direct trust in our internal database """
        req = request.data.decode("utf-8")
        information = json.loads(req)

        print("$$$$$$$$$$$$$$ Starting trust information storage process $$$$$$$$$$$$$$\n")
        #start_time_store = time.time()
        print("Registering a new trust interaction between two domains in the DLT\n")
        data = "{\"trustorDID\": \""+information["trustor"]["trustorDID"]+"\", \"trusteeDID\": \""+information["trustee"]["trusteeDID"]+"\", \"offerDID\": \""+information["trustee"]["offerDID"]+"\",\"userSatisfaction\": "+str(information["trustor"]["direct_parameters"]["userSatisfaction"])+", \"interactionNumber\": "+str(information["trustor"]["direct_parameters"]["interactionNumber"])+", \"totalInteractionNumber\": "+str(information["trustor"]["direct_parameters"]["totalInteractionNumber"])+", \"currentInteractionNumber\": "+str(information["currentInteractionNumber"])+"}\""
        print(data,"\n")
        print("Sending new trust information in the Kafka topic generated by the Trust Management Framework \n")
        print(information)
        print("\nStoring new trust information in our internal MongoDB database\n")

        print("\n$$$$$$$$$$$$$$ Ending trust information storage process $$$$$$$$$$$$$$\n")
        #print("%s seconds during the Store Process " % (time.time()-start_time_store), "\n")
        mongoDB.insert_one(information)
        #pprint.pprint(mongoDB.find_one({"trustorDID": trustorDID}))
        #mongoDB.insert_many([tutorial2, tutorial1])
        #for doc in mongoDB.find():
        #pprint.pprint(doc)

        print("Total Peer 130:", peerTrust.counter_consumer_130," Total 170: ", peerTrust.counter_consumer_170, " Total 350: ", peerTrust.counter_consumer_350)

        return 200

class update_trust_level(Resource):
    def post(self):
        """ This method updates a trust score based on certain SLA events. More events need to be considered,
        it is only an initial version"""

        req = request.data.decode("utf-8")
        information = json.loads(req)

        print("\n$$$$$$$$$$$$$$ Starting update trust level process process $$$$$$$$$$$$$$\n")

        slaBreachPredictor_topic = information["SLABreachPredictor"]
        topic_key = information["key"]

        notifications = consumer.readSLANotification(slaBreachPredictor_topic, topic_key)

        positive_notification = "was able to manage the SLA violation successfully"
        negative_notification = "was not able to manage the SLA violation successfully"
        first_range_probability = 0.25
        second_range_probability = 0.50
        third_range_probability = 0.75
        fourth_range_probability = 1.0

        new_trust_score = 0.0

        for notification in notifications:
            print("Notification received from the SLA Breach Predictor about", notification["breachPredictionNotification"],":\n")

            current_notification = notification["notification"]
            print("\t-", current_notification,"\n")
            likehood = notification["breachPredictionNotification"]["value"]
            #likehood = float(likehood)

            last_trust_score = consumer.readAllInformationTrustValue(topic_key)
            counter_consumer_130+=1

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
                    new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.10
                elif likehood <= second_range_probability:
                    new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.125
                elif likehood <= third_range_probability:
                    new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.15
                elif likehood <= fourth_range_probability:
                    new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.175

            if new_trust_score > 1.0:
                new_trust_score = 1.0
            elif new_trust_score < 0.0:
                new_trust_score = 0.0

            print("\t\tPrevious Trust Score", last_trust_score ["trust_value"], " --- Updated Trust Score --->", round(new_trust_score, 3), "\n")
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