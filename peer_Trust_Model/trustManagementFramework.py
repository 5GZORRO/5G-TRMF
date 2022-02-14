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
import threading
from threading import Lock
from dotenv import load_dotenv
from peerTrust import *
#from producer import *
from consumer import *
from trustInformationTemplate import *
from datetime import datetime
from multiprocessing import Process, Value, Manager
logging.basicConfig(level=logging.INFO)
import queue

from gevent import monkey
monkey.patch_all()

app = Flask(__name__)
api = Api(app)

producer = "Producer()"
consumer = Consumer()
peerTrust = PeerTrust()
data_lock = Lock()
trustInformationTemplate = TrustInformationTemplate()

client = MongoClient(host='mongodb-trmf', port=27017, username='5gzorro', password='password')
db = client.rptutorials
mongoDB = db.tutorial

dlt_headers = ["trustorDID","trusteeDID", "offerDID", "userSatisfaction","interactionNumber","totalInteractionNumber", "currentInteractionNumber"]
dlt_file_name = 'DLT.csv'

provider_list = []
considered_offer_list = []
consumer_instance = None

history = {}
trustor_acquired = False
trustorDID = ""
new_request = True

gather_time = 0
compute_time = 0
storage_time = 0
update_time = 0
satisfaction = 0
credibility = 0
TF = 0
CF = 0
offer_type = {}
product_offering = []
old_product_offering = []
statistic_catalog = []


def find_by_column(filename, column, value):
    """ This method discovers interactions registered in the DLT looking at one specific value"""
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

class initialise_offer_type(Resource):
    def post(self):
        global offer_type

        req = request.data.decode("utf-8")
        offer_type = json.loads(req)
        return 200


class start_data_collection(Resource):
    """ This method is responsible for creating the minimum information in the 5G-TRMF framework
    to avoid the cold start """

    def post(self):
        global trustor_acquired
        global gather_time
        global compute_time
        global storage_time
        global update_time
        global satisfaction
        global credibility
        global TF
        global CF
        global considered_offer_list
        global new_request

        gather_time, compute_time, storage_time, update_time, satisfaction, credibility, TF, CF = 0, 0, 0, 0, 0, 0, 0, 0
        trustor_acquired = False
        max_trust_score = 0
        max_trust_score_offerDID = ""

        time_file_name = 'tests/time.csv'
        time_headers = ["start_timestamp","end_timestamp","total_time", "total_without_cold", "cold_time", "gather_time", "compute_time",
                   "storage_time", "update_time","satisfaction","credibility","TF", "CF", "offers"]

        req = request.data.decode("utf-8")
        dict_product_offers = json.loads(req)
        initial_timestamp = time.time()

        """if not os.path.exists(dlt_file_name):
            with open(dlt_file_name, 'w', encoding='UTF8', newline='') as dlt_data:
                writer = csv.DictWriter(dlt_data, fieldnames=dlt_headers)
                writer.writeheader()"""

        trust_scores = []
        list_product_offers = {}
        considered_offer_list = []

        """ If it is not the first time that the 5G-TRMF is executed, it should retrieve information from the MongoDB
        in case of such an information is not already loaded in the historical parameter """

        for trustee in dict_product_offers:
            if trustor_acquired == False:
                trustorDID = dict_product_offers[trustee]
                list_product_offers['trustorDID'] = trustorDID
                trustor_acquired = True

            else:
                for offer in dict_product_offers[trustee]:
                    considered_offer_list.append({'trusteeDID': trustee, 'offerDID': offer})

                    """ In case of first time the 5G-TRMF is executed, we should retrieve information from MongoDB and
                    check if it is already or not in the historical"""
                    previous_interaction = mongoDB.find({'trustee.offerDID': offer})
                    offer_found = False
                    if previous_interaction is not None:
                        for interaction in previous_interaction:
                            del interaction['_id']
                            if interaction['trustor']['trusteeDID'] == trustee and \
                                    interaction['trustor']['offerDID'] == offer:
                                if interaction not in peerTrust.historical:
                                    peerTrust.historical.append(interaction)
                                offer_found = True

                    if not offer_found:
                        if trustee in list_product_offers:
                            list_product_offers[trustee].append(offer)
                        else:
                            list_product_offers[trustee] = [offer]

        """ Adding a set of minimum interactions between entities that compose the trust model """
        if len(list_product_offers)>1:
            minimum_data = peerTrust.minimumTrustValuesDLT(producer, consumer, trustorDID, list_product_offers)
            write_data_to_csv(dlt_file_name, minimum_data)

        trustor_acquired = False

        for trustee in dict_product_offers:
            if trustor_acquired == False:
                trustor_acquired = True

            else:
                for offer in dict_product_offers[trustee]:

                    if trustee+"$"+offer not in provider_list:
                        provider_list.append(trustee+"$"+offer)

                    """ we generated initial trust information to avoid the cold start"""
                    print("$$$$$$$$$$$$$$ Starting cold start procces on ",trustee, " $$$$$$$$$$$$$$\n")
                    for key, value in list_product_offers.items():
                        if offer in value:
                            peerTrust.generateHistoryTrustInformation(producer, consumer, trustorDID, trustee, offer, 3)
                            """ Establish two new interactions per each provider"""
                            peerTrust.setTrusteeInteractions(producer, consumer, trustee, 2)

                    #if trustee in list_product_offers:
                        #print("New Interactions")
                        #peerTrust.setTrusteeInteractions(producer, consumer, trustee, 2)

                    print("$$$$$$$$$$$$$$ Ending cold start procces on ",trustee, " $$$$$$$$$$$$$$\n")

                    """ Retrieve information from trustor and trustee """
                    data = {"trustorDID": trustorDID, "trusteeDID": trustee, "offerDID": offer, "topicName": trustorDID}

                    response = requests.post("http://localhost:5002/gather_information", data=json.dumps(data).encode("utf-8"))
                    response = json.loads(response.text)

                    if response["trust_value"] > max_trust_score:
                        max_trust_score = response["trust_value"]
                        max_trust_score_offerDID = response["trusteeDID"]["offerDID"]
                    trust_scores.append(response)

        "We are currently registering as a new interaction the offer with the highest trust score"
        for interaction in reversed(peerTrust.historical):
            if interaction["trust_value"] == max_trust_score and \
                    interaction["trustor"]["offerDID"] == max_trust_score_offerDID:
                data = {"trustorDID": trustorDID, "trusteeDID": interaction["trustor"]["trusteeDID"], "offerDID": max_trust_score_offerDID,
                        "userSatisfaction": interaction["trustor"]["direct_parameters"]["userSatisfaction"],
                        "interactionNumber": interaction["trustor"]["direct_parameters"]["interactionNumber"],
                        "totalInteractionNumber": interaction["trustor"]["direct_parameters"]["totalInteractionNumber"],
                        "currentInteractionNumber": interaction["currentInteractionNumber"]}

                write_only_row_to_csv(dlt_file_name, data)


        if not os.path.exists("tests"):
            os.makedirs("tests")

        if not os.path.exists(time_file_name):
            with open(time_file_name, 'w', encoding='UTF8', newline='') as time_data:
                writer = csv.DictWriter(time_data, fieldnames=time_headers)
                writer.writeheader()
                data = {"start_timestamp": initial_timestamp,"end_timestamp": time.time(), "total_time": time.time()-initial_timestamp,
                                "total_without_cold": gather_time+compute_time+storage_time+update_time,"cold_time":
                                    time.time()-initial_timestamp-gather_time-compute_time-storage_time-update_time,
                                "gather_time": gather_time, "compute_time": compute_time, "storage_time": storage_time,
                                "update_time": update_time, "satisfaction": satisfaction, "credibility": credibility,
                                "TF": TF, "CF": CF, "offers": 1000}
                writer.writerow(data)
        else:
            with open(time_file_name, 'a', encoding='UTF8', newline='') as time_data:
                writer = csv.DictWriter(time_data, fieldnames=time_headers)
                data = {"start_timestamp": initial_timestamp,"end_timestamp": time.time(), "total_time": time.time()-initial_timestamp,
                                "total_without_cold": gather_time+compute_time+storage_time+update_time,"cold_time":
                                    time.time()-initial_timestamp-gather_time-compute_time-storage_time-update_time,
                                "gather_time": gather_time, "compute_time": compute_time, "storage_time": storage_time,
                                "update_time": update_time, "satisfaction": satisfaction, "credibility": credibility,
                                "TF": TF, "CF": CF, "offers": 1000}
                writer.writerow(data)

        #client.close()
        #new_request = False
        return json.dumps(trust_scores)


class gather_information(Resource):
    def post(self):
        """ This method will retrieve information from the historical (MongoDB)+
        search for supplier/offer interactions in the simulated DLT to retrieve recommendations from
        other 5G-TRMFs. Currently there is no interaction with other 5G-TRMFs, we generate our
        internal information """

        global gather_time

        """ Retrieve parameters from post request"""
        req = request.data.decode("utf-8")
        parameter = json.loads(req)


        trustorDID = parameter["trustorDID"]
        trusteeDID = parameter["trusteeDID"]
        offerDID = parameter["offerDID"]
        topic_name = parameter["topicName"]

        print("$$$$$$$$$$$$$$ Starting data collection procces on ",trusteeDID, " $$$$$$$$$$$$$$\n")

        start_time = time.time()

        """Read last value registered in the historical"""
        last_trust_value = consumer.readLastTrustValueOffer(peerTrust.historical, trustorDID, trusteeDID, offerDID)

        print("\nThe latest trust interaction (history) of "+trustorDID+" with "+trusteeDID+" was:\n",last_trust_value, "\n")

        """Read interactions related to a Trustee"""
        interactions = self.getInteractionTrustee(trusteeDID)
        print("Public information from "+trusteeDID+" interactions registered in the DLT:\n", interactions, "\n")

        print("$$$$$$$$$$$$$$ Ending data collection procces on ",trusteeDID, " $$$$$$$$$$$$$$\n")

        gather_time = gather_time + (time.time()-start_time)
        ###print("Gather time: ", gather_time)

        """ Retrieve information from trustor and trustee """
        trust_information = []
        current_offer = {"trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID, "topicName": topic_name, "lastValue": last_trust_value, "trusteeInteractions": interactions}
        trust_information.append(current_offer)

        response = requests.post("http://localhost:5002/compute_trust_level", data=json.dumps(trust_information).encode("utf-8"))

        response = json.loads(response.text)


        return response

    def getInteractionTrustee(self, trusteeDID):
        """ This method retrieves all interactions related to a Trustee"""

        return list(find_by_column(dlt_file_name, "trustorDID", trusteeDID))

class compute_trust_level(Resource):
    def post(self):
        """This method retrieves the last value of the Trustor for a particular Trustee and the Trustee's interactions.
        It will then do the summation from its last computed value to the recent one by updating it trust value over
        the trustee """

        global compute_time
        global satisfaction
        global credibility
        global TF
        global CF
        global offer_type
        global considered_offer_list
        global availableAssets
        global totalAssets
        global availableAssetLocation
        global totalAssetLocation
        global consideredOffers
        global totalOffers
        global consideredOfferLocation
        global totalOfferLocation
        global new_request

        FORGETTING_FACTOR = 0.2

        """ Retrieve parameters from post request"""
        req = request.data.decode("utf-8")
        parameter = json.loads(req)

        for i in parameter:

            print("$$$$$$$$$$$$$$ Starting trust computation procces on ",i['trusteeDID'], " $$$$$$$$$$$$$$\n")

            start_time = time.time()

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

                    new_trustee_interaction = consumer.readLastTrustValues(peerTrust.historical, current_trustee, new_interaction['trusteeDID'], last_trustee_interaction_registered, new_interaction['currentInteractionNumber'])

                    for i in new_trustee_interaction:
                        print(new_interaction['trustorDID']," had an interaction with ", new_interaction['trusteeDID'],"\n")
                        print("\tS(u,i) ---> ", i['trusteeSatisfaction'])
                        new_satisfaction = new_satisfaction + i['trusteeSatisfaction']
                        start_credibility = time.time()
                        current_credibility = peerTrust.credibility(current_trustee, new_interaction['trusteeDID'])
                        print("\tCr(p(u,i)) ---> ", round(current_credibility, 4))
                        new_credibility = new_credibility + current_credibility
                        credibility = credibility + (time.time()-start_credibility)
                        start_TF = time.time()
                        current_transaction_factor = peerTrust.transactionContextFactor(current_trustee, new_interaction['trusteeDID'], new_interaction['offerDID'])
                        print("\tTF(u,i) ---> ", current_transaction_factor)
                        new_transaction_factor = new_transaction_factor + current_transaction_factor
                        TF = TF + (time.time()-start_TF)
                        start_CF = time.time()
                        #current_community_factor = peerTrust.communityContextFactor2(current_trustee, new_interaction['trusteeDID'])
                        current_community_factor = peerTrust.bad_mouthing_attack_resilience(trustorDID, current_trustee, new_interaction['trusteeDID'])
                        print("\tCF(u) ---> ", current_community_factor, "\n")
                        new_community_factor = new_community_factor + current_community_factor
                        CF = CF + (time.time()-start_CF)
                        counter_new_interactions += 1

                """ Updating the last value with the summation of new interactions"""
                new_satisfaction = round(self.recomputingTrustValue(last_satisfaction, (new_satisfaction/counter_new_interactions), FORGETTING_FACTOR), 4)
                new_credibility = round(self.recomputingTrustValue(last_credibility, (new_credibility/counter_new_interactions), FORGETTING_FACTOR), 4)
                new_transaction_factor = round(self.recomputingTrustValue(last_transaction_factor, (new_transaction_factor/counter_new_interactions), FORGETTING_FACTOR), 4)
                new_community_factor = round(self.recomputingTrustValue(last_community_factor, (new_community_factor/counter_new_interactions), FORGETTING_FACTOR), 4)

                information = trustInformationTemplate.trustTemplate()
                information["trustee"]["trusteeDID"] = current_trustee
                information["trustee"]["offerDID"] = offerDID
                information["trustee"]["trusteeSatisfaction"] = round(new_satisfaction, 4)
                information["trustor"]["trustorDID"] = trustorDID
                information["trustor"]["trusteeDID"] = current_trustee
                information["trustor"]["offerDID"] = offerDID
                information["trustor"]["credibility"] = round(new_credibility, 4)
                information["trustor"]["transactionFactor"] = round(new_transaction_factor, 4)
                information["trustor"]["communityFactor"] = round(new_community_factor, 4)
                #information["trustor"]["direct_parameters"]["userSatisfaction"] = round((round(random.uniform(0.75, 0.95), 3) + i["userSatisfaction"])/2, 3)
                direct_weighting = round(random.uniform(0.65, 0.7),2)
                information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
                information["trustor"]["indirect_parameters"]["recommendation_weighting"] = round(1-direct_weighting, 4)
                information["trustor"]["direct_parameters"]["interactionNumber"] = last_interaction_number+1
                information["trustor"]["direct_parameters"]["totalInteractionNumber"] = peerTrust.getLastTotalInteractionNumber(current_trustee)
                information["trustor"]["direct_parameters"]["feedbackNumber"] = peerTrust.getTrusteeFeedbackNumberDLT(current_trustee)
                information["trustor"]["direct_parameters"]["feedbackOfferNumber"] = peerTrust.getOfferFeedbackNumberDLT(current_trustee, offerDID)
                information["trust_value"] = round(direct_weighting*(new_satisfaction*new_credibility*new_transaction_factor)+(1-direct_weighting)*new_community_factor,4)
                information["currentInteractionNumber"] = peerTrust.getCurrentInteractionNumber(trustorDID)
                information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
                information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

                """UPDATE THE RECOMMENDATION TRUST HERE"""
                recommendation_list = consumer.readAllRecommenders(peerTrust.historical, trustorDID, current_trustee)
                new_recommendation_list = []

                for recommendation in recommendation_list:
                    satisfaction_deviation= last_satisfaction - new_satisfaction
                    new_recommendation_trust = self.recomputingRecommendationTrust(satisfaction_deviation, recommendation)
                    recommendation["recommendation_trust"] = new_recommendation_trust
                    new_recommendation_list.append(recommendation)

                if bool(new_recommendation_list):
                    information["trustor"]["indirect_parameters"]["recommendations"] = new_recommendation_list

                """ These values should be requested from other 5GZORRO components in future releases, in particular, 
                from the Calatog and SLA Breach Predictor"""
                for interaction in provider_list:
                    trustee = interaction.split("$")[0]
                    offer = interaction.split("$")[1]

                    start_satisfaction = time.time()

                    if current_trustee == trustee and offer == offerDID:

                        availableAssets = 0
                        totalAssets = 0
                        availableAssetLocation = 0
                        totalAssetLocation = 0
                        consideredOffers = 0
                        totalOffers= 0
                        consideredOfferLocation = 0
                        totalOfferLocation = 0

                        "5GBarcelona"
                        load_dotenv()
                        barcelona_address = os.getenv('5GBARCELONA_CATALOG_A')
                        response = requests.get(barcelona_address+"productCatalogManagement/v4/productOffering/did/"+offerDID)

                        "5TONIC"
                        #madrid_address = os.getenv('5TONIC_CATALOG_A')
                        #response = requests.get(madrid_address+"productCatalogManagement/v4/productOffering/did/")

                        response = json.loads(response.text)

                        place = response['place'][0]['href']
                        response = requests.get(place)
                        response = json.loads(response.text)
                        city = response['city']
                        country = response['country']
                        locality = response['locality']
                        x_coordinate = response['geographicLocation']['geometry'][0]['x']
                        y_coordinate = response['geographicLocation']['geometry'][0]['y']
                        z_coordinate = response['geographicLocation']['geometry'][0]['z']

                        self.productOfferingCatalog(trustee, offer, offer_type[offerDID], availableAssets, totalAssets,
                                                    availableAssetLocation, totalAssetLocation, totalOffers,
                                                             totalOfferLocation, city, country, locality, x_coordinate,
                                                             y_coordinate, z_coordinate, new_request)

                        #new_request = False

                        """Calculate the statistical parameters with respect to the considered offers"""
                        for offer in considered_offer_list:
                            if offer['trusteeDID'] == trustee:
                                consideredOffers+=1

                                "5GBarcelona"
                                load_dotenv()
                                barcelona_address = os.getenv('5GBARCELONA_CATALOG_A')
                                response = requests.get(barcelona_address+"productCatalogManagement/v4/productOffering/did/"+offer['offerDID'])

                                #madrid_address = os.getenv('5TONIC_CATALOG_A')
                                #response = requests.get(madrid_address+"productCatalogManagement/v4/productOffering/did/"+offer['offerDID'])

                                response = json.loads(response.text)

                                current_offer_place = response['place'][0]['href']
                                response = requests.get(current_offer_place)
                                response = json.loads(response.text)

                                "Check whether the POs have location information"
                                if "city" and "country" and "locality" in response:
                                    current_offer_city = response['city']
                                    current_offer_country = response['country']
                                    current_offer_locality = response['locality']
                                    current_offer_x_coordinate = response['geographicLocation']['geometry'][0]['x']
                                    current_offer_y_coordinate = response['geographicLocation']['geometry'][0]['y']
                                    current_offer_z_coordinate = response['geographicLocation']['geometry'][0]['z']

                                    if city == current_offer_city and country == current_offer_country and locality == \
                                            current_offer_locality and x_coordinate == current_offer_x_coordinate and \
                                            y_coordinate == current_offer_y_coordinate and z_coordinate \
                                            == current_offer_z_coordinate:
                                        consideredOfferLocation+=1
                                else:
                                    print("Product Offering without location information")

                        "These parameter should be collected from SLA Breach Predictor in the future"
                        managedViolations = random.randint(1,20)
                        predictedViolations = managedViolations + random.randint(0,5)
                        executedViolations = random.randint(0,6)
                        nonPredictedViolations = random.randint(0,2)

                        managedOfferViolations = random.randint(4,22)
                        predictedOfferViolations = managedOfferViolations + random.randint(0,8)
                        executedOfferViolations = random.randint(0,4)
                        nonPredictedOfferViolations = random.randint(0,3)

                        provider_reputation = peerTrust.providerReputation(availableAssets, totalAssets,
                                                                           availableAssetLocation, totalAssetLocation,
                                                                           managedViolations, predictedViolations,
                                                                           executedViolations, nonPredictedViolations)

                        information["trustor"]["direct_parameters"]["availableAssets"] = availableAssets
                        information["trustor"]["direct_parameters"]["totalAssets"] = totalAssets
                        information["trustor"]["direct_parameters"]["availableAssetLocation"] = availableAssetLocation
                        information["trustor"]["direct_parameters"]["totalAssetLocation"] = totalAssetLocation
                        information["trustor"]["direct_parameters"]["managedViolations"] = managedViolations
                        information["trustor"]["direct_parameters"]["predictedViolations"] = predictedOfferViolations
                        information["trustor"]["direct_parameters"]["executedViolations"] = executedViolations
                        information["trustor"]["direct_parameters"]["nonPredictedViolations"] = nonPredictedViolations

                        offer_reputation = peerTrust.offerReputation(consideredOffers, totalOffers, consideredOfferLocation,
                                                                     totalOfferLocation, managedOfferViolations,
                                                                     predictedOfferViolations, executedOfferViolations,
                                                                     nonPredictedOfferViolations)

                        information["trustor"]["direct_parameters"]["consideredOffers"] = consideredOffers
                        information["trustor"]["direct_parameters"]["totalOffers"] = totalOffers
                        information["trustor"]["direct_parameters"]["consideredOfferLocation"] = consideredOfferLocation
                        information["trustor"]["direct_parameters"]["totalOfferLocation"] = totalOfferLocation
                        information["trustor"]["direct_parameters"]["managedOfferViolations"] = managedOfferViolations
                        information["trustor"]["direct_parameters"]["predictedOfferViolations"] = predictedOfferViolations
                        information["trustor"]["direct_parameters"]["executedOfferViolations"] = executedOfferViolations
                        information["trustor"]["direct_parameters"]["nonPredictedOfferViolations"] = nonPredictedOfferViolations
                        satisfaction = satisfaction + (time.time()-start_satisfaction)

                start_satisfaction = time.time()
                provider_satisfaction = peerTrust.providerSatisfaction(trustorDID, current_trustee, provider_reputation)
                offer_satisfaction = peerTrust.offerSatisfaction(trustorDID, current_trustee, offerDID, offer_reputation)
                ps_weighting = round(random.uniform(0.4, 0.6),2)
                information["trustor"]["direct_parameters"]["providerSatisfaction"] = round(provider_satisfaction, 4)
                ps_weighting = round(random.uniform(0.4, 0.6),2)
                information["trustor"]["direct_parameters"]["PSWeighting"] = ps_weighting
                information["trustor"]["direct_parameters"]["offerSatisfaction"] = round(offer_satisfaction, 4)
                os_weighting = 1-ps_weighting
                information["trustor"]["direct_parameters"]["OSWeighting"] = os_weighting
                information["trustor"]["direct_parameters"]["providerReputation"] = round(provider_reputation, 4)
                information["trustor"]["direct_parameters"]["offerReputation"] = round(offer_reputation, 4)
                information["trustor"]["direct_parameters"]["userSatisfaction"] = round(peerTrust.satisfaction(ps_weighting, os_weighting, provider_satisfaction, offer_satisfaction), 4)
                satisfaction = satisfaction + (time.time()-start_satisfaction)

                response = {"trustorDID": trustorDID, "trusteeDID": {"trusteeDID": current_trustee, "offerDID": offerDID}, "trust_value": information["trust_value"], "currentInteractionNumber": information["currentInteractionNumber"],"evaluation_criteria": "Inter-domain", "initEvaluationPeriod": information["initEvaluationPeriod"],"endEvaluationPeriod": information["endEvaluationPeriod"]}

                print("\nNew Trust values after considering new interactions of "+current_trustee+":")
                print("\tα ---> ", direct_weighting)
                print("\tS(u,i) ---> ", new_satisfaction)
                print("\tCr(p(u,i)) ---> ", new_credibility)
                print("\tTF(u,i) ---> ", new_transaction_factor)
                print("\tβ ---> ", round(1-direct_weighting, 3))
                print("\tCF(u) ---> ", new_community_factor)

                print("\nPrevious Trust score of "+trustorDID+" on "+current_trustee+" --->", last_trust_value, " -- New trust score --->", information["trust_value"])

                peerTrust.historical.append(information)

                #data = {"trustorDID": trustorDID, "trusteeDID": current_trustee, "offerDID": offerDID,
                        #"userSatisfaction": information["trustor"]["direct_parameters"]["userSatisfaction"],
                        #"interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"],
                        #"totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                        #"currentInteractionNumber": information["currentInteractionNumber"]}

                #write_only_row_to_csv(dlt_file_name, data)

                compute_time = compute_time + (time.time()-start_time)
                ###print("Compute time:", compute_time)

                print("\n$$$$$$$$$$$$$$ Ending trust computation procces on ",i['trusteeDID'], " $$$$$$$$$$$$$$\n")

                requests.post("http://localhost:5002/store_trust_level", data=json.dumps(information).encode("utf-8"))

        return response

    def recomputingRecommendationTrust(self, satisfaction_deviation, recommendation_object):

        mean_deviation = (recommendation_object["average_recommendations"]/recommendation_object["recommendation_total_number"]) - recommendation_object["last_recommendation"]

        if satisfaction_deviation > 0 and mean_deviation > 0:
            new_recommendation_trust = (1 + satisfaction_deviation)*(mean_deviation/10) + recommendation_object["recommendation_trust"]
            if new_recommendation_trust > 1.0:
                new_recommendation_trust = 1.0
            return new_recommendation_trust
        elif satisfaction_deviation < 0 and mean_deviation < 0:
            new_recommendation_trust = (1 + abs(satisfaction_deviation))*(abs(mean_deviation)/10) + recommendation_object["recommendation_trust"]
            if new_recommendation_trust > 1.0:
                new_recommendation_trust = 1.0
            return new_recommendation_trust
        elif satisfaction_deviation < 0 and mean_deviation > 0:
            new_recommendation_trust = (1 - satisfaction_deviation)*(mean_deviation/10) - recommendation_object["recommendation_trust"]
            if new_recommendation_trust < 0:
                new_recommendation_trust = 0
            return new_recommendation_trust
        elif satisfaction_deviation > 0 and mean_deviation < 0:
            new_recommendation_trust = recommendation_object["recommendation_trust"] - (1 + satisfaction_deviation)*(abs(mean_deviation)/10)
            if new_recommendation_trust < 0:
                new_recommendation_trust = 0
            return new_recommendation_trust
        elif mean_deviation == 0:
            return recommendation_object["recommendation_trust"]


    def recomputingTrustValue(self, historical_value, new_value, forgetting_factor):

        return (1-forgetting_factor) * historical_value + forgetting_factor * new_value

    def productOfferingCatalog (self, trustee, offer, offer_type, current_availableAssets, current_totalAssets,
                                current_availableAssetLocation, current_totalAssetLocation, current_totalOffers,
                                current_totalOfferLocation, current_city_offer, current_country_offer,
                                current_locality_offer, current_x_coordinate_offer, current_y_coordinate_offer,
                                current_z_coordinate_offer, new_request):
        """ This method collects statistical parameters from the Catalog which will be used by the PeerTrust"""
        global availableAssets
        global totalAssets
        global availableAssetLocation
        global totalAssetLocation
        global totalOffers
        global totalOfferLocation
        global product_offering
        global old_product_offering
        global statistic_catalog

        "Avoiding request again the product offering objects for an SRSD request with multiple offers to be analyzed"
        if new_request:
            """Requesting all product offering objects"""
            "5GBarcelona"
            load_dotenv()
            barcelona_address = os.getenv('5GBARCELONA_CATALOG_A')
            response = requests.get(barcelona_address+"productCatalogManagement/v4/productOffering")

            "5TONIC"
            #madrid_address = os.getenv('5TONIC_CATALOG_A')
            #response = requests.get(madrid_address+"productCatalogManagement/v4/productOffering")

            product_offering = json.loads(response.text)

        if bool(product_offering) and product_offering != old_product_offering:

            for i in product_offering:
                href = i['productSpecification']['href']
                id_product_offering = i['id']
                product_offering_location = i['place'][0]['href']
                category = i['category'][0]['name']

                """ Obtaining the real product offer specification object"""
                response = requests.get(href)
                response = json.loads(response.text)
                did_provider = response['relatedParty'][0]['extendedInfo']

                """ Obtaining the location of the product offering object"""
                response = requests.get(product_offering_location)
                response = json.loads(response.text)

                "Check whether the POs have location information"
                new_object = {}
                location = ""

                if "city" and "country" and "locality" in response:
                    city = response['city']
                    country = response['country']
                    locality = response['locality']
                    x_coordinate = response['geographicLocation']['geometry'][0]['x']
                    y_coordinate = response['geographicLocation']['geometry'][0]['y']
                    z_coordinate = response['geographicLocation']['geometry'][0]['z']
                    location = str(x_coordinate)+"_"+str(y_coordinate)+"_"+str(z_coordinate)

                    new_object["provider"] = did_provider
                    new_object["n_resource"] = 1
                    new_object[location] = 1

                    if i['lifecycleStatus'] == 'Active':
                        new_object["active"] = 1
                        new_object["active"+"_"+location] = 1
                        new_object["active"+"_"+category.lower()] = 1
                        new_object["active"+"_"+category.lower()+"_"+location] = 1


                if bool(statistic_catalog):
                    statistic_catalog.append(new_object)
                elif bool(new_object):
                    for product_offer in statistic_catalog:
                        if product_offer["provider"] == did_provider:
                            product_offer["n_resource"] = product_offer["n_resource"] + new_object["n_resource"]
                            if location not in product_offer:
                                product_offer[location] = new_object[location]
                            else:
                                product_offer[location] = product_offer[location] + new_object[location]
                            if 'active' not in product_offer:
                                product_offer['active'] = new_object['active']
                                product_offer["active"+"_"+location] = new_object["active"+"_"+location]
                                product_offer["active"+"_"+category.lower()] = new_object["active"+"_"+category.lower()]
                                product_offer["active"+"_"+category.lower()+"_"+location] = new_object["active"+"_"+category.lower()+"_"+location]
                            else:
                                product_offer['active'] =  product_offer['Active'] + new_object["active"]
                                if 'active'+"_"+location not in product_offer:
                                    product_offer['active'+"_"+location] = new_object["active"+"_"+location]
                                else:
                                    product_offer["active"+"_"+location] = product_offer["active"+"_"+location] + new_object["active"+"_"+location]

                                if "active"+"_"+category.lower() not in product_offer:
                                    product_offer['active'+"_"+category.lower()] = new_object["active"+"_"+category.lower()]
                                else:
                                    product_offer["active"+"_"+category.lower()] = product_offer["active"+"_"+category.lower()] + new_object["active"+"_"+category.lower()]

                                if "active"+"_"+category.lower()+"_"+location not in product_offer:
                                    product_offer['active'+"_"+category.lower()+"_"+location] = new_object["active"+"_"+category.lower()+"_"+location]
                                else:
                                    product_offer["active"+"_"+category.lower()+"_"+location] = product_offer["active"+"_"+category.lower()+"_"+location] + new_object["active"+"_"+category.lower()+"_"+location]

                        else:
                            statistic_catalog.append(new_object)

            old_product_offering = product_offering

        for product_offer in statistic_catalog:
            if product_offer['provider'] == trustee:
                current_totalAssets = product_offer['n_resource']
                location = current_x_coordinate_offer+"_"+current_y_coordinate_offer+"_"+current_z_coordinate_offer
                current_totalAssetLocation = product_offer[location]
                current_availableAssets = product_offer['active']
                current_availableAssetLocation = product_offer['active'+"_"+location]
                current_totalOffers = product_offer['active'+"_"+offer_type.lower()]
                current_totalOfferLocation = product_offer['active'+"_"+offer_type.lower()+"_"+location]
                break

        "Updating global variables"
        availableAssets = current_availableAssets
        totalAssets = current_totalAssets
        availableAssetLocation = current_availableAssetLocation
        totalAssetLocation = current_totalAssetLocation
        totalOffers = current_totalOffers
        totalOfferLocation = current_totalOfferLocation

        """for i in product_offering:
            href = i['productSpecification']['href']
            id_product_offering = i['id']
            product_offering_location = i['place'][0]['href']
            category = i['category'][0]['name']

            #Obtaining the real product offer specification object
            response = requests.get(href)
            response = json.loads(response.text)
            did_provider = response['relatedParty'][0]['extendedInfo']

            #Obtaining the location of the product offering object
            response = requests.get(product_offering_location)
            response = json.loads(response.text)

            #Check whether the POs have location information
            if "city" and "country" and "locality" in response:
                city = response['city']
                country = response['country']
                locality = response['locality']
                x_coordinate = response['geographicLocation']['geometry'][0]['x']
                y_coordinate = response['geographicLocation']['geometry'][0]['y']
                z_coordinate = response['geographicLocation']['geometry'][0]['z']

                #Getting statictical parameters from the Catalog
                if did_provider == trustee:
                    current_totalAssets += 1
                    if city == current_city_offer and country == current_country_offer and locality == \
                            current_locality_offer and x_coordinate == current_x_coordinate_offer and y_coordinate == \
                            current_y_coordinate_offer and z_coordinate == current_z_coordinate_offer:
                        current_totalAssetLocation+=1

                    if i['lifecycleStatus'] == 'Active':
                        current_availableAssets+=1
                        if city == current_city_offer and country == current_country_offer and locality == \
                                current_locality_offer and x_coordinate == current_x_coordinate_offer and y_coordinate == \
                                current_y_coordinate_offer and z_coordinate == current_z_coordinate_offer:
                            current_availableAssetLocation+=1

                    if i['lifecycleStatus'] == 'Active' and category.lower() == type_offer.lower():
                        current_totalOffers+=1
                        if city == current_city_offer and country == current_country_offer and locality == \
                                current_locality_offer and x_coordinate == current_x_coordinate_offer and y_coordinate == \
                                current_y_coordinate_offer and z_coordinate == current_z_coordinate_offer:
                            current_totalOfferLocation+=1

                    #Obtaining the did product offer
                    #5GBarcelona"
                    #load_dotenv()
                    #barcelona_address = os.getenv('5GBARCELONA_CATALOG_A')
                    #response = requests.get(barcelona_address+"productCatalogManagement/v4/productOfferingStatus/"+id_product_offering)

                    #5TONIC"
                    #madrid_address = os.getenv('5TONIC_CATALOG_A')
                    #response = requests.get(madrid_address+"productCatalogManagement/v4/productOfferingStatus/"+id_product_offering)
                    #response = json.loads(response.text)
                    #did_offer = response['did']"""


class store_trust_level(Resource):
    def post(self):
        """ This method is employed to register direct trust in our internal database """
        global storage_time

        req = request.data.decode("utf-8")
        information = json.loads(req)

        print("$$$$$$$$$$$$$$ Starting trust information storage process $$$$$$$$$$$$$$\n")

        start_time = time.time()

        print("Registering a new trust interaction between two domains in the DLT\n")
        data = "{\"trustorDID\": \""+information["trustor"]["trustorDID"]+"\", \"trusteeDID\": \""+information["trustee"]["trusteeDID"]+"\", \"offerDID\": \""+information["trustee"]["offerDID"]+"\",\"userSatisfaction\": "+str(information["trustor"]["direct_parameters"]["userSatisfaction"])+", \"interactionNumber\": "+str(information["trustor"]["direct_parameters"]["interactionNumber"])+", \"totalInteractionNumber\": "+str(information["trustor"]["direct_parameters"]["totalInteractionNumber"])+", \"currentInteractionNumber\": "+str(information["currentInteractionNumber"])+"}\""
        print(data,"\n")
        print("Sending new trust information in the historical generated by the Trust Management Framework \n")
        print(information)
        print("\nStoring new trust information in our internal MongoDB database\n")

        print("\n$$$$$$$$$$$$$$ Ending trust information storage process $$$$$$$$$$$$$$\n")

        """list_trustee_interactions = {}
        query = mongoDB.find_one(information["trustee"]["trusteeDID"])
        if query is not None:
            list_trustee_interactions[information["trustee"]["trusteeDID"]].append(information)
            mongoDB.update_one(query, list_trustee_interactions)
        else:
            list_trustee_interactions[information["trustee"]["trusteeDID"]] = [information]
            mongoDB.insert_one(list_trustee_interactions)"""

        #mongoDB.insert_one(information)

        #pprint.pprint(mongoDB.find_one({"trustorDID": trustorDID}))
        #mongoDB.insert_many([tutorial2, tutorial1])
        #for doc in mongoDB.find():
        #pprint.pprint(doc)

        storage_time = storage_time + (time.time()-start_time)
        ###print("Storage time:", storage_time)

        return 200

class update_trust_level(Resource):
    def post(self):
        """ This method updates a trust score based on certain SLA events. More events need to be considered,
        it is only an initial version"""
        global offer_type

        req = request.data.decode("utf-8")
        information = json.loads(req)

        print("\n$$$$$$$$$$$$$$ Starting update trust level process process $$$$$$$$$$$$$$\n")

        #slaBreachPredictor_topic = information["SLABreachPredictor"]
        trustorDID = information["trustorDID"]
        trusteeDID = information["trusteeDID"]
        offerDID = information["offerDID"]

        " Equation for calculating new trust --> n_ts = n_ts+o_ts*((1-n_ts)/10) from security events"
        last_trust_score = consumer.readAllInformationTrustValue(peerTrust.historical, trustorDID, trusteeDID, offerDID)
        new_reward_and_punishment = self.reward_and_punishment_based_on_security(last_trust_score, offer_type)

        if new_reward_and_punishment >= 0.5:
            reward_and_punishment = new_reward_and_punishment - 0.5
            n_ts = float(last_trust_score ["trust_value"]) + reward_and_punishment * ((1-float(last_trust_score ["trust_value"]))/10)
            new_trust_score = min(n_ts, 1)
        elif new_reward_and_punishment < 0.5:
            "The lower value the higher punishment"
            reward_and_punishment = 0.5 - new_reward_and_punishment
            n_ts = float(last_trust_score ["trust_value"]) - reward_and_punishment * ((1-float(last_trust_score ["trust_value"]))/10)
            new_trust_score = max(0, n_ts)

        print("\t\tPrevious Trust Score", last_trust_score ["trust_value"], " --- Updated Trust Score --->", round(new_trust_score, 4), "\n")
        last_trust_score["trustor"]["reward_and_punishment"] = new_reward_and_punishment
        last_trust_score["trust_value"] = round(new_trust_score, 4)
        last_trust_score["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

        peerTrust.historical.append(last_trust_score)
        #mongoDB.insert_one(last_trust_score)

        #notifications = consumer.readSLANotification(peerTrust.historical, slaBreachPredictor_topic, trustorDID, trusteeDID, offerDID)

        #positive_notification = "was able to manage the SLA violation successfully"
        #negative_notification = "was not able to manage the SLA violation successfully"
        #first_range_probability = 0.25
        #second_range_probability = 0.50
        #third_range_probability = 0.75
        #fourth_range_probability = 1.0

        #new_trust_score = 0.0

        #for notification in notifications:
            #print("Notification received from the SLA Breach Predictor about", notification["breachPredictionNotification"],":\n")

            #current_notification = notification["notification"]
            #print("\t-", current_notification,"\n")
            #likehood = notification["breachPredictionNotification"]["value"]

            #last_trust_score = consumer.readAllInformationTrustValue(peerTrust.historical, trustorDID, trusteeDID, offerDID)

            #if positive_notification in current_notification:
                #if likehood <= first_range_probability:
                    #new_trust_score = last_trust_score["trust_value"] + last_trust_score["trust_value"]*0.075
                #elif likehood <= second_range_probability:
                    #new_trust_score = last_trust_score["trust_value"] + last_trust_score["trust_value"]*0.10
                #elif likehood <= third_range_probability:
                    #new_trust_score = last_trust_score["trust_value"] + last_trust_score["trust_value"]*0.125
                #elif likehood <= fourth_range_probability:
                    #new_trust_score = last_trust_score["trust_value"] + last_trust_score["trust_value"]*0.15
            #elif negative_notification in current_notification:
                #if likehood <= first_range_probability:
                    #new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.10
                #elif likehood <= second_range_probability:
                    #new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.125
                #elif likehood <= third_range_probability:
                    #new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.15
                #elif likehood <= fourth_range_probability:
                    #new_trust_score = last_trust_score["trust_value"] - last_trust_score["trust_value"]*0.175

            #if new_trust_score > 1.0:
                #new_trust_score = 1.0
            #elif new_trust_score < 0.0:
                #new_trust_score = 0.0

            #print("\t\tPrevious Trust Score", last_trust_score ["trust_value"], " --- Updated Trust Score --->", round(new_trust_score, 3), "\n")
            #last_trust_score["trust_value"] = round(new_trust_score, 3)
            #last_trust_score["endEvaluationPeriod"] = datetime.timestamp(datetime.now())
            
            #peerTrust.historical.append(last_trust_score)

        return 200

    def reward_and_punishment_based_on_security(self, last_trust_score, offer_type):

        "Sliding window weighting with respect to the forgetting factor"
        TOTAL_RW = 0.9
        NOW_RW = 1 - TOTAL_RW

        "Sliding window definition IN SECONDS"
        CURRENT_TIME_WINDOW = 1800

        "Dimensions weighting"
        #CONN_DIMENSION_WEIGHTING = 0.233
        #NOTICE_DIMENSION_WEIGHTING = 0.3
        #WEIRD_DIMENSION_WEIGHTING = 0.233
        #STATS_DIMENSION_WEIGHTING = 0.233


        total_reward_and_punishment = float(last_trust_score["trustor"]["reward_and_punishment"])
        offerDID = last_trust_score["trustor"]["offerDID"]
        current_offer_type = offer_type[offerDID]

        if current_offer_type == 'RAN' or current_offer_type == 'spectrum':
            current_reward_and_punishment = self.RAN_and_spectrum_reward_and_punishment_based_on_security(CURRENT_TIME_WINDOW, current_offer_type)
        elif current_offer_type == 'edge':
            current_reward_and_punishment = self.edge_reward_and_punishment_based_on_security(CURRENT_TIME_WINDOW, current_offer_type)
        elif current_offer_type == 'cloud':
            current_reward_and_punishment = self.cloud_reward_and_punishment_based_on_security(CURRENT_TIME_WINDOW, current_offer_type)
        elif current_offer_type == 'vnf' or current_offer_type == 'cnf':
            current_reward_and_punishment = self.vnf_cnf_reward_and_punishment_based_on_security(CURRENT_TIME_WINDOW, current_offer_type)

        #current_reward_and_punishment = CONN_DIMENSION_WEIGHTING * first_conn_value + NOTICE_DIMENSION_WEIGHTING * first_notice_value \
                          #+ WEIRD_DIMENSION_WEIGHTING * first_weird_value + STATS_DIMENSION_WEIGHTING * first_stats_value

        final_security_reward_and_punishment = TOTAL_RW * total_reward_and_punishment + NOW_RW * current_reward_and_punishment


        return final_security_reward_and_punishment

    def RAN_and_spectrum_reward_and_punishment_based_on_security(self, CURRENT_TIME_WINDOW, offer_type):
        "Global variable definition"
        global icmp_orig_pkts
        global tcp_orig_pkts
        global udp_orig_pkts

        "Dimensions weighting"
        CONN_DIMENSION_WEIGHTING = 0.4
        NOTICE_DIMENSION_WEIGHTING = 0.1
        WEIRD_DIMENSION_WEIGHTING = 0.1
        STATS_DIMENSION_WEIGHTING = 0.4

        first_conn_value = self.conn_log(CURRENT_TIME_WINDOW)
        first_notice_value = self.notice_log(CURRENT_TIME_WINDOW, offer_type)
        first_weird_value = self.weird_log(CURRENT_TIME_WINDOW, offer_type)
        first_stats_value = self.stats_log(CURRENT_TIME_WINDOW, icmp_orig_pkts, tcp_orig_pkts, udp_orig_pkts)

        return CONN_DIMENSION_WEIGHTING * first_conn_value + NOTICE_DIMENSION_WEIGHTING * first_notice_value \
               + WEIRD_DIMENSION_WEIGHTING * first_weird_value + STATS_DIMENSION_WEIGHTING * first_stats_value

    def edge_reward_and_punishment_based_on_security(self, CURRENT_TIME_WINDOW, offer_type):
        "Global variable definition"
        global icmp_orig_pkts
        global tcp_orig_pkts
        global udp_orig_pkts

        "Dimensions weighting"
        CONN_DIMENSION_WEIGHTING = 0.2
        NOTICE_DIMENSION_WEIGHTING = 0.35
        WEIRD_DIMENSION_WEIGHTING = 0.25
        STATS_DIMENSION_WEIGHTING = 0.2

        first_conn_value = self.conn_log(CURRENT_TIME_WINDOW)
        first_notice_value = self.notice_log(CURRENT_TIME_WINDOW, offer_type)
        first_weird_value = self.weird_log(CURRENT_TIME_WINDOW, offer_type)
        first_stats_value = self.stats_log(CURRENT_TIME_WINDOW, icmp_orig_pkts, tcp_orig_pkts, udp_orig_pkts)

        return CONN_DIMENSION_WEIGHTING * first_conn_value + NOTICE_DIMENSION_WEIGHTING * first_notice_value \
               + WEIRD_DIMENSION_WEIGHTING * first_weird_value + STATS_DIMENSION_WEIGHTING * first_stats_value

    def cloud_reward_and_punishment_based_on_security(self, CURRENT_TIME_WINDOW, offer_type):
        "Global variable definition"
        global icmp_orig_pkts
        global tcp_orig_pkts
        global udp_orig_pkts

        "Dimensions weighting"
        CONN_DIMENSION_WEIGHTING = 0.2
        NOTICE_DIMENSION_WEIGHTING = 0.35
        WEIRD_DIMENSION_WEIGHTING = 0.25
        STATS_DIMENSION_WEIGHTING = 0.2

        first_conn_value = self.conn_log(CURRENT_TIME_WINDOW)
        first_notice_value = self.notice_log(CURRENT_TIME_WINDOW, offer_type)
        first_weird_value = self.weird_log(CURRENT_TIME_WINDOW, offer_type)
        first_stats_value = self.stats_log(CURRENT_TIME_WINDOW, icmp_orig_pkts, tcp_orig_pkts, udp_orig_pkts)

        return CONN_DIMENSION_WEIGHTING * first_conn_value + NOTICE_DIMENSION_WEIGHTING * first_notice_value \
               + WEIRD_DIMENSION_WEIGHTING * first_weird_value + STATS_DIMENSION_WEIGHTING * first_stats_value

    def vnf_cnf_reward_and_punishment_based_on_security(self, CURRENT_TIME_WINDOW):
        "Global variable definition"
        global icmp_orig_pkts
        global tcp_orig_pkts
        global udp_orig_pkts

        "Dimensions weighting"
        CONN_DIMENSION_WEIGHTING = 0.233
        NOTICE_DIMENSION_WEIGHTING = 0.3
        WEIRD_DIMENSION_WEIGHTING = 0.233
        STATS_DIMENSION_WEIGHTING = 0.233

        first_conn_value = self.conn_log(CURRENT_TIME_WINDOW)
        first_notice_value = self.notice_log(CURRENT_TIME_WINDOW, offer_type)
        first_weird_value = self.weird_log(CURRENT_TIME_WINDOW, offer_type)
        first_stats_value = self.stats_log(CURRENT_TIME_WINDOW, icmp_orig_pkts, tcp_orig_pkts, udp_orig_pkts)

        return CONN_DIMENSION_WEIGHTING * first_conn_value + NOTICE_DIMENSION_WEIGHTING * first_notice_value \
               + WEIRD_DIMENSION_WEIGHTING * first_weird_value + STATS_DIMENSION_WEIGHTING * first_stats_value


    def conn_log(self, time_window):
        """ This function will compute the security level of an ongoing trust relationship between two operators from the
        percentage of network packages correctly sent """
        global icmp_orig_pkts
        global tcp_orig_pkts
        global udp_orig_pkts

        "Weight definition"
        ICMP = 0.3
        TCP = 0.3
        UDP = 0.4

        "Variable definition"
        icmp_orig_pkts = 0
        tcp_orig_pkts = 0
        udp_orig_pkts = 0
        icmp_resp_pkts = 0
        tcp_resp_pkts = 0
        udp_resp_pkts = 0

        timestamp = time.time()
        timestamp_limit = timestamp - time_window

        filebeat_index = "XXXXX"
        "Change the direction for the IP in which the service is listening"
        response = requests.get("elasticsearch:9200/"+filebeat_index)
        response = json.loads(response.text)

        for log in response:
            if log["ts"] >= timestamp_limit and log["id"] == filebeat_index:
                if log["proto"] == "icmp":
                    icmp_orig_pkts += icmp_orig_pkts + int(log["orig_pkts"])
                    icmp_resp_pkts += icmp_resp_pkts + int(log["resp_pkts"])
                elif log["proto"] == "tcp":
                    tcp_orig_pkts += tcp_orig_pkts + int(log["orig_pkts"])
                    tcp_resp_pkts += tcp_resp_pkts + int(log["resp_pkts"])
                elif log["proto"] == "udp":
                    udp_orig_pkts += udp_orig_pkts + int(log["orig_pkts"])
                    udp_resp_pkts += udp_orig_pkts + int(log["resp_pkts"])

        icmp_packet_hit_rate = icmp_resp_pkts/icmp_orig_pkts
        tcp_packet_hit_rate = tcp_resp_pkts/tcp_orig_pkts
        udp_packet_hit_rate = udp_resp_pkts/udp_orig_pkts

        final_conn_value = ICMP * icmp_packet_hit_rate + TCP * tcp_packet_hit_rate + UDP * udp_packet_hit_rate

        return final_conn_value

    def notice_log(self, time_window, offer_type):
        """ This function will compute the security level of an ongoing trust relationship between two operators from
         critical security events detected by the Zeek """

        "Generic label definition"
        TOO_MUCH_LOSS = "CaptureLoss::Too_Much_Loss"
        TOO_LITTLE_TRAFFIC = " CaptureLoss::Too_Little_Traffic"
        WEIRD_ACTIVITY = "Weird::Activity"
        PACKET_FILTER = "PacketFilter::Dropped_Packets"
        SOFTWARE_VULNERABLE = "Software::Vulnerable_Version"
        SQL_INJECTION_ATTACKER = "HTTP::SQL_Injection_Attacker"
        SQL_INJECTION_VICTIM = "HTTP::SQL_Injection_Victim"
        PASSWORD_GUESSING = "SSH::Password_Guessing"

        "Edge specific label definition"
        TOO_LONG_TO_COMPILE_FAILURE = "PacketFilter::Too_Long_To_Compile_Filter"
        ADDRESS_SCAN = "Scan::Address_Scan"
        PORT_SCAN = "Scan::Port_Scan"
        MALWARE_HASH = "TeamCymruMalwareHashRegistry::Match"
        TRACEROUTE = "Traceroute::Detected"
        BLOCKED_HOST = "SMTP::Blocklist_Blocked_Host"
        SUSPICIOUS_ORIGINATION = "SMTP::Suspicious_Origination"
        CERTIFICATE_EXPIRED = "SSL::Certificate_Expired"
        CERTIFICATE_NOT_VALID = "SSL::Certificate_Not_Valid_Yet"
        SSL_HEARTBEAT_ATTACK = "Heartbleed::SSL_Heartbeat_Attack"
        SSL_HEARTBEAT_ATTACK_SUCCESS = "Heartbleed::SSL_Heartbeat_Attack_Success"
        SSL_WEAK_KEY = "SSL::Weak_Key"
        SSL_OLD_VERSION = "SSL::Old_Version"
        SSL_WEAK_CIPHER = "SSL::Weak_Cipher"

        "Cloud specific label definition"
        SERVER_FOUND = "ProtocolDetector::Server_Found"
        BRUTEFORCING = "FTP::Bruteforcing"

        "VNF/CNF specific label definition"
        SENSITIVE_SIGNATURE = "Signatures::Sensitive_Signature"
        COMPILE_FAILURE_PACKET_FILTER = "PacketFilter::Compile_Failure"
        INSTALL_FAILURE = "PacketFilter::Install_Failure"
        CONTENT_GAP = "Conn::Content_Gap"

        "By default notice.log file is gathered after 15 minutes"
        TIME_MONITORING_EVENT = 900
        LAST_FIVE_TIME_MONITORING_EVENT = 4500

        "List of general labels"
        events_to_monitor = []
        events_to_monitor.append(TOO_MUCH_LOSS)
        events_to_monitor.append(TOO_LITTLE_TRAFFIC)
        events_to_monitor.append(WEIRD_ACTIVITY)
        events_to_monitor.append(PACKET_FILTER)
        events_to_monitor.append(SOFTWARE_VULNERABLE)
        events_to_monitor.append(SQL_INJECTION_ATTACKER)
        events_to_monitor.append(SQL_INJECTION_VICTIM)
        events_to_monitor.append(PASSWORD_GUESSING)

        "List of specific labels regarding the type of offer"
        edge_events_to_monitor = []
        edge_events_to_monitor.append(PORT_SCAN)
        edge_events_to_monitor.append(TOO_LONG_TO_COMPILE_FAILURE)
        edge_events_to_monitor.append(COMPILE_FAILURE_PACKET_FILTER)
        edge_events_to_monitor.append(INSTALL_FAILURE)
        edge_events_to_monitor.append(MALWARE_HASH)
        edge_events_to_monitor.append(TRACEROUTE)
        edge_events_to_monitor.append(ADDRESS_SCAN)
        edge_events_to_monitor.append(BRUTEFORCING)
        edge_events_to_monitor.append(BLOCKED_HOST)
        edge_events_to_monitor.append(SUSPICIOUS_ORIGINATION)
        edge_events_to_monitor.append(CERTIFICATE_EXPIRED)
        edge_events_to_monitor.append(CERTIFICATE_NOT_VALID)
        edge_events_to_monitor.append(SSL_HEARTBEAT_ATTACK)
        edge_events_to_monitor.append(SSL_HEARTBEAT_ATTACK_SUCCESS)
        edge_events_to_monitor.append(SSL_WEAK_KEY)
        edge_events_to_monitor.append(SSL_OLD_VERSION)
        edge_events_to_monitor.append(SSL_WEAK_CIPHER)

        cloud_events_to_monitor = []
        cloud_events_to_monitor.append(PORT_SCAN)
        cloud_events_to_monitor.append(COMPILE_FAILURE_PACKET_FILTER)
        cloud_events_to_monitor(INSTALL_FAILURE)
        cloud_events_to_monitor.append(SERVER_FOUND)
        cloud_events_to_monitor.append(MALWARE_HASH)
        cloud_events_to_monitor.append(TRACEROUTE)
        cloud_events_to_monitor.append(ADDRESS_SCAN)
        cloud_events_to_monitor.append(BRUTEFORCING)
        cloud_events_to_monitor.append(CERTIFICATE_EXPIRED)
        cloud_events_to_monitor.append(CERTIFICATE_NOT_VALID)
        cloud_events_to_monitor.append(SSL_HEARTBEAT_ATTACK)
        cloud_events_to_monitor.append(SSL_HEARTBEAT_ATTACK_SUCCESS)
        cloud_events_to_monitor.append(SSL_WEAK_KEY)
        cloud_events_to_monitor.append(SSL_OLD_VERSION)
        cloud_events_to_monitor.append(SSL_WEAK_CIPHER)

        vnf_cnf_events_to_monitor = []
        vnf_cnf_events_to_monitor.append(SENSITIVE_SIGNATURE)
        vnf_cnf_events_to_monitor.append(COMPILE_FAILURE_PACKET_FILTER)
        vnf_cnf_events_to_monitor.append(INSTALL_FAILURE)
        vnf_cnf_events_to_monitor.append(MALWARE_HASH)
        vnf_cnf_events_to_monitor.append(TRACEROUTE)
        vnf_cnf_events_to_monitor.append(ADDRESS_SCAN)
        vnf_cnf_events_to_monitor.append(PORT_SCAN)
        vnf_cnf_events_to_monitor.append(CONTENT_GAP)

        "Variable definition"
        actual_event_number = 0
        previous_monitoring_window_event_number = 0
        last_five_monitoring_window_event_number = 0

        timestamp = time.time()
        timestamp_limit = timestamp - time_window

        previous_event_monitoring_timestamp = timestamp - TIME_MONITORING_EVENT
        last_five_event_monitoring_timestamp = timestamp - LAST_FIVE_TIME_MONITORING_EVENT

        filebeat_index = "XXXXX"
        "Change the direction for the IP in which the service is listening"
        response = requests.get("elasticsearch:9200/"+filebeat_index)
        response = json.loads(response.text)

        for log in response:
            if log["note"] in events_to_monitor and log["ts"] >= timestamp_limit:
                actual_event_number += 1
            elif log["note"] in events_to_monitor and log["ts"] >= previous_event_monitoring_timestamp:
                previous_monitoring_window_event_number += 1
                last_five_monitoring_window_event_number += 1
            elif log["note"] in events_to_monitor and log["ts"] >= last_five_event_monitoring_timestamp:
                last_five_monitoring_window_event_number += 1
            elif offer_type == 'edge' and log["note"] in edge_events_to_monitor and \
                    log["ts"] >= timestamp_limit:
                actual_event_number += 1
            elif offer_type == 'edge' and log["note"] in edge_events_to_monitor and \
                    log["ts"] >= previous_event_monitoring_timestamp:
                previous_monitoring_window_event_number += 1
                last_five_monitoring_window_event_number += 1
            elif offer_type == 'edge' and log["note"] in edge_events_to_monitor and \
                    log["ts"] >= last_five_event_monitoring_timestamp:
                last_five_monitoring_window_event_number += 1
            elif offer_type == 'cloud' and log["note"] in cloud_events_to_monitor and \
                    log["ts"] >= timestamp_limit:
                actual_event_number += 1
            elif offer_type == 'cloud' and log["note"] in cloud_events_to_monitor and \
                    log["ts"] >= previous_event_monitoring_timestamp:
                previous_monitoring_window_event_number += 1
                last_five_monitoring_window_event_number += 1
            elif offer_type == 'cloud' and log["note"] in cloud_events_to_monitor and \
                    log["ts"] >= last_five_event_monitoring_timestamp:
                last_five_monitoring_window_event_number += 1
            elif offer_type == 'vnf' or offer_type == 'cnf' and log["note"] in vnf_cnf_events_to_monitor and \
                    log["ts"] >= timestamp_limit:
                actual_event_number += 1
            elif offer_type == 'vnf' or offer_type == 'cnf' and log["note"] in vnf_cnf_events_to_monitor and \
                    log["ts"] >= previous_event_monitoring_timestamp:
                previous_monitoring_window_event_number += 1
                last_five_monitoring_window_event_number += 1
            elif offer_type == 'vnf' or offer_type == 'cnf' and log["note"] in vnf_cnf_events_to_monitor and \
                    log["ts"] >= last_five_event_monitoring_timestamp:
                last_five_monitoring_window_event_number += 1


        final_notice_value = 1 - ((actual_event_number/(previous_monitoring_window_event_number + actual_event_number) +
                                   (actual_event_number / actual_event_number + ( last_five_monitoring_window_event_number / 5))) / 2)


        return final_notice_value

    def weird_log(self, time_window):
        """ This function will compute the security level of an ongoing trust relationship between two operators from
         weird events detected by the Zeek """

        "Label definition"
        DNS_UNMTATCHED_REPLY = "dns_unmatched_reply"
        ACTIVE_CONNECTION_REUSE = "active_connection_reuse"

        "List of labels"
        weird_event_list = []
        weird_event_list.apppend(DNS_UNMTATCHED_REPLY)
        weird_event_list.apppend(ACTIVE_CONNECTION_REUSE)

        "Variable definition"
        actual_weird_event_number = 0
        previous_monitoring_window_weird_event_number = 0
        last_five_monitoring_window_weird_event_number = 0

        "By default weird.log file is gathered after 15 minutes, VERIFY!"
        TIME_MONITORING_WEIRD_EVENT = 900
        LAST_FIVE_TIME_MONITORING_WEIRD_EVENT = 4500

        timestamp = time.time()
        timestamp_limit = timestamp - time_window

        previous_event_monitoring_timestamp = timestamp - TIME_MONITORING_WEIRD_EVENT
        last_five_event_monitoring_timestamp = timestamp - LAST_FIVE_TIME_MONITORING_WEIRD_EVENT

        filebeat_index = "XXXXX"
        "Change the direction for the IP in which the service is listening"
        response = requests.get("elasticsearch:9200/"+filebeat_index)
        response = json.loads(response.text)

        for log in response:
            if log["name"] in weird_event_list and log["ts"] >= timestamp_limit:
                actual_weird_event_number += 1
            elif log["name"] in weird_event_list and log["ts"] >= previous_event_monitoring_timestamp:
                previous_monitoring_window_weird_event_number += 1
                last_five_monitoring_window_weird_event_number += 1
            elif log["name"] in weird_event_list and log["ts"] >= last_five_event_monitoring_timestamp:
                last_five_monitoring_window_weird_event_number += 1

        final_weird_value = 1 - ((actual_weird_event_number/(previous_monitoring_window_weird_event_number + actual_weird_event_number) +
                                   (actual_weird_event_number / actual_weird_event_number + (last_five_monitoring_window_weird_event_number / 5))) / 2)

        return final_weird_value

    def stats_log(self, time_window, icmp_sent_pkts, tcp_sent_pkts, udp_sent_pkts):
        """ This function will compute the security level of an ongoing trust relationship between two operators from the
        percentage of network packages sent and the packets finally analyzed by Zeek"""

        "Global variable definition"
        global icmp_orig_pkts
        global tcp_orig_pkts
        global udp_orig_pkts

        "Weight definition"
        ICMP = 0.3
        TCP = 0.3
        UDP = 0.4

        "Variable definition"
        icmp_orig_pkts = icmp_sent_pkts
        tcp_orig_pkts = tcp_sent_pkts
        udp_orig_pkts = udp_sent_pkts
        icmp_pkts_analyzed_by_zeek = 0
        tcp_pkts_analyzed_by_zeek = 0
        udp_pkts_analyzed_by_zeek = 0

        timestamp = time.time()
        timestamp_limit = timestamp - time_window

        filebeat_index = "XXXXX"
        "Change the direction for the IP in which the service is listening"
        response = requests.get("elasticsearch:9200/"+filebeat_index)
        response = json.loads(response.text)

        for log in response:
            if log["ts"] >= timestamp_limit and log["id"] == filebeat_index:
                if log["proto"] == "icmp":
                    icmp_orig_pkts += icmp_orig_pkts + int(log["orig_pkts"])
                    icmp_pkts_analyzed_by_zeek += icmp_pkts_analyzed_by_zeek + int(log["resp_pkts"])
                elif log["proto"] == "tcp":
                    tcp_orig_pkts += tcp_orig_pkts + int(log["orig_pkts"])
                    tcp_pkts_analyzed_by_zeek += tcp_pkts_analyzed_by_zeek + int(log["resp_pkts"])
                elif log["proto"] == "udp":
                    udp_orig_pkts += udp_orig_pkts + int(log["orig_pkts"])
                    udp_pkts_analyzed_by_zeek += udp_pkts_analyzed_by_zeek + int(log["resp_pkts"])

        icmp_packet_rate_analyzed_by_zeek = icmp_pkts_analyzed_by_zeek/icmp_orig_pkts
        tcp_packet_rate_analyzed_by_zeek = tcp_pkts_analyzed_by_zeek/tcp_orig_pkts
        udp_packet_rate_analyzed_by_zeek = udp_pkts_analyzed_by_zeek/udp_orig_pkts

        final_stats_value = ICMP * icmp_packet_rate_analyzed_by_zeek + TCP * tcp_packet_rate_analyzed_by_zeek + UDP * \
                            udp_packet_rate_analyzed_by_zeek

        return final_stats_value


def launch_server_REST(port):
    api.add_resource(initialise_offer_type, '/initialise_offer_type')
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