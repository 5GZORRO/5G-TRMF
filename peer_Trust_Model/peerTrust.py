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


from producer import *
from trustInformationTemplate import *
from consumer import *
from datetime import datetime
from random import randint

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

    """ Parameters to define a minimum interactions in the system and avoid a cold start"""
    max_previous_providers_DLT = 4
    max_previous_providers_interactions_DLT = 3
    max_previous_interactions_DLT = max_previous_providers_DLT * max_previous_providers_interactions_DLT
    max_different_interactions = max_previous_providers_DLT * 2

    historical = []
    consumer = None

    def find_by_column(self, filename, column, value):
        """ This method discovers interactions registered in the DLT looking at one specific value"""

        list_object = []
        with open(filename) as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item[column] == value:
                    list_object.append(item)
        return list(list_object)

    def find_by_two_column(self, filename, column1, value1, colum2, value2):
        """ This method discovers interactions registered in the DLT looking at two specific values"""

        list_object = []
        with open(filename) as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item[column1] == value1 and item[colum2] == value2:
                    list_object.append(item)
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
        information["trustee"]["trusteeSatisfaction"] = round(random.uniform(0.8, 0.95),3)
        information["trustor"]["trustorDID"] = trustorDID
        information["trustor"]["trusteeDID"] = trusteeDID
        information["trustor"]["offerDID"] = offerDID
        information["trustor"]["credibility"] = round(random.uniform(0.75, 0.9),3)
        information["trustor"]["transactionFactor"] = round(random.uniform(0.8, 0.9),3)
        information["trustor"]["communityFactor"] = round(random.uniform(0.85, 0.9),3)
        information["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.75, 0.9),3)
        direct_weighting = round(random.uniform(0.6, 0.7),2)
        information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
        information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting
        information["trustor"]["direct_parameters"]["interactionNumber"] = self.getInteractionNumber(trustorDID, trusteeDID)
        information["trustor"]["direct_parameters"]["totalInteractionNumber"] = self.getLastTotalInteractionNumber(trusteeDID)
        information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],3)
        information["currentInteractionNumber"] = self.getCurrentInteractionNumber(trustorDID)
        information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
        information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

        return information

    def minimumTrustValuesDLT(self, producer, trustor, dict_product_offers):
        """ This method establishes multiple trust relationships from list of product offers to start the trust
         model with a set of minimum relationships. In addition, it also simulates the registration of such interactions
         in the DLT """

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


                new_interaction = {"trustorDID": self.list_additional_did_providers[i], "trusteeDID":  new_trustee,
                                   "offerDID": new_offer, "userSatisfaction": round(random.uniform(0.80, 0.99), 3),
                                   "interactionNumber": 1, "totalInteractionNumber": 6, "currentInteractionNumber": 8}

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
                    new_interaction = {"trustorDID": "did:5gzorro:domain-Z", "trusteeDID":  trustee, "offerDID": offer,
                                       "userSatisfaction": round(random.uniform(0.80, 0.99), 3), "interactionNumber": 1, "totalInteractionNumber": 6, "currentInteractionNumber": 8}
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
        for interaction in data:
            trust_informartion = self.minimumTrustTemplate(interaction["trustorDID"], interaction["trusteeDID"], interaction["offerDID"])
            trust_informartion["trustor"]["direct_parameters"]["userSatisfaction"] = interaction["userSatisfaction"]
            trust_informartion["trustor"]["direct_parameters"]["interactionNumber"] = interaction["interactionNumber"]
            trust_informartion["trustor"]["direct_parameters"]["totalInteractionNumber"] = interaction["totalInteractionNumber"]
            trust_informartion["currentInteractionNumber"] = interaction["currentInteractionNumber"]

            """ The minimum interactions are also registered in the Trustor's historical but 
            they must be deleted when cold start is not used """
            interactions.append(trust_informartion)

        for i in interactions:
            self.historical.append(i)

        return data

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

        last_total_iteraction_number = 1

        with open(self.dlt_file_name) as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item["trustorDID"] == trusteeDID and int(item["currentInteractionNumber"]) > last_total_iteraction_number:
                    last_total_iteraction_number = int(item["currentInteractionNumber"])
                elif item["trusteeDID"] == trusteeDID and int(item["totalInteractionNumber"]) > last_total_iteraction_number:
                    last_total_iteraction_number = int(item["totalInteractionNumber"])

        return last_total_iteraction_number

    def getCurrentInteractionNumber(self, trustorDID):
        """ This method returns the next interaction number for a trustor """

        current_iteraction_number = 0

        with open(self.dlt_file_name) as f:
            reader = csv.DictReader(f)
            for item in reader:
                if item["trustorDID"] == trustorDID and int(item["currentInteractionNumber"]) > current_iteraction_number:
                    current_iteraction_number = int(item["currentInteractionNumber"])
                elif item["trusteeDID"] == trustorDID and int(item["totalInteractionNumber"]) > current_iteraction_number:
                    current_iteraction_number = int(item["totalInteractionNumber"])

        return current_iteraction_number+1

    def getInteractionNumber(self, trustorDID, trusteeDID):
        """ This method retrieves the number of interactions between two entities and adds one more interaction """
        iteraction_number = 0

        list_interactions = self.find_by_column(self.dlt_file_name, 'trustorDID', trustorDID)
        for interaction in list_interactions:
            if interaction["trusteeDID"] == trusteeDID and int(interaction["interactionNumber"]) > iteraction_number:
                iteraction_number = int(interaction["interactionNumber"])

        return iteraction_number+1


    def getRecommenderDLT(self, trustorDID, trusteeDID):
        """ This method recovers a recommender, who is reliable for us, that has recently interacted with a trustee.
        Return the last interaction in order to request the last trust value. In this case, reliable means
        other trustees with whom we have previously interacted with """

        last_interaction = {}

        last_registered_interaction = True

        with open(self.dlt_file_name) as f:
            reader = csv.DictReader(f)
            """ Starting from the end to identify the last recommender"""
            for interaction in reversed(list(reader)):
                """ Check that the last recommender is not ourselves"""
                if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID:
                    """ Store the most recent interaction with the Trustee to return it in the case of no trustworthy 
                    recommenders can be found"""
                    if last_registered_interaction:
                        last_interaction = interaction
                        last_registered_interaction = False
                    """Check if the Trustor is reliable for us"""
                    for trustworthy_candidate in reversed(list(reader)):
                        if trustworthy_candidate['trustorDID'] == trustorDID and trustworthy_candidate['trusteeDID'] == interaction['trustorDID']:
                            return dict(interaction)
        return dict(last_interaction)

    def getRecommenderOfferDLT(self, trustorDID, trusteeDID, offerDID):
        """ This method recovers an offer associated with a recommender, who is reliable for us, that has recently
        interacted with a trustee. Return the last interaction in order to request the last trust value.
        In this case, reliable means other trustees with whom we have previously interacted with"""

        last_interaction = {}

        last_registered_interaction = True

        with open(self.dlt_file_name) as f:
            reader = csv.DictReader(f)
            """ Starting from the end to identify the last recommender"""
            for interaction in reversed(list(reader)):
                """ Check that the last recommender is not ourselves"""
                if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID and interaction['offerDID'] == offerDID:
                    """ Store the most recent interaction with the Trustee """
                    if last_registered_interaction:
                        last_interaction = interaction
                        last_registered_interaction = False
                    """ Check if the Trustor is reliable for us """
                    for trustworthy_candidate in reversed(list(reader)):
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

        last_interaction = self.find_by_column(self.dlt_file_name, 'trustorDID', trusteeDID)
        for interaction in last_interaction:
            general_satisfaction = general_satisfaction + float(interaction['userSatisfaction'])
            counter = counter + 1

        return round(general_satisfaction/counter, 3)

    def generateHistoryTrustInformation(self, producer, consumer_instance, trustorDID, trusteeDID, offerDID, previous_interaction_number):
        """ This method generates trust information that will be sent to trustor Kafka Topic. In particular,
        it is adding _n_ previous interactions (history) to be contemplated in future assessments"""

        list_interactions = []
        global consumer

        self.consumer = consumer_instance

        if previous_interaction_number != 0:
            trustInformationTemplate = TrustInformationTemplate()
            information = trustInformationTemplate.trustTemplate()

            """ Adding information related to the specific request """
            information["trustee"]["trusteeDID"] = trusteeDID
            information["trustee"]["offerDID"] = offerDID
            information["trustee"]["trusteeSatisfaction"] = round(random.uniform(0.8, 0.95), 3)
            information["trustor"]["trustorDID"] = trustorDID
            information["trustor"]["trusteeDID"] = trusteeDID
            information["trustor"]["offerDID"] = offerDID
            information["trustor"]["credibility"] = 0.913
            information["trustor"]["transactionFactor"] = 0.856
            information["trustor"]["communityFactor"] = 0.865
            information["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.8, 0.95),3)
            direct_weighting = round(random.uniform(0.6, 0.7),2)
            information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
            information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting
            information["trustor"]["direct_parameters"]["interactionNumber"] = self.getInteractionNumber(trustorDID, trusteeDID)
            information["trustor"]["direct_parameters"]["totalInteractionNumber"] = self.getLastTotalInteractionNumber(trusteeDID)
            information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],3)
            information["currentInteractionNumber"] = self.getCurrentInteractionNumber(trustorDID)
            information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
            information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

            if information not in self.historical:
                self.historical.append(information)

            data = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID,
                     "userSatisfaction": information["trustor"]["direct_parameters"]["userSatisfaction"],
                    "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                    "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                    "currentInteractionNumber": information["currentInteractionNumber"]}

            with open(self.dlt_file_name, 'a', encoding='UTF8', newline='') as dlt_data:
                writer = csv.DictWriter(dlt_data, fieldnames=self.dlt_headers)
                writer.writerow(data)

            for i in range(previous_interaction_number-1):
                interaction_number = self.getInteractionNumber(trustorDID, trusteeDID)

                trust_data = self.consumer.readLastTrustInterationValues(self.historical, trustorDID, trusteeDID, offerDID, interaction_number)

                information["trustee"]["trusteeDID"] = trusteeDID
                information["trustee"]["offerDID"] = offerDID
                information["trustee"]["trusteeSatisfaction"] = round((round(random.uniform(0.8, 0.9),3) + trust_data["trusteeSatisfaction"])/2, 3)
                #information["trustee"]["trusteeSatisfaction"] = round(random.uniform(0.8, 0.9), 3)
                information["trustor"]["trustorDID"] = trustorDID
                information["trustor"]["trusteeDID"] = trusteeDID
                information["trustor"]["offerDID"] = offerDID
                information["trustor"]["credibility"] = round((round(random.uniform(0.8, 0.9),3) + trust_data["credibility"])/2, 3)
                information["trustor"]["transactionFactor"] = round((round(random.uniform(0.75, 0.95), 3) + trust_data["transactionFactor"])/2, 3)
                information["trustor"]["communityFactor"] = round((round(random.uniform(0.75, 0.9), 3) + trust_data["communityFactor"])/2, 3)
                information["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.8, 0.9),3)
                direct_weighting = round(random.uniform(0.6, 0.7),2)
                information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
                information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting
                information["trustor"]["direct_parameters"]["interactionNumber"] = interaction_number
                information["trustor"]["direct_parameters"]["totalInteractionNumber"] = self.getLastTotalInteractionNumber(trusteeDID)
                information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],3)
                information["currentInteractionNumber"] = self.getCurrentInteractionNumber(trustorDID)
                information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
                information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

                if information not in self.historical:
                    self.historical.append(information)

                data = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID,
                        "userSatisfaction": information["trustor"]["direct_parameters"]["userSatisfaction"],
                        "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                        "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                        "currentInteractionNumber": information["currentInteractionNumber"]}

                with open(self.dlt_file_name, 'a', encoding='UTF8', newline='') as dlt_data:
                    writer = csv.DictWriter(dlt_data, fieldnames=self.dlt_headers)
                    writer.writerow(data)

        return None

    def generateTrusteeInformation(self, producer, consumer, trustorDID, availableAssets, totalAssets, availableAssetLocation, totalAssetLocation, managedViolations, predictedViolations, executedViolations, nonPredictedViolations, consideredOffers, totalOffers, consideredOfferLocation, totalOfferLocation, managedOfferViolations, predictedOfferViolations, executedOfferViolations, nonPredictedOfferViolations):
        """ This method introduces Trustee information based on peerTrust equations and using the minimum
        values previously established """

        self.consumer = consumer
        trustee_selection = random.randint(0,3)
        offer_selection = random.randint(0,1)

        if not bool(self.list_additional_did_providers):
            "Adding the previous DID providers autogenerated to avoid the cold start"
            self.list_additional_did_offers = [[]] * self.max_previous_providers_DLT
            with open(self.dlt_file_name) as f:
                reader = csv.DictReader(f)
                pointer = 0
                for item in reader:
                    if item["trustorDID"] not in self.list_additional_did_providers and pointer < self.max_previous_interactions_DLT:
                        self.list_additional_did_providers.append(item["trustorDID"])
                    pointer+=1
            "Adding the previous DID offers autogenerated to avoid the cold start"
            with open(self.dlt_file_name) as f:
                reader = csv.DictReader(f)
                for item in reader:
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
        information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],3)

        if information not in self.historical:
            self.historical.append(information)

        data = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID,
                "userSatisfaction": information["trustor"]["direct_parameters"]["userSatisfaction"],
                "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                "currentInteractionNumber": information["currentInteractionNumber"]}

        with open(self.dlt_file_name, 'a', encoding='UTF8', newline='') as dlt_data:
            writer = csv.DictWriter(dlt_data, fieldnames=self.dlt_headers)
            writer.writerow(data)

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
            return 1

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
        list_interactions = self.find_by_column(self.dlt_file_name, 'trusteeDID', trusteeDID)

        """ Check the number of interactions whose offerID is the same"""
        for interaction in list_interactions:
            if interaction["offerDID"] == offerDID:
                counter+=1

        return counter

    def getTrusteeFeedbackNumberDLT(self, trusteeDID):
        """ This method counts the number of feedbacks registered in the DLT for a particular trustee """

        """ Check that the last recommender is not ourselves"""
        return len(self.find_by_column(self.dlt_file_name, 'trusteeDID', trusteeDID))

    def getTrustworthyRecommendationDLT(self, trustorDID, trusteeDID, trustworthy_recommender_list):
        """ This method returns from a trusted list those recommender that have interacted with the trustor """

        trustworthy_recommendations = []

        list_interactions = self.find_by_column(self.dlt_file_name, 'trusteeDID', trusteeDID)
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

        list_trustor_interactions = self.find_by_column(self.dlt_file_name, 'trustorDID', trustorDID)
        for interaction in list_trustor_interactions:
            trustee_interactions.append(interaction["trusteeDID"])

        return trustee_interactions

    def getTrusteeInteractions(self, trustorDID, trusteeDID):
        """ This methods return all entities that have interacted with a trustee and
        have published feedbacks in the DLT"""
        interactions = []

        list_interactions = self.find_by_column(self.dlt_file_name, 'trusteeDID', trusteeDID)
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
                similarity_summation = similarity_summation + self.similarity(previous_interaction)
        else:
            similarity_summation = 1
            summation_counter = 1

        trustee_similarity = self.similarity(trusteeDID)

        credibility = trustee_similarity/(similarity_summation/summation_counter)
        if credibility > 1.0:
            credibility = (similarity_summation/summation_counter)/trustee_similarity

        return round(credibility, 3)

    def similarity(self, trusteeDID):
        """ This method identifies stakeholders who have evaluated one or more entities in common with the trustor
        (trustee parameter) to compare their satisfaction values and determine how credible the trustor's
        (trustee parameter) satisfaction value is """

        common_interaction = []
        trustor_interaction_list = self.getTrustorInteractions(trusteeDID)

        for interaction in trustor_interaction_list:
            common_interaction = self.getTrusteeInteractions(trusteeDID, interaction)
            if common_interaction:
                """ Currently, only one common interaction is contemplated """
                break

        common_interaction_list = self.getTrustorInteractions(common_interaction[0])

        IJS_counter = 0
        global_satisfaction_summation = 0.0

        for interaction in trustor_interaction_list:
            if interaction in common_interaction_list:

                trustor_satisfaction_summation = self.consumer.readSatisfactionSummation(self.historical, trusteeDID, interaction)
                common_interaction_satisfaction_summation = self.consumer.readSatisfactionSummation(self.historical, common_interaction[0], interaction)
                satisfaction_summation = pow((trustor_satisfaction_summation - common_interaction_satisfaction_summation), 2)
                global_satisfaction_summation = global_satisfaction_summation + satisfaction_summation
                IJS_counter = IJS_counter + 1

        final_similarity = 1 - math.sqrt(global_satisfaction_summation/IJS_counter)

        return final_similarity


    def communityContextFactor(self, trustorDID, trusteeDID):
        """ Static list of recommender based on the domains registered in the DLT. TODO dynamic """

        global consumer

        trustworthy_recommender_list = self.list_additional_did_providers[:]

        total_registered_trustee_interaction = self.consumer.readTrusteeInteractions(self.historical, trusteeDID)

        number_trustee_feedbacks_DLT = self.getTrusteeFeedbackNumberDLT(trusteeDID)

        trustee_interaction_rate = number_trustee_feedbacks_DLT / total_registered_trustee_interaction

        if trustorDID in trustworthy_recommender_list:
            trustworthy_recommender_list.remove(trustorDID)

        trustworthy_recommendations = self.getTrustworthyRecommendationDLT(trustorDID, trusteeDID, trustworthy_recommender_list)

        summation_trustworthy_recommendations = 0.0

        for recommender in trustworthy_recommendations:
            last_value = self.getLastHistoryTrustValue(recommender, trusteeDID)
            last_credibility = self.getLastCredibility(trustorDID, recommender)
            summation_trustworthy_recommendations = summation_trustworthy_recommendations + (last_credibility*last_value)


        return round((trustee_interaction_rate+(summation_trustworthy_recommendations/len(trustworthy_recommendations)))/2,3)

    def communityContextFactor2(self, trustorDID, trusteeDID):
        """ This method displays the recommender on the screen and we have changed the parameters of the
        getLastCredibility, the only difference being  """

        global consumer

        trustworthy_recommender_list = self.list_additional_did_providers[:]

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
            print("\tCredibility of ",trustorDID," on the recommender (", recommender, ") --->", round(last_credibility, 3), "\n")
            summation_trustworthy_recommendations = summation_trustworthy_recommendations + (last_credibility*last_value)


        return round((trustee_interaction_rate+(summation_trustworthy_recommendations/len(trustworthy_recommendations)))/2,3)

    def transactionContextFactor(self, trustorDID, trusteeDID, offerDID):
        global consumer
        """ Currently, only one time-window is contemplated """

        total_registered_trustee_interaction = self.consumer.readTrusteeInteractions(self.historical, trusteeDID)
        total_registered_offer_interactions = self.consumer.readOfferTrusteeInteractions(self.historical, trusteeDID, offerDID)

        number_offer_trustee_feedbacks_DLT = self.getOfferFeedbackNumberDLT(trusteeDID, offerDID)
        number_trustee_feedbacks_DLT = self.getTrusteeFeedbackNumberDLT(trusteeDID)

        transactionFactor = (number_offer_trustee_feedbacks_DLT / total_registered_offer_interactions + number_trustee_feedbacks_DLT / total_registered_trustee_interaction)/2

        return round(transactionFactor, 3)


    def satisfaction(self, PSWeighting, OSWeighting, providerSatisfaction, offerSatisfaction):

        return PSWeighting*providerSatisfaction + OSWeighting*offerSatisfaction


    def providerSatisfaction(self, trustorDID, trusteeDID, providerReputation):
        """ This method computes the Provider's satisfaction considering its reputation and recommendations"""

        """ Only one recommendation is currently contemplated"""
        last_interaction = self.getRecommenderDLT(trustorDID, trusteeDID)

        provider_recommendation = self.getLastRecommendationValue(last_interaction)

        """ We obtain our last trust value on the recommender from our Kafka topic """
        last_trust_score_recommender = self.getLastHistoryTrustValue(trustorDID, last_interaction['trustorDID'])

        provider_satisfaction = round((providerReputation + provider_recommendation * last_trust_score_recommender)/2, 3)

        return provider_satisfaction

    def providerReputation(self, availableAssets, totalAssets, availableAssetLocation, totalAssetLocation, managedViolations, predictedViolations, executedViolations, nonPredictedViolations):
        """ Currently, only one time-window is contemplated"""

        assets_percentage = availableAssets / totalAssets

        assets_location_percentage = availableAssetLocation / totalAssetLocation

        managed_violations_percentage = managedViolations / predictedViolations

        violations_percentage = (executedViolations + nonPredictedViolations) / predictedViolations

        reputation = ((assets_percentage + assets_location_percentage + (2 * managed_violations_percentage) - (2 * violations_percentage)) + 2) / 6

        return reputation

    def offerSatisfaction(self, trustorDID, trusteeDID, offerDID, offerReputation):
        """ This method computes the Provider's satisfaction considering its reputation and recommendations"""

        """ Only one recommendation is currently contemplated"""
        last_interaction = self.getRecommenderOfferDLT(trustorDID, trusteeDID, offerDID)

        provider_recommendation = self.getLastOfferRecommendationValue(last_interaction)

        """ We obtain our last trust value on the offer from our Kafka topic"""
        last_trust_score_recommender = self.getLastOfferHistoryTrustValue(last_interaction['trustorDID'], trusteeDID, offerDID)

        provider_satisfaction = round((offerReputation + provider_recommendation * last_trust_score_recommender)/2, 3)

        return provider_satisfaction

    def offerReputation(self, consideredOffers, totalOffers, consideredOfferLocation, totalOfferLocation, managedOfferViolations, predictedOfferViolations, executedOfferViolations, nonPredictedOfferViolations):
        """ Currently, only one time-window is contemplated"""

        assets_percentage = consideredOffers / totalOffers

        assets_location_percentage = consideredOfferLocation / totalOfferLocation

        managed_violations_percentage = managedOfferViolations / predictedOfferViolations

        violations_percentage = (executedOfferViolations + nonPredictedOfferViolations) / predictedOfferViolations

        reputation = ((assets_percentage + assets_location_percentage + (2 * managed_violations_percentage) - (2 * violations_percentage)) + 2) / 6

        return reputation