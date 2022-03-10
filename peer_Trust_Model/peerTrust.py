import json
import sys
import logging
import random
import time
import ast
import math
import os.path
import csv
import rstr
import copy
import requests


#from producer import *
from trustInformationTemplate import *
from consumer import *
from datetime import datetime
from random import randint
from dotenv import load_dotenv

from multiprocessing import Process, Value, Manager
from threading import Lock

#logging.basicConfig(level=logging.INFO)

""" This file contains all methods necessary to obtain the minimum information required by the peerTrust model """
class PeerTrust():

    dlt_file_name = 'DLT.csv'
    dlt_headers = ["trustorDID","trusteeDID", "offerDID", "userSatisfaction", "interactionNumber",
                   "totalInteractionNumber", "currentInteractionNumber"]

    """ Creating additional domains to generate previous interactions and avoid a cold start """
    list_additional_did_providers = []
    list_additional_did_offers = []
    recommender_list = []
    kafka_interaction_list = []

    """ Parameters to define a minimum interactions in the system and avoid a cold start"""
    max_previous_providers_DLT = 4
    max_previous_providers_interactions_DLT = 3
    max_previous_interactions_DLT = max_previous_providers_DLT * max_previous_providers_interactions_DLT
    max_different_interactions = max_previous_providers_DLT * 2

    historical = []
    consumer = None

    def find_by_column(self, column, value):
        """ This method discovers interactions registered in the DLT looking at one specific value"""

        list_object = []
        """with open(filename) as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item[column] == value:
                    list_object.append(item)"""
        for interaction in self.kafka_interaction_list:
            if interaction[column] == value:
                list_object.append(interaction)

        return list(list_object)

    def find_by_two_column(self, filename, column1, value1, colum2, value2):
        """ This method discovers interactions registered in the DLT looking at two specific values"""

        list_object = []
        """with open(filename) as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item[column1] == value1 and item[colum2] == value2:
                    list_object.append(item)"""
        for interaction in self.kafka_interaction_list:
            if interaction[column1] == value1 and interaction[colum2] == value2:
                list_object.append(interaction)

        return list(list_object)

    def minimumTrustTemplate(self, trustorDID, trusteeDID, offerDID):
        """ This method initialises a set of minimum trust parameters to ensure that the system does not start from
         scratch as well as defining a common trust template which will then be updated """

        trustInformationTemplate = TrustInformationTemplate()
        information = trustInformationTemplate.trustTemplate()

        """ Adding information related to the specific request """
        information["trustee"]["trusteeDID"] = trusteeDID
        information["trustee"]["offerDID"] = offerDID
        #information["trustee"]["trusteeSatisfaction"] = self.getTrusteeSatisfactionDLT(trusteeDID)
        information["trustee"]["trusteeSatisfaction"] = round(random.uniform(0.8, 0.95),4)
        information["trustor"]["trustorDID"] = trustorDID
        information["trustor"]["trusteeDID"] = trusteeDID
        information["trustor"]["offerDID"] = offerDID
        information["trustor"]["credibility"] = round(random.uniform(0.75, 0.9),4)
        information["trustor"]["transactionFactor"] = round(random.uniform(0.8, 0.9),4)
        information["trustor"]["communityFactor"] = round(random.uniform(0.85, 0.9),4)
        information["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.5, 0.7),4)
        direct_weighting = round(random.uniform(0.6, 0.7),2)
        information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
        information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting
        information["trustor"]["direct_parameters"]["interactionNumber"] = self.getInteractionNumber(trustorDID, trusteeDID, offerDID)
        information["trustor"]["direct_parameters"]["totalInteractionNumber"] = self.getLastTotalInteractionNumber(trusteeDID)
        information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],4)
        information["currentInteractionNumber"] = self.getCurrentInteractionNumber(trustorDID)
        information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
        information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

        return information

    def minimumTrustValuesDLT(self, producer, consumer_instance, trustor, dict_product_offers):
        """ This method establishes multiple trust relationships from list of product offers to start the trust
         model with a set of minimum relationships. In addition, it also simulates the registration of such interactions
         in the DLT """

        global consumer

        self.consumer = consumer_instance

        load_dotenv()
        trmf_endpoint = os.getenv('TRMF_C_5GBARCELONA')

        print("\n\nSet of previous trust interactions between 5GZORRO domains\n")
        data = []

        """ 4 extra domains are currently considered"""
        for i in range(4):
            self.list_additional_did_providers.append(rstr.xeger("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"))
            additional_did_offers = []
            additional_did_offers.append(rstr.xeger("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"))
            additional_did_offers.append(rstr.xeger("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"))
            self.list_additional_did_offers.append(additional_did_offers)

        aux_did_providers = self.list_additional_did_providers[:]
        aux_did_offers = copy.deepcopy(self.list_additional_did_offers)

        """ Generating two interactions per provider, one per each offer"""
        counter = 0

        for i in range(self.max_previous_providers_DLT):
            providers = list(range(0,self.max_previous_providers_DLT))
            providers.remove(i)

            current_additional_provider = random.choice(providers)
            current_additional_offer = randint(0,1)

            for j in range (self.max_previous_providers_interactions_DLT):

                interaction = False
                new_trustee = None
                new_offer = None

                while (interaction == False):

                    if "$" not in aux_did_providers[current_additional_provider] and \
                            self.list_additional_did_providers[i] != aux_did_providers[current_additional_provider]:
                        if "$" not in aux_did_offers[current_additional_provider][current_additional_offer]:
                            new_trustee = aux_did_providers[current_additional_provider]
                            new_offer = aux_did_offers[current_additional_provider][current_additional_offer]
                            counter+=1
                            interaction = True
                            aux_did_offers[current_additional_provider][current_additional_offer] = \
                                aux_did_offers[current_additional_provider][current_additional_offer] + "$"
                        else:
                            current_additional_offer = (current_additional_offer+1)\
                                                       %len(aux_did_offers[current_additional_provider])
                            if "$" not in aux_did_offers[current_additional_provider][current_additional_offer] and \
                                    self.list_additional_did_providers[i] != aux_did_providers[current_additional_provider]:
                                new_trustee = aux_did_providers[current_additional_provider]
                                new_offer = aux_did_offers[current_additional_provider][current_additional_offer]
                                counter+=1
                                interaction = True
                                aux_did_offers[current_additional_provider][current_additional_offer] = \
                                    aux_did_offers[current_additional_provider][current_additional_offer] + "$"
                            else:
                                aux_did_providers[current_additional_provider] = \
                                    aux_did_providers[current_additional_provider] + "$"
                                current_additional_provider = (current_additional_provider+1)%len(aux_did_providers)
                    else:
                        current_additional_provider = (current_additional_provider+1)%len(aux_did_providers)
                        if counter >= self.max_different_interactions-1 and \
                                self.list_additional_did_providers[i] != self.list_additional_did_providers[current_additional_provider]:
                            new_trustee = aux_did_providers[current_additional_provider]
                            new_offer = aux_did_offers[current_additional_provider][current_additional_offer]
                            if "$" in new_trustee:
                                new_trustee = self.list_additional_did_providers[current_additional_provider]
                            else:
                                aux_did_providers[current_additional_provider] = aux_did_providers[current_additional_provider] + "$"

                            if "$" in new_offer:
                                new_offer = self.list_additional_did_offers[current_additional_provider][current_additional_offer]
                            else:
                                aux_did_offers[current_additional_provider][current_additional_offer] = \
                                    aux_did_offers[current_additional_provider][current_additional_offer] + "$"
                            counter+=1
                            interaction = True


                """new_interaction = {"trustorDID": self.list_additional_did_providers[i], "trusteeDID":  new_trustee,
                                   "offerDID": new_offer, "userSatisfaction": round(random.uniform(0.50, 0.75), 4),
                                   "interactionNumber": 1, "totalInteractionNumber": 6, "currentInteractionNumber": 8}"""
                new_interaction = {"trustorDID": self.list_additional_did_providers[i], "trusteeDID": new_trustee, "offerDID": new_offer,
                           "interactionNumber": 1, "totalInteractionNumber": 2, "currentInteractionNumber": 3,
                           "timestamp": datetime.timestamp(datetime.now()), "endpoint":trmf_endpoint}

                """ Adjusting the parameters based on previous interactions """
                for interaction in data:
                    if interaction["trustorDID"] == new_interaction["trustorDID"]:
                        new_interaction["currentInteractionNumber"] = interaction["currentInteractionNumber"] + 1
                    if interaction["trustorDID"] == new_interaction["trustorDID"] and interaction["trusteeDID"] == new_interaction["trusteeDID"] and interaction["offerDID"] == new_interaction["offerDID"]:
                        new_interaction["interactionNumber"] == interaction["interactionNumber"] + 1
                    if interaction["trustorDID"] == new_interaction["trusteeDID"]:
                        new_interaction["currentInteractionNumber"] = interaction["totalInteractionNumber"] + 1
                    if interaction["trusteeDID"] == new_interaction["trustorDID"]:
                        new_interaction["totalInteractionNumber"] = interaction["currentInteractionNumber"]
                    if interaction["trusteeDID"] == new_interaction["trusteeDID"]:
                        new_interaction["totalInteractionNumber"] = interaction["totalInteractionNumber"]
                data.append(new_interaction)

        """ Adding new interactions with respect to the product offers sent by the SRSD request"""
        aux_new_interactions = []
        trustor_acquired = False

        for trustee in dict_product_offers:
            """ Ignore the first item related to the trustor DID """
            if trustor_acquired == False:
                next(iter(dict_product_offers.values()))
                trustor_acquired = True
            else:
                for offer in dict_product_offers[trustee]:
                    """new_interaction = {"trustorDID": "did:5gzorro:domain-Z", "trusteeDID":  trustee, "offerDID": offer,
                                       "userSatisfaction": round(random.uniform(0.5, 0.7), 4), "interactionNumber": 1, "totalInteractionNumber": 6, "currentInteractionNumber": 8}"""
                    new_interaction = {"trustorDID": "did:5gzorro:domain-Z", "trusteeDID": trustee, "offerDID": offer,
                               "interactionNumber": 1, "totalInteractionNumber": 2, "currentInteractionNumber": 3,
                               "timestamp": datetime.timestamp(datetime.now()), "endpoint":trmf_endpoint}
                    aux_new_interactions.append(new_interaction)

        """ Adjusting the parameters based on previous interactions"""
        for i in range(len(aux_new_interactions)):
            index = i%len(self.list_additional_did_providers)
            aux_new_interactions[i]["trustorDID"] = self.list_additional_did_providers[index]
            for interaction in data:
                if interaction["trustorDID"] == aux_new_interactions[i]["trustorDID"]:
                    aux_new_interactions[i]["currentInteractionNumber"] = interaction["currentInteractionNumber"] + 1
                if interaction["trustorDID"] == aux_new_interactions[i]["trustorDID"] and interaction["trusteeDID"] == aux_new_interactions[i]["trusteeDID"] and interaction["offerDID"] == aux_new_interactions[i]["offerDID"]:
                    aux_new_interactions[i]["interactionNumber"] == interaction["interactionNumber"] + 1
                if interaction["trustorDID"] == aux_new_interactions[i]["trusteeDID"]:
                    aux_new_interactions[i]["currentInteractionNumber"] = interaction["totalInteractionNumber"] + 1
                if interaction["trusteeDID"] == aux_new_interactions[i]["trustorDID"]:
                    aux_new_interactions[i]["totalInteractionNumber"] = interaction["currentInteractionNumber"]
                if interaction["trusteeDID"] == aux_new_interactions[i]["trusteeDID"]:
                    aux_new_interactions[i]["totalInteractionNumber"] = interaction["totalInteractionNumber"]
            data.append(aux_new_interactions[i])

        print(data, "\n")

        interactions = []
        "If DLT.csv file doesn't exist, we add new interactions related to the POs and minimum interactions between providers"
        #if not os.path.exists(self.dlt_file_name):
        if not bool(self.kafka_interaction_list):
            #if not os.path.exists(self.dlt_file_name):
                #with open(self.dlt_file_name, 'w', encoding='UTF8', newline='') as dlt_data:
                    #writer = csv.DictWriter(dlt_data, fieldnames=self.dlt_headers)
                    #writer.writeheader()

            for interaction in data:
                trust_informartion = self.minimumTrustTemplate(interaction["trustorDID"], interaction["trusteeDID"], interaction["offerDID"])
                trust_informartion["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.5, 0.75), 4)
                trust_informartion["trustor"]["direct_parameters"]["interactionNumber"] = interaction["interactionNumber"]
                trust_informartion["trustor"]["direct_parameters"]["totalInteractionNumber"] = interaction["totalInteractionNumber"]
                trust_informartion["currentInteractionNumber"] = interaction["currentInteractionNumber"]

                """ Adding the recommender list so as to have an initial set"""
                recommender_list = self.setRecommenderList(trust_informartion["trustor"]["trustorDID"], trust_informartion["trustor"]["trusteeDID"])
                if len(recommender_list)>0:
                    trust_informartion["trustor"]["indirect_parameters"]["recommendations"] = recommender_list

                """ The minimum interactions are also registered in the Trustor's historical but 
                they must be deleted when cold start is not used """
                interactions.append(trust_informartion)

            for i in interactions:
                self.historical.append(i)

            self.kafka_interaction_list = copy.deepcopy(data)
            return data
        else:
            "We only add new interactions related to the POs"
            for interaction in aux_new_interactions:
                trust_informartion = self.minimumTrustTemplate(interaction["trustorDID"], interaction["trusteeDID"], interaction["offerDID"])
                trust_informartion["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.5, 0.75), 4)
                trust_informartion["trustor"]["direct_parameters"]["interactionNumber"] = interaction["interactionNumber"]
                trust_informartion["trustor"]["direct_parameters"]["totalInteractionNumber"] = interaction["totalInteractionNumber"]
                trust_informartion["currentInteractionNumber"] = interaction["currentInteractionNumber"]

                """ Adding the recommender list so as to have an initial set"""
                recommender_list = self.setRecommenderList(trust_informartion["trustor"]["trustorDID"], trust_informartion["trustor"]["trusteeDID"])
                if len(recommender_list) > 0:
                    trust_informartion["trustor"]["indirect_parameters"]["recommendations"] = recommender_list

                """ The minimum interactions are also registered in the Trustor's historical but 
                they must be deleted when cold start is not used """
                interactions.append(trust_informartion)
                """ Adding new interaction to Kafka copy list"""
                self.kafka_interaction_list.append(interaction)

            for i in interactions:
                self.historical.append(i)

            return aux_new_interactions

        #return data

    def setRecommenderList(self, trustorDID, trusteeDID):
        """ Adding the recommender list so as to have an initial set"""
        recommender_list = []
        for aditional_provider in self.list_additional_did_providers:
            if aditional_provider != trustorDID and aditional_provider != trusteeDID:
                trust_value = self.getLastHistoryTrustValue(trustorDID, trusteeDID)
                last_trust_value = self.getLastHistoryTrustValue(aditional_provider, trusteeDID)
                previous_recommendations = self.consumer.readAllRecommenders(self.historical, trustorDID, trusteeDID)
                if last_trust_value != 0 and trust_value!= 0:
                    "1 means there is not an interaction between recommender and trusteeDID"
                    if bool(previous_recommendations):
                        return previous_recommendations
                    else:
                        recommender_list.append({"recommender": aditional_provider,"trust_value": trust_value,
                                             "recommendation_trust": 0.5, "recommendation_total_number": 1,
                                             "average_recommendations": last_trust_value, "last_recommendation": last_trust_value})
        return recommender_list


    def stringToDictionaryList(self):
        """Convert string to a list of dictionaries"""
        new_interaction_list = []

        with open('DLT.json', 'r') as file:
            file.seek(0)
            interaction_list = file.read()

            interaction_list = interaction_list.split("\\n")
            for interaction in interaction_list:
                interaction = interaction.replace("\\\"","\"")
                interaction = interaction.replace("\"{", "{")
                interaction = interaction.replace("}\"", "}")
                new_interaction_list.append(ast.literal_eval(interaction))

        file.close()
        return new_interaction_list

    def getLastTotalInteractionNumber(self, trusteeDID):
        """ Retrieve the last interactions number registered in the DLT for a Trustee"""

        #last_total_iteraction_number = 1
        last_total_iteraction_number = 0

        """with open(self.dlt_file_name) as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item["trustorDID"] == trusteeDID and int(item["currentInteractionNumber"]) > last_total_iteraction_number:
                    last_total_iteraction_number = int(item["currentInteractionNumber"])
                elif item["trusteeDID"] == trusteeDID and int(item["totalInteractionNumber"]) > last_total_iteraction_number:
                    last_total_iteraction_number = int(item["totalInteractionNumber"])"""

        for interaction in self.kafka_interaction_list:
            if interaction["trustorDID"] == trusteeDID and int(interaction["currentInteractionNumber"]) > last_total_iteraction_number:
                last_total_iteraction_number = int(interaction["currentInteractionNumber"])
            if interaction["trusteeDID"] == trusteeDID and int(interaction["totalInteractionNumber"]) > last_total_iteraction_number:
                last_total_iteraction_number = int(interaction["totalInteractionNumber"])

        return last_total_iteraction_number

    def getCurrentInteractionNumber(self, trustorDID):
        """ This method returns the next interaction number for a trustor """

        current_iteraction_number = 0

        """with open(self.dlt_file_name) as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item["trustorDID"] == trustorDID and int(item["currentInteractionNumber"]) > current_iteraction_number:
                    current_iteraction_number = int(item["currentInteractionNumber"])
                elif item["trusteeDID"] == trustorDID and int(item["totalInteractionNumber"]) > current_iteraction_number:
                    current_iteraction_number = int(item["totalInteractionNumber"])"""

        for interaction in self.kafka_interaction_list:
            if interaction["trustorDID"] == trustorDID and int(interaction["currentInteractionNumber"]) > current_iteraction_number:
                current_iteraction_number = int(interaction["currentInteractionNumber"])
            if interaction["trusteeDID"] == trustorDID and int(interaction["totalInteractionNumber"]) > current_iteraction_number:
                current_iteraction_number = int(interaction["totalInteractionNumber"])

        return current_iteraction_number+1

    def getInteractionNumber(self, trustorDID, trusteeDID, offerDID):
        """ This method retrieves the number of interactions between two entities and adds one more interaction """
        iteraction_number = 0

        list_interactions = self.find_by_column('trustorDID', trustorDID)
        for interaction in list_interactions:
            if interaction["trusteeDID"] == trusteeDID and interaction["offerDID"] == offerDID and int(interaction["interactionNumber"]) > iteraction_number:
                iteraction_number = int(interaction["interactionNumber"])

        return iteraction_number+1


    def getRecommenderDLT(self, trustorDID, trusteeDID):
        """ This method recovers a recommender, who is reliable for us, that has recently interacted with a trustee.
        Return the last interaction in order to request the last trust value. In this case, reliable means
        other trustees with whom we have previously interacted with """

        last_interaction = {}

        last_registered_interaction = True

        #with open(self.dlt_file_name) as f:
            #reader = csv.DictReader(f)
        """ Starting from the end to identify the last recommender"""
        for interaction in reversed(self.kafka_interaction_list):
            """ Check that the last recommender is not ourselves"""
            if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID:
                """ Store the most recent interaction with the Trustee to return it in the case of no trustworthy 
                recommenders can be found"""
                if last_registered_interaction:
                    last_interaction = interaction
                    last_registered_interaction = False
                """Check if the Trustor is reliable for us"""
                for trustworthy_candidate in reversed(self.kafka_interaction_list):
                    if trustworthy_candidate['trustorDID'] == trustorDID and trustworthy_candidate['trusteeDID'] == interaction['trustorDID']:
                        return dict(interaction)
        return dict(last_interaction)

    def getRecommenderOfferDLT(self, trustorDID, trusteeDID, offerDID):
        """ This method recovers an offer associated with a recommender, who is reliable for us, that has recently
        interacted with a trustee. Return the last interaction in order to request the last trust value.
        In this case, reliable means other trustees with whom we have previously interacted with"""

        last_interaction = {}

        last_registered_interaction = True

        #with open(self.dlt_file_name) as f:
            #reader = csv.DictReader(f)
        """ Starting from the end to identify the last recommender"""
        for interaction in reversed(self.kafka_interaction_list):
            """ Check that the last recommender is not ourselves"""
            if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID and interaction['offerDID'] == offerDID:
                """ Store the most recent interaction with the Trustee """
                if last_registered_interaction:
                    last_interaction = interaction
                    last_registered_interaction = False
                """ Check if the Trustor is reliable for us """
                for trustworthy_candidate in reversed(self.kafka_interaction_list):
                    if trustworthy_candidate['trustorDID'] == trustorDID and trustworthy_candidate['trusteeDID'] == interaction['trustorDID'] and trustworthy_candidate['offerDID'] == offerDID:
                        return dict(interaction)

        return dict(last_interaction)

    def getLastRecommendationValue(self, last_interaction):
        """ This methods goes to a recommender kafka channel to request a trust score """
        global consumer
        last_truste_value = 0.0

        trustor = last_interaction['trustorDID']
        trustee = last_interaction['trusteeDID']

        trust_information = self.consumer.readLastTrustValue(self.historical, trustor, trustee)
        last_truste_value = trust_information["trust_value"]

        return last_truste_value

    def getLastOfferRecommendationValue(self, last_interaction):
        """ This methods goes to an offer recommender kafka channel to request a trust score """
        global consumer
        last_truste_value = 0.0

        trustor = last_interaction['trustorDID']
        trustee = last_interaction['trusteeDID']
        offer = last_interaction['offerDID']

        trust_information = self.consumer.readLastTrustValueOffer(self.historical, trustor, trustee, offer)
        last_truste_value = trust_information["trust_value"]

        return last_truste_value

    def getTrusteeSatisfactionDLT(self, trusteeDID):
        """ This method collects the userSatisfaction from the DLT when a trustor contemplates a feedback. However,
        this information should be deleted from the DLT and requested directly to other 5G-TRMFs """

        counter = 0
        general_satisfaction = 0.0

        #last_interaction = self.find_by_column(self.dlt_file_name, 'trustorDID', trusteeDID)
        last_interaction = self.find_by_column('trustorDID', trusteeDID)
        for interaction in last_interaction:
            endpoint = interaction["endpoint"].split("/")[2]
            data = {"trustorDID": interaction["trustorDID"], "trusteeDID": interaction["trusteeDID"], "offerDID": interaction["offerDID"]}
            response = requests.post("http://"+endpoint+"/query_satisfaction_value", data=json.dumps(data).encode("utf-8"))
            response = json.loads(response.text)
            general_satisfaction = general_satisfaction + float(response['userSatisfaction'])
            counter = counter + 1

        return round(general_satisfaction/counter, 4)

    def generateHistoryTrustInformation(self, producer, consumer_instance, trustorDID, trusteeDID, offerDID, previous_interaction_number):
        """ This method generates trust information that will be sent to trustor Kafka Topic. In particular,
        it is adding _n_ previous interactions (history) to be contemplated in future assessments"""

        list_interactions = []
        global consumer

        self.consumer = consumer_instance

        load_dotenv()
        trmf_endpoint = os.getenv('TRMF_C_5GBARCELONA')

        if previous_interaction_number != 0:
            trustInformationTemplate = TrustInformationTemplate()
            information = trustInformationTemplate.trustTemplate()

            """ Adding information related to the specific request """
            information["trustee"]["trusteeDID"] = trusteeDID
            information["trustee"]["offerDID"] = offerDID
            information["trustee"]["trusteeSatisfaction"] = round(random.uniform(0.8, 0.95), 4)
            information["trustor"]["trustorDID"] = trustorDID
            information["trustor"]["trusteeDID"] = trusteeDID
            information["trustor"]["offerDID"] = offerDID
            information["trustor"]["credibility"] = round(random.uniform(0.9, 0.92), 4)
            information["trustor"]["transactionFactor"] = round(random.uniform(0.85, 0.88), 4)
            information["trustor"]["communityFactor"] = round(random.uniform(0.85, 0.88), 4)
            information["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.5, 0.7),4)
            direct_weighting = round(random.uniform(0.6, 0.7),2)
            information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
            information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting
            information["trustor"]["direct_parameters"]["interactionNumber"] = self.getInteractionNumber(trustorDID, trusteeDID, offerDID)
            information["trustor"]["direct_parameters"]["totalInteractionNumber"] = self.getLastTotalInteractionNumber(trusteeDID)
            information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],4)
            information["currentInteractionNumber"] = self.getCurrentInteractionNumber(trustorDID)
            information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
            information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

            if information not in self.historical:
                #""" Adding the recommender list so as to have an initial set"""
                #recommender_list = self.setRecommenderList(information["trustor"]["trustorDID"], information["trustor"]["trusteeDID"])
                #if len(recommender_list)>0:
                    #information["trustor"]["indirect_parameters"]["recommendations"] = recommender_list

                self.historical.append(information)

            """data = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID,
                     "userSatisfaction": information["trustor"]["direct_parameters"]["userSatisfaction"],
                    "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                    "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                    "currentInteractionNumber": information["currentInteractionNumber"]}"""

            data = {"trustorDID": trustorDID, "trusteeDID": trusteeDID,
                    "offerDID": offerDID, "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                    "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                    "currentInteractionNumber": information["currentInteractionNumber"], "timestamp":
                        information["endEvaluationPeriod"], "endpoint":trmf_endpoint}

            #with open(self.dlt_file_name, 'a', encoding='UTF8', newline='') as dlt_data:
                #writer = csv.DictWriter(dlt_data, fieldnames=self.dlt_headers)
                #writer.writerow(data)
            producer.createTopic("TRMF-interconnections")
            producer.sendMessage("TRMF-interconnections", trustorDID, data)
            self.kafka_interaction_list.append(data)

            for i in range(previous_interaction_number-1):
                interaction_number = self.getInteractionNumber(trustorDID, trusteeDID, offerDID)

                trust_data = self.consumer.readLastTrustInterationValues(self.historical, trustorDID, trusteeDID, offerDID, interaction_number)

                information = trustInformationTemplate.trustTemplate()


                information["trustee"]["trusteeDID"] = trusteeDID
                information["trustee"]["offerDID"] = offerDID
                information["trustee"]["trusteeSatisfaction"] = round((round(random.uniform(0.8, 0.9),3) + (interaction_number * trust_data["trusteeSatisfaction"]))/(interaction_number+1), 4)
                #information["trustee"]["trusteeSatisfaction"] = round(random.uniform(0.8, 0.9), 3)
                information["trustor"]["trustorDID"] = trustorDID
                information["trustor"]["trusteeDID"] = trusteeDID
                information["trustor"]["offerDID"] = offerDID
                information["trustor"]["credibility"] = round((round(random.uniform(0.8, 0.9),3) + (interaction_number * trust_data["credibility"]))/(interaction_number+1), 4)
                information["trustor"]["transactionFactor"] = round((round(random.uniform(0.75, 0.95), 3) + (interaction_number * trust_data["transactionFactor"]))/(interaction_number+1), 4)
                information["trustor"]["communityFactor"] = round((round(random.uniform(0.75, 0.9), 3) + (interaction_number * trust_data["communityFactor"]))/(interaction_number+1), 4)
                information["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.5, 0.7),4)
                direct_weighting = round(random.uniform(0.6, 0.7),2)
                information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
                information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting
                information["trustor"]["direct_parameters"]["interactionNumber"] = interaction_number
                information["trustor"]["direct_parameters"]["totalInteractionNumber"] = self.getLastTotalInteractionNumber(trusteeDID)
                information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],4)
                information["currentInteractionNumber"] = self.getCurrentInteractionNumber(trustorDID)
                information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
                information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

                if information not in self.historical:
                    #""" Adding the recommender list so as to have an initial set"""
                    #recommender_list = self.setRecommenderList(information["trustor"]["trustorDID"], information["trustor"]["trusteeDID"])
                    #if len(recommender_list)>0:
                        #information["trustor"]["indirect_parameters"]["recommendations"] = recommender_list

                    self.historical.append(information)

                data = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID,
                        "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                        "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                        "currentInteractionNumber": information["currentInteractionNumber"], "timestamp":
                            information["endEvaluationPeriod"], "endpoint":trmf_endpoint}

                #with open(self.dlt_file_name, 'a', encoding='UTF8', newline='') as dlt_data:
                    #writer = csv.DictWriter(dlt_data, fieldnames=self.dlt_headers)
                    #writer.writerow(data)
                producer.createTopic("TRMF-interconnections")
                producer.sendMessage("TRMF-interconnections", trustorDID, data)
                self.kafka_interaction_list.append(data)

        return None

    def generateTrusteeInformation(self, producer, consumer, trustorDID, availableAssets, totalAssets, availableAssetLocation, totalAssetLocation, managedViolations, predictedViolations, executedViolations, nonPredictedViolations, consideredOffers, totalOffers, consideredOfferLocation, totalOfferLocation, managedOfferViolations, predictedOfferViolations, executedOfferViolations, nonPredictedOfferViolations):
        """ This method introduces Trustee information based on peerTrust equations and using the minimum
        values previously established """

        self.consumer = consumer
        load_dotenv()
        trmf_endpoint = os.getenv('TRMF_C_5GBARCELONA')

        trustee_selection = random.randint(0,3)
        offer_selection = random.randint(0,1)

        if not bool(self.list_additional_did_providers):
            "Adding the previous DID providers autogenerated to avoid the cold start"
            self.list_additional_did_offers = [[]] * self.max_previous_providers_DLT
            """with open(self.dlt_file_name) as f:
                reader = csv.DictReader(f)
                pointer = 0
                for item in reader:"""
            pointer = 0
            for item in self.kafka_interaction_list:
                if item["trustorDID"] not in self.list_additional_did_providers and pointer < self.max_previous_interactions_DLT:
                    self.list_additional_did_providers.append(item["trustorDID"])
                pointer+=1
            "Adding the previous DID offers autogenerated to avoid the cold start"
            #with open(self.dlt_file_name) as f:
                #reader = csv.DictReader(f)
            for item in self.kafka_interaction_list:
                #for item in reader:
                if item["trusteeDID"] in self.list_additional_did_providers and item["offerDID"] not in self.list_additional_did_offers:
                    self.list_additional_did_offers[self.list_additional_did_providers.index(item["trusteeDID"])].append(item["offerDID"])


        trusteeDID = self.list_additional_did_providers[trustee_selection]
        offerDID = self.list_additional_did_offers[trustee_selection][offer_selection]
        information = self.minimumTrustTemplate(trustorDID, trusteeDID, offerDID)

        print("\t* Provider ---> "+trusteeDID+" -- Product offer ---> "+offerDID)

        information["trustor"]["credibility"] = self.credibility(trustorDID, trusteeDID)
        information["trustor"]["transactionFactor"] = self.transactionContextFactor(trustorDID, trusteeDID, offerDID)
        information["trustor"]["communityFactor"] = self.communityContextFactor(trustorDID, trusteeDID)

        direct_weighting = round(random.uniform(0.6, 0.7),2)
        information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
        provider_reputation = self.providerReputation(availableAssets, totalAssets, availableAssetLocation, totalAssetLocation, managedViolations, predictedViolations, executedViolations, nonPredictedViolations)
        provider_satisfaction = self.providerSatisfaction(trustorDID, trusteeDID, provider_reputation)
        offer_reputation = self.offerReputation(consideredOffers, totalOffers, consideredOfferLocation, totalOfferLocation, managedOfferViolations, predictedOfferViolations, executedOfferViolations, nonPredictedOfferViolations)
        offer_satisfaction = self.offerSatisfaction(trustorDID, trusteeDID, offerDID, offer_reputation)

        information["trustor"]["direct_parameters"]["providerSatisfaction"] = provider_satisfaction
        ps_weighting = round(random.uniform(0.4, 0.6),2)
        information["trustor"]["direct_parameters"]["PSWeighting"] = ps_weighting
        information["trustor"]["direct_parameters"]["offerSatisfaction"] = offer_satisfaction
        os_weighting = 1-ps_weighting
        information["trustor"]["direct_parameters"]["OSWeighting"] = os_weighting
        information["trustor"]["direct_parameters"]["providerReputation"] = provider_reputation
        information["trustor"]["direct_parameters"]["offerReputation"] = offer_reputation
        information["trustor"]["direct_parameters"]["availableAssets"] = availableAssets
        information["trustor"]["direct_parameters"]["totalAssets"] = totalAssets
        information["trustor"]["direct_parameters"]["availableAssetLocation"] = availableAssetLocation
        information["trustor"]["direct_parameters"]["totalAssetLocation"] = totalAssetLocation
        information["trustor"]["direct_parameters"]["managedViolations"] = managedViolations
        information["trustor"]["direct_parameters"]["predictedViolations"] = predictedViolations
        information["trustor"]["direct_parameters"]["executedViolations"] = executedViolations
        information["trustor"]["direct_parameters"]["nonPredictedOfferViolations"] = nonPredictedViolations

        information["trustor"]["direct_parameters"]["consideredOffers"] = consideredOffers
        information["trustor"]["direct_parameters"]["totalOffers"] = totalOffers
        information["trustor"]["direct_parameters"]["consideredOfferLocation"] = consideredOfferLocation
        information["trustor"]["direct_parameters"]["totalOfferLocation"] = totalOfferLocation
        information["trustor"]["direct_parameters"]["managedOfferViolations"] = managedOfferViolations
        information["trustor"]["direct_parameters"]["predictedOfferViolations"] = predictedOfferViolations
        information["trustor"]["direct_parameters"]["executedOfferViolations"] = executedOfferViolations
        information["trustor"]["direct_parameters"]["nonPredictedOfferViolations"] = nonPredictedOfferViolations

        #information["trustor"]["direct_parameters"]["feedbackNumber"] = nonPredictedViolations
        #information["trustor"]["direct_parameters"]["feedbackOfferNumber"] = nonPredictedViolations
        #information["trustor"]["direct_parameters"]["location"] = nonPredictedViolations
        #information["trustor"]["direct_parameters"]["validFor"] = nonPredictedViolations
        information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting

        information["trustee"]["trusteeDID"] = trusteeDID
        information["trustee"]["offerDID"] = offerDID
        information["trustee"]["trusteeSatisfaction"] = self.getTrusteeSatisfactionDLT(trusteeDID)
        information["trustor"]["direct_parameters"]["userSatisfaction"] = self.satisfaction(ps_weighting, os_weighting, provider_satisfaction, offer_satisfaction)
        information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],4)

        if information not in self.historical:
            self.historical.append(information)

        data = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID,
                "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                "currentInteractionNumber": information["currentInteractionNumber"], "timestamp":
                    information["endEvaluationPeriod"], "endpoint":trmf_endpoint}

        #with open(self.dlt_file_name, 'a', encoding='UTF8', newline='') as dlt_data:
            #writer = csv.DictWriter(dlt_data, fieldnames=self.dlt_headers)
            #writer.writerow(data)
        producer.createTopic("TRMF-interconnections")
        producer.sendMessage("TRMF-interconnections", trustorDID, data)
        self.kafka_interaction_list.append(data)

        return data

    def setTrusteeInteractions(self, producer, consumer, trusteeDID, interactions):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """

        for i in range(interactions):
            availableAssets = randint(2,10)
            totalAssets = availableAssets + randint(0,2)
            availableAssetLocation = randint(1,6)
            totalAssetLocation = availableAssetLocation + randint(0,2)
            managedViolations = randint(10,25)
            predictedViolations = managedViolations + randint(0,3)
            executedViolations = randint(0,3)
            nonPredictedViolations = randint(0,4)

            consideredOffers = randint(2,10)
            totalOffers = consideredOffers + randint(0,2)
            consideredOfferLocation = randint(1,6)
            totalOfferLocation = consideredOfferLocation + randint(0,2)
            managedOfferViolations = randint(10,25)
            predictedOfferViolations = managedOfferViolations + randint(0,3)
            executedOfferViolations = randint(0,3)
            nonPredictedOfferViolations = randint(0,4)

            self.generateTrusteeInformation(producer, consumer, trusteeDID, availableAssets, totalAssets, availableAssetLocation, totalAssetLocation, managedViolations, predictedViolations, executedViolations, nonPredictedViolations, consideredOffers, totalOffers, consideredOfferLocation, totalOfferLocation, managedOfferViolations, predictedOfferViolations, executedOfferViolations, nonPredictedOfferViolations)

    def getLastHistoryTrustValue(self, trustorDID, trusteeDID):
        """ This method retrieves the last trust score that a trustor has stored about a trustee in its historical"""

        global consumer

        trust_information = self.consumer.readLastTrustValue(self.historical, trustorDID, trusteeDID)

        if bool(trust_information):
            last_truste_value = trust_information["trust_value"]
            return last_truste_value
        else:
            """In this case, Trustor didn't have an interaction with Trustee and 
            the provider recommendation is based on the last interaction registered in the DLT"""
            return 0

    def getLastOfferHistoryTrustValue(self, trustorDID, trusteeDID, offerDID):
        """ This method retrieves the last trust score that a trustor has stored about an offer trustee
        in its historical"""
        global consumer

        trust_information = self.consumer.readLastTrustValueOffer(self.historical, trustorDID, trusteeDID, offerDID)

        if bool(trust_information):
            last_truste_value = trust_information["trust_value"]
            return last_truste_value
        else:
            """In this case, Trustor didn't have an interaction with Trustee and 
            the provider recommendation is based on the last interaction registered in the DLT"""
            return 1

    def getOfferFeedbackNumberDLT(self, trusteeDID, offerDID):
        """ This method counts the number of feedbacks registered in the DLT for a particular offer """
        counter = 0

        """ Check that the last recommender is not ourselves"""
        #list_interactions = self.find_by_column(self.dlt_file_name, 'trusteeDID', trusteeDID)
        list_interactions = self.find_by_column('trusteeDID', trusteeDID)

        """ Check the number of interactions whose offerID is the same"""
        for interaction in list_interactions:
            if interaction["offerDID"] == offerDID:
                counter+=1

        return counter

    def getTrusteeFeedbackNumberDLT(self, trusteeDID):
        """ This method counts the number of feedbacks registered in the DLT for a particular trustee """

        """ Check that the last recommender is not ourselves"""
        #return len(self.find_by_column(self.dlt_file_name, 'trusteeDID', trusteeDID))
        return len(self.find_by_column('trusteeDID', trusteeDID))


    def getTrustworthyRecommendationDLT(self, trustorDID, trusteeDID, trustworthy_recommender_list):
        """ This method returns from a trusted list those recommender that have interacted with the trustor """

        trustworthy_recommendations = []

        #list_interactions = self.find_by_column(self.dlt_file_name, 'trusteeDID', trusteeDID)
        list_interactions = self.find_by_column('trusteeDID', trusteeDID)
        """ Starting from the end to identify the last recommender"""
        for interaction in reversed(list_interactions):
            """ We obtain the latest trust value from our reliable recommenders on the trustor giving 
            the highest weight to the final recommendations."""
            if interaction['trustorDID'] != trustorDID and interaction['trustorDID'] in trustworthy_recommender_list:
                trustworthy_recommendations.append(interaction['trustorDID'])
                trustworthy_recommender_list.remove(interaction['trustorDID'])

        return trustworthy_recommendations

    def getLastCredibility(self, trustorDID, trusteeDID):
        """ This method recovers the last credibility value registered in the DLT for a particular trustee"""
        global consumer

        trust_information = self.consumer.readLastTrustValue(self.historical, trustorDID, trusteeDID)

        if bool(trust_information):
            last_credibility = trust_information["credibility"]
            return last_credibility
        else:
            """In this case, Trustor didn't have an credibility with Trustee and 
            the provider recommendation is based on the last history value registered in its Kafka topic"""
            return 1

    def getTrustorInteractions(self, trustorDID):
        """ This methods return all trustor's interactions registered in the DLT"""
        trustee_interactions = []

        #list_trustor_interactions = self.find_by_column(self.dlt_file_name, 'trustorDID', trustorDID)
        list_trustor_interactions = self.find_by_column('trustorDID', trustorDID)
        for interaction in list_trustor_interactions:
            if interaction not in trustee_interactions:
                #trustee_interactions.append(interaction["trusteeDID"])
                trustee_interactions.append(interaction)

        return trustee_interactions

    def getTrusteeInteractions(self, trustorDID, trusteeDID):
        """ This methods return all entities that have interacted with a trustee and
        have published feedbacks in the DLT"""
        interactions = []

        #list_interactions = self.find_by_column(self.dlt_file_name, 'trusteeDID', trusteeDID)
        list_interactions = self.find_by_column('trusteeDID', trusteeDID)
        for interaction in list_interactions:
            if interaction["trustorDID"] != trustorDID:
                interactions.append(interaction["trustorDID"])
                return interactions

        return interactions

    """%%%%%%%%%%%%%%   PEERTRUST EQUATIONS %%%%%%%%%%%%%%%%%"""

    def credibility(self, trustorDID, trusteeDID):

        previous_trustor_interactions = self.getTrustorInteractions(trustorDID)
        similarity_summation = 0.0

        summation_counter = 0

        if previous_trustor_interactions:
            for previous_interaction in previous_trustor_interactions:
                summation_counter = summation_counter + 1
                similarity_summation = similarity_summation + self.similarity(previous_interaction["trusteeDID"])
        else:
            similarity_summation = 0.5
            summation_counter = 0.5

        trustee_similarity = self.similarity(trusteeDID)

        credibility = trustee_similarity/(similarity_summation/summation_counter)
        if credibility > 1.0:
            credibility = (similarity_summation/summation_counter)/trustee_similarity
        elif credibility == 0.0:
            "Just in case of cold-start"
            return 0.5

        return round(credibility, 4)

    def similarity(self, trusteeDID):
        """ This method identifies stakeholders who have evaluated one or more entities in common with the trustor
        (trustee parameter) to compare their satisfaction values and determine how credible the trustor's
        (trustee parameter) satisfaction value is """

        common_interaction = []
        trustor_interaction_list = self.getTrustorInteractions(trusteeDID)

        for interaction in trustor_interaction_list:
            common_interaction = self.getTrusteeInteractions(trusteeDID, interaction["trusteeDID"])
            if common_interaction:
                """ Currently, only one common interaction is contemplated """
                break

        common_interaction_list = self.getTrustorInteractions(common_interaction[0]["trusteeDID"])

        IJS_counter = 0
        global_satisfaction_summation = 0.0

        for interaction in trustor_interaction_list:
            if interaction["trusteeDID"] in common_interaction_list:

                trustor_satisfaction_summation = self.consumer.readSatisfactionSummation(self.historical, trusteeDID, interaction["trusteeDID"])
                if trustor_satisfaction_summation == 0.0:
                    endpoint = interaction["endpoint"].split("/")[2]
                    data = {"trustorDID": trusteeDID, "trusteeDID": interaction["trusteeDID"], "offerDID": None}
                    response = requests.post("http://"+endpoint+"/query_satisfaction_value", data=json.dumps(data).encode("utf-8"))
                    response = json.loads(response.text)
                    trustor_satisfaction_summation = response['userSatisfaction']

                common_interaction_satisfaction_summation = self.consumer.readSatisfactionSummation(self.historical, common_interaction[0]["trusteeDID"], interaction["trusteeDID"])
                if common_interaction_satisfaction_summation == 0.0:
                    endpoint = interaction["endpoint"].split("/")[2]
                    data = {"trustorDID": common_interaction[0]["trusteeDID"], "trusteeDID": interaction["trusteeDID"], "offerDID": None}
                    response = requests.post("http://"+endpoint+"/query_satisfaction_value", data=json.dumps(data).encode("utf-8"))
                    response = json.loads(response.text)
                    common_interaction_satisfaction_summation = response['userSatisfaction']


                satisfaction_summation = pow((trustor_satisfaction_summation - common_interaction_satisfaction_summation), 2)
                global_satisfaction_summation = global_satisfaction_summation + satisfaction_summation
                IJS_counter = IJS_counter + 1


        final_similarity = 1 - math.sqrt(global_satisfaction_summation/IJS_counter)

        return final_similarity


    def communityContextFactor(self, trustorDID, trusteeDID):
        """ Static list of recommender based on the domains registered in the DLT. TODO dynamic """

        global consumer
        global recommender_list

        #trustworthy_recommender_list = self.list_additional_did_providers[:]
        trustworthy_recommender_list = self.recommender_list[:]

        total_registered_trustee_interaction = self.consumer.readTrusteeInteractions(self.historical, trusteeDID)

        number_trustee_feedbacks_DLT = self.getTrusteeFeedbackNumberDLT(trusteeDID)

        trustee_interaction_rate = number_trustee_feedbacks_DLT / total_registered_trustee_interaction

        if trustorDID in trustworthy_recommender_list:
            trustworthy_recommender_list.remove(trustorDID)

        trustworthy_recommendations = self.getTrustworthyRecommendationDLT(trustorDID, trusteeDID, trustworthy_recommender_list)

        summation_trustworthy_recommendations = 0.0
        recommendation_counter = 0

        for recommender in trustworthy_recommendations:
            last_value = self.getLastHistoryTrustValue(recommender, trusteeDID)
            if last_value != 0:
                last_credibility = self.getLastCredibility(trustorDID, recommender)
                summation_trustworthy_recommendations = summation_trustworthy_recommendations + (last_credibility*last_value)
                recommendation_counter = recommendation_counter + 1


        return round((trustee_interaction_rate+(summation_trustworthy_recommendations/recommendation_counter))/2,4)

    def bad_mouthing_attack_resilience(self, trustorDID, trusteeDID, new_trusteeDID, new_offerDID):

        global consumer
        global recommender_list

        """ This constant displays the weighting of action trust and recommendation trust """
        ALPHA_WEIGTHING = 0.5
        RECOMMENDATION_THRESHOLD = 0.2

        deleted_recommender = False
        no_recommendations = False

        #if bool(self.recommender_list):
            #self.recommender_list = self.list_additional_did_providers[:]

        #trustworthy_recommender_list = self.list_additional_did_providers[:]

        total_registered_trustee_interaction = self.consumer.readTrusteeInteractions(self.historical, new_trusteeDID)

        number_trustee_feedbacks_DLT = self.getTrusteeFeedbackNumberDLT(new_trusteeDID)

        trustee_interaction_rate = number_trustee_feedbacks_DLT / total_registered_trustee_interaction

        if trusteeDID in self.recommender_list:
            self.recommender_list.remove(trusteeDID)
            deleted_recommender = True

        trustworthy_recommendations = self.getTrustworthyRecommendationDLT(trusteeDID, new_trusteeDID, self.recommender_list)

        summation_trustworthy_recommendations = 0.0
        average_trust_recommenders = 0.0
        counter = 0

        if len(trustworthy_recommendations) > 0:
            "If we had trustworthy recommenders, we will use their recommendations together with our trust recommendation"
            for recommender in trustworthy_recommendations:
                recommendation_trust = self.consumer.readLastRecommendationTrustValue(self.historical, trustorDID, trusteeDID, recommender)
                if bool(recommendation_trust) and recommendation_trust >= RECOMMENDATION_THRESHOLD:
                    counter +=1
                    average_trust_recommenders = average_trust_recommenders + recommendation_trust
                elif bool(recommendation_trust) and recommendation_trust < RECOMMENDATION_THRESHOLD:
                    print("Recommendation trust, ",recommendation_trust," is lower than Threshold: ", RECOMMENDATION_THRESHOLD)

            try:
                average_trust_recommenders = average_trust_recommenders / counter
            except ZeroDivisionError:
                average_trust_recommenders = 0
                no_recommendations = True

            if not no_recommendations:
                for recommender in trustworthy_recommendations:
                    recommendation_trust = self.consumer.readLastRecommendationTrustValue(self.historical, trustorDID, trusteeDID, recommender)
                    if bool(recommendation_trust) and recommendation_trust >= 0.3:
                        last_trust_score_recommender = self.getLastHistoryTrustValue(trusteeDID, recommender)
                        action_trust = ALPHA_WEIGTHING * last_trust_score_recommender

                        recommendation = self.getLastHistoryTrustValue(recommender, new_trusteeDID)
                        trust_on_recommender = (1-ALPHA_WEIGTHING) * (recommendation_trust * recommendation)

                        recommender_influence = recommendation_trust / average_trust_recommenders
                        summation_trustworthy_recommendations = summation_trustworthy_recommendations + ((action_trust + trust_on_recommender) * recommender_influence)

                        trustor_template = self.consumer.readAllTemplateTrustValue(self.historical, trustorDID, trusteeDID)

                        new_recommender = True

                        for recommendation_list in trustor_template["trustor"]["indirect_parameters"]["recommendations"]:
                            if recommendation_list["recommender"] == recommender:
                                recommendation_list["average_recommendations"] = ((recommendation_list["average_recommendations"] * recommendation_list["recommendation_total_number"]) + recommendation) / (recommendation_list["recommendation_total_number"] + 1)
                                recommendation_list["recommendation_total_number"] =  recommendation_list["recommendation_total_number"] + 1
                                recommendation_list["last_recommendation"] = recommendation
                                new_recommender = False

                        if new_recommender:
                            recommendation_list = trustor_template["trustor"]["indirect_parameters"]["recommendations"]
                            recommendation_list.append({"recommender": recommender,"trust_value": last_trust_score_recommender,
                                                        "recommendation_trust": 0.5, "recommendation_total_number": 1,
                                                        "average_recommendations": recommendation, "last_recommendation": recommendation})
                            trustor_template["trustor"]["indirect_parameters"]["recommendations"] = recommendation_list

                        self.historical.append(trustor_template)
        else:
            "We don't have reliable recommendations and we are going to obtain external recommendations"
            no_recommendations = True

        if no_recommendations:
            "We don't have trustworthy recommenders and we use external recommendations"
            self.consumer.start("TRMF-interconnections")
            self.consumer.subscribe("TRMF-interconnections")
            external_recommendations = self.consumer.start_reading(trustorDID, new_offerDID)

            if bool(external_recommendations):
                trustor_template = self.consumer.readAllTemplateTrustValue(self.historical, trustorDID, trusteeDID)
                recommendation_list = trustor_template["trustor"]["indirect_parameters"]["recommendations"]

                for external_recommendation in external_recommendations:
                    recommendation_list.append({"recommender": external_recommendation["trustorDID"],"trust_value": 0.5,
                                                "recommendation_trust": 0.5, "recommendation_total_number": 1,
                                                "average_recommendations": external_recommendation["trust_value"],
                                                "last_recommendation": external_recommendation["trust_value"]})
                    summation_trustworthy_recommendations = summation_trustworthy_recommendations + external_recommendation["trust_value"]
                    "Adding new recommenders"
                    self.recommender_list.append(external_recommendation["trustorDID"])

                counter = len(external_recommendations)
                if counter > 0:
                    trustor_template["trustor"]["indirect_parameters"]["recommendations"] = recommendation_list
                    self.historical.append(trustor_template)
            else:
                return 0.5

        if deleted_recommender:
            self.recommender_list.append(trusteeDID)

        return round((trustee_interaction_rate+(summation_trustworthy_recommendations/counter))/2,4)


    def communityContextFactor2(self, trustorDID, trusteeDID):
        """ This method displays the recommender on the screen and we have changed the parameters of the
        getLastCredibility, the only difference being  """

        global consumer
        global recommender_list

        #trustworthy_recommender_list = self.list_additional_did_providers[:]
        trustworthy_recommender_list = self.recommender_list[:]

        total_registered_trustee_interaction = self.consumer.readTrusteeInteractions(self.historical, trusteeDID)

        number_trustee_feedbacks_DLT = self.getTrusteeFeedbackNumberDLT(trusteeDID)

        trustee_interaction_rate = number_trustee_feedbacks_DLT / total_registered_trustee_interaction

        if trustorDID in trustworthy_recommender_list:
            trustworthy_recommender_list.remove(trustorDID)

        trustworthy_recommendations = self.getTrustworthyRecommendationDLT(trustorDID, trusteeDID, trustworthy_recommender_list)

        summation_trustworthy_recommendations = 0.0
        print("\n\tComputing community factor:")
        for recommender in trustworthy_recommendations:
            print("\n\tRecommendation from ", recommender, " over ", trusteeDID, " to calculate the community factor")
            last_value = self.getLastHistoryTrustValue(recommender, trusteeDID)
            print("\tLast trust score of ", recommender, " on ", trusteeDID, " was ---> ",last_value)
            last_credibility = self.getLastCredibility(trustorDID, recommender)
            print("\tCredibility of ",trustorDID," on the recommender (", recommender, ") --->", round(last_credibility, 4), "\n")
            summation_trustworthy_recommendations = summation_trustworthy_recommendations + (last_credibility*last_value)


        return round((trustee_interaction_rate+(summation_trustworthy_recommendations/len(trustworthy_recommendations)))/2,4)

    def transactionContextFactor(self, trustorDID, trusteeDID, offerDID):
        global consumer
        """ Currently, only one time-window is contemplated """

        total_registered_trustee_interaction = self.consumer.readTrusteeInteractions(self.historical, trusteeDID)
        total_registered_offer_interactions = self.consumer.readOfferTrusteeInteractions(self.historical, trusteeDID, offerDID)

        number_offer_trustee_feedbacks_DLT = self.getOfferFeedbackNumberDLT(trusteeDID, offerDID)
        number_trustee_feedbacks_DLT = self.getTrusteeFeedbackNumberDLT(trusteeDID)

        try:
            offer_percentage_DLT = number_offer_trustee_feedbacks_DLT / total_registered_offer_interactions
        except ZeroDivisionError:
            offer_percentage_DLT = 0

        try:
            trustee_percentage_DLT = number_trustee_feedbacks_DLT / total_registered_trustee_interaction
        except ZeroDivisionError:
            trustee_percentage_DLT = 0

        if offer_percentage_DLT == 0 and trustee_percentage_DLT != 0:
            transactionFactor = (number_trustee_feedbacks_DLT / total_registered_trustee_interaction)/ 2
        elif offer_percentage_DLT != 0 and trustee_percentage_DLT == 0:
            transactionFactor = (number_offer_trustee_feedbacks_DLT / total_registered_offer_interactions)/ 2
        elif offer_percentage_DLT == 0 and trustee_percentage_DLT == 0:
            transactionFactor = 0.5
        else:
            transactionFactor = (number_offer_trustee_feedbacks_DLT / total_registered_offer_interactions + number_trustee_feedbacks_DLT / total_registered_trustee_interaction)/2

        return round(transactionFactor, 4)


    def satisfaction(self, PSWeighting, OSWeighting, providerSatisfaction, offerSatisfaction):

        return PSWeighting*providerSatisfaction + OSWeighting*offerSatisfaction


    def providerSatisfaction(self, trustorDID, trusteeDID, providerReputation):
        """ This method computes the Provider's satisfaction considering its reputation and recommendations"""

        """ Only one recommendation is currently contemplated"""
        last_interaction = self.getRecommenderDLT(trustorDID, trusteeDID)

        if not bool(last_interaction):
            return 0.5
        else:
            provider_recommendation = self.getLastRecommendationValue(last_interaction)

            """ We obtain our last trust value on the recommender from our Kafka topic """
            last_trust_score_recommender = self.getLastHistoryTrustValue(trustorDID, last_interaction['trustorDID'])
            """ If we don't have a trust value about the recommender, its recommendation is fully contemplated """
            if last_trust_score_recommender == 0:
                provider_satisfaction = round((providerReputation + provider_recommendation)/2, 4)
            else:
                provider_satisfaction = round((providerReputation + provider_recommendation * last_trust_score_recommender)/2, 4)

        return provider_satisfaction

    def providerReputation(self, availableAssets, totalAssets, availableAssetLocation, totalAssetLocation, managedViolations, predictedViolations, executedViolations, nonPredictedViolations):
        """ Currently, only one time-window is contemplated"""

        try:
            assets_percentage = availableAssets / totalAssets
        except ZeroDivisionError:
            assets_percentage = 0

        try:
            assets_location_percentage = availableAssetLocation / totalAssetLocation
        except ZeroDivisionError:
            assets_location_percentage = 0

        try:
            managed_violations_percentage = managedViolations / predictedViolations
        except ZeroDivisionError:
            managed_violations_percentage = 0

        try:
            violations_percentage = (executedViolations + nonPredictedViolations) / predictedViolations
        except ZeroDivisionError:
            violations_percentage = 0

        reputation = ((assets_percentage + assets_location_percentage + (2 * managed_violations_percentage) - (2 * violations_percentage)) + 2) / 6

        return reputation

    def offerSatisfaction(self, trustorDID, trusteeDID, offerDID, offerReputation):
        """ This method computes the Provider's satisfaction considering its reputation and recommendations"""

        """ Only one recommendation is currently contemplated"""
        last_interaction = self.getRecommenderOfferDLT(trustorDID, trusteeDID, offerDID)

        """ If we don't have a trust value about the recommender, it is its first interaction """
        if not bool(last_interaction):
            return 0.5
        else:
            provider_recommendation = self.getLastOfferRecommendationValue(last_interaction)

            """ We obtain our last trust value on the offer from our Kafka topic"""
            last_trust_score_recommender = self.getLastOfferHistoryTrustValue(last_interaction['trustorDID'], trusteeDID, offerDID)

            """ If we don't have a trust value about the recommender its recommendation is fully contemplated """
            if last_trust_score_recommender == 0:
                provider_satisfaction = round((offerReputation + provider_recommendation )/2, 4)
            else:
                provider_satisfaction = round((offerReputation + provider_recommendation * last_trust_score_recommender)/2, 4)

        return provider_satisfaction

    def offerReputation(self, consideredOffers, totalOffers, consideredOfferLocation, totalOfferLocation, managedOfferViolations, predictedOfferViolations, executedOfferViolations, nonPredictedOfferViolations):
        """ Currently, only one time-window is contemplated"""
        try:
            assets_percentage = consideredOffers / totalOffers
        except ZeroDivisionError:
            assets_percentage = 0
        try:
            assets_location_percentage = consideredOfferLocation / totalOfferLocation
        except ZeroDivisionError:
            assets_location_percentage = 0
        try:
            managed_violations_percentage = managedOfferViolations / predictedOfferViolations
        except ZeroDivisionError:
            managed_violations_percentage = 0
        try:
            violations_percentage = (executedOfferViolations + nonPredictedOfferViolations) / predictedOfferViolations
        except ZeroDivisionError:
            violations_percentage = 0


        reputation = ((assets_percentage + assets_location_percentage + (2 * managed_violations_percentage) - (2 * violations_percentage)) + 2) / 6

        return reputation