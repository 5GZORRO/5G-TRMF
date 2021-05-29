import json
import sys
import logging
from flask import Flask, request
from flask_restful import Resource, Api
from gevent.pywsgi import WSGIServer
import random
import time
import ast
import math
import consumer
import requests
import os.path


from producer import *
from trustInformationTemplate import *
from peerTrust import *
from datetime import datetime
#logging.basicConfig(level=logging.INFO)

class PeerTrust():

    def minimumTrustTemplate(self, trustorDID, trusteeDID, offerDID):
        trustInformationTemplate = TrustInformationTemplate()
        information = trustInformationTemplate.trustTemplate()
        """ !!!! Cambiar por el último número registrado en la DLT para el Trustor¡¡¡¡"""
        #interaction_number = 1
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

        time.sleep(3)

        return information

    def minimumTrustValuesDLT(self, producer):
        user_satisfaction_1 = round(random.uniform(0.8, 0.9),3)
        user_satisfaction_2 = round(random.uniform(0.6, 0.8),3)
        user_satisfaction_3 = round(random.uniform(0.75, 0.8),3)
        user_satisfaction_4 = round(random.uniform(0.6, 0.75),3)
        user_satisfaction_5 = round(random.uniform(0.85, 0.95),3)
        user_satisfaction_6 = round(random.uniform(0.85, 0.95),3)
        user_satisfaction_7 = round(random.uniform(0.80, 0.99),3)
        user_satisfaction_8 = round(random.uniform(0.80, 0.95),3)
        user_satisfaction_9 = round(random.uniform(0.85, 0.99),3)
        user_satisfaction_10 = round(random.uniform(0.83, 0.92),3)
        user_satisfaction_11 = round(random.uniform(0.86, 0.91),3)
        user_satisfaction_12 = round(random.uniform(0.76, 0.95),3)


        data = [{"trustorDID": "did:5gzorro:domain5-RAN", "trusteeDID": "did:5gzorro:domain6-RAN", "offerDID": "did:5gzorro:domain6-RAN-1",
                 "userSatisfaction": user_satisfaction_1, "interactionNumber": 1, "totalInteractionNumber": 6, "currentInteractionNumber": 8},
                {"trustorDID": "did:5gzorro:domain5-RAN", "trusteeDID": "did:5gzorro:domain8-RAN", "offerDID": "did:5gzorro:domain8-RAN-2",
                 "userSatisfaction": user_satisfaction_2, "interactionNumber": 1, "totalInteractionNumber": 7, "currentInteractionNumber": 9},
                {"trustorDID": "did:5gzorro:domain5-RAN", "trusteeDID": "did:5gzorro:domain1-RAN", "offerDID": "did:5gzorro:domain1-RAN-2",
                 "userSatisfaction": user_satisfaction_3, "interactionNumber": 1, "totalInteractionNumber": 1, "currentInteractionNumber": 10},
                {"trustorDID": "did:5gzorro:domain6-RAN", "trusteeDID": "did:5gzorro:domain7-RAN", "offerDID": "did:5gzorro:domain7-RAN-1",
                 "userSatisfaction": user_satisfaction_4, "interactionNumber": 1, "totalInteractionNumber": 10, "currentInteractionNumber": 7},
                {"trustorDID": "did:5gzorro:domain6-RAN", "trusteeDID": "did:5gzorro:domain8-RAN", "offerDID": "did:5gzorro:domain8-RAN-1",
                 "userSatisfaction": user_satisfaction_5, "interactionNumber": 1, "totalInteractionNumber": 7, "currentInteractionNumber": 8},
                {"trustorDID": "did:5gzorro:domain6-RAN", "trusteeDID": "did:5gzorro:domain2-RAN", "offerDID": "did:5gzorro:domain2-RAN-1",
                 "userSatisfaction": user_satisfaction_6, "interactionNumber": 1, "totalInteractionNumber": 1, "currentInteractionNumber": 9},
                {"trustorDID": "did:5gzorro:domain7-RAN", "trusteeDID": "did:5gzorro:domain5-RAN", "offerDID": "did:5gzorro:domain5-RAN-2",
                 "userSatisfaction": user_satisfaction_7, "interactionNumber": 1, "totalInteractionNumber": 10, "currentInteractionNumber": 11},
                {"trustorDID": "did:5gzorro:domain7-RAN", "trusteeDID": "did:5gzorro:domain6-RAN", "offerDID": "did:5gzorro:domain6-RAN-2",
                 "userSatisfaction": user_satisfaction_8, "interactionNumber": 1, "totalInteractionNumber": 9, "currentInteractionNumber": 12},
                {"trustorDID": "did:5gzorro:domain7-RAN", "trusteeDID": "did:5gzorro:domain3-RAN", "offerDID": "did:5gzorro:domain3-RAN-2",
                 "userSatisfaction": user_satisfaction_9, "interactionNumber": 1, "totalInteractionNumber": 1, "currentInteractionNumber": 13},
                {"trustorDID": "did:5gzorro:domain8-RAN", "trusteeDID": "did:5gzorro:domain7-RAN", "offerDID": "did:5gzorro:domain7-RAN-2",
                 "userSatisfaction": user_satisfaction_10, "interactionNumber": 1, "totalInteractionNumber": 13, "currentInteractionNumber": 8},
                {"trustorDID": "did:5gzorro:domain8-RAN", "trusteeDID": "did:5gzorro:domain5-RAN", "offerDID": "did:5gzorro:domain5-RAN-1",
                 "userSatisfaction": user_satisfaction_11, "interactionNumber": 1, "totalInteractionNumber": 10, "currentInteractionNumber": 9},
                {"trustorDID": "did:5gzorro:domain8-RAN", "trusteeDID": "did:5gzorro:domain4-RAN", "offerDID": "did:5gzorro:domain4-RAN-1",
                 "userSatisfaction": user_satisfaction_12, "interactionNumber": 1, "totalInteractionNumber": 1, "currentInteractionNumber": 10}
                ]
        string_data = "{\"trustorDID\": \"did:5gzorro:domain5-RAN\", \"trusteeDID\": \"did:5gzorro:domain6-RAN\", \"offerDID\": \"did:5gzorro:domain6-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_1)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 6, \"currentInteractionNumber\": 8}\n"+"{\"trustorDID\": \"did:5gzorro:domain5-RAN\", \"trusteeDID\": \"did:5gzorro:domain8-RAN\", \"offerDID\": \"did:5gzorro:domain8-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_2)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 7, \"currentInteractionNumber\": 9}\n"+"{\"trustorDID\": \"did:5gzorro:domain5-RAN\", \"trusteeDID\": \"did:5gzorro:domain1-RAN\", \"offerDID\": \"did:5gzorro:domain1-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_3)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 1, \"currentInteractionNumber\": 10}\n"+"{\"trustorDID\": \"did:5gzorro:domain6-RAN\", \"trusteeDID\": \"did:5gzorro:domain7-RAN\", \"offerDID\": \"did:5gzorro:domain7-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_4)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 10, \"currentInteractionNumber\": 7}\n"+"{\"trustorDID\": \"did:5gzorro:domain6-RAN\", \"trusteeDID\": \"did:5gzorro:domain8-RAN\", \"offerDID\": \"did:5gzorro:domain8-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_5)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 7, \"currentInteractionNumber\": 8}\n"+"{\"trustorDID\": \"did:5gzorro:domain6-RAN\", \"trusteeDID\": \"did:5gzorro:domain2-RAN\", \"offerDID\": \"did:5gzorro:domain2-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_6)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 1, \"currentInteractionNumber\": 9}\n"+"{\"trustorDID\": \"did:5gzorro:domain7-RAN\", \"trusteeDID\": \"did:5gzorro:domain5-RAN\", \"offerDID\": \"did:5gzorro:domain5-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_7)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 10, \"currentInteractionNumber\": 11}\n"+"{\"trustorDID\": \"did:5gzorro:domain7-RAN\", \"trusteeDID\": \"did:5gzorro:domain6-RAN\", \"offerDID\": \"did:5gzorro:domain6-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_8)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 9, \"currentInteractionNumber\": 12}\n"+"{\"trustorDID\": \"did:5gzorro:domain7-RAN\", \"trusteeDID\": \"did:5gzorro:domain3-RAN\", \"offerDID\": \"did:5gzorro:domain3-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_9)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 1, \"currentInteractionNumber\": 13}\n"+"{\"trustorDID\": \"did:5gzorro:domain8-RAN\", \"trusteeDID\": \"did:5gzorro:domain7-RAN\", \"offerDID\": \"did:5gzorro:domain7-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_10)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 13, \"currentInteractionNumber\": 8}\n"+"{\"trustorDID\": \"did:5gzorro:domain8-RAN\", \"trusteeDID\": \"did:5gzorro:domain5-RAN\", \"offerDID\": \"did:5gzorro:domain5-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_11)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 10, \"currentInteractionNumber\": 9}\n"+"{\"trustorDID\": \"did:5gzorro:domain8-RAN\", \"trusteeDID\": \"did:5gzorro:domain4-RAN\", \"offerDID\": \"did:5gzorro:domain4-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_12)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 1, \"currentInteractionNumber\": 10}"

        for interaction in data:
            trust_informartion = self.minimumTrustTemplate(interaction["trustorDID"], interaction["trusteeDID"], interaction["offerDID"])
            trust_informartion["trustor"]["direct_parameters"]["userSatisfaction"] = interaction["userSatisfaction"]
            trust_informartion["trustor"]["direct_parameters"]["interactionNumber"] = interaction["interactionNumber"]
            trust_informartion["trustor"]["direct_parameters"]["totalInteractionNumber"] = interaction["totalInteractionNumber"]
            trust_informartion["currentInteractionNumber"] = interaction["currentInteractionNumber"]

            registered_offer_interaction = interaction["trusteeDID"].split(":")[2] + "-" + interaction["offerDID"].split(":")[2]
            registered_interaction = interaction["trusteeDID"].split(":")[2]
            producer.createTopic(registered_interaction)

            provider_topic_name = interaction["trustorDID"].split(":")[2] + "-" + interaction["trusteeDID"].split(":")[2]
            result = producer.createTopic(provider_topic_name)
            full_topic_name = interaction["trustorDID"].split(":")[2] + "-" + interaction["trusteeDID"].split(":")[2] + "-" + interaction["offerDID"].split(":")[2]
            result = producer.createTopic(full_topic_name)
            if result == 1:
                message = {"interaction": interaction["trustorDID"]+" has interacted with "+interaction["trusteeDID"]}
                producer.sendMessage(registered_interaction, registered_offer_interaction, message)
                producer.sendMessage(provider_topic_name, provider_topic_name, trust_informartion)
                producer.sendMessage(full_topic_name, full_topic_name, trust_informartion)

                #previous_interaction_not_published = random.randint(0, 2)
                #for i in range(0,previous_interaction_not_published):
                    #message = {"interaction": interaction["trustorDID"]+" has interacted with "+interaction["trusteeDID"]}
                    #producer.sendMessage(registered_interaction, registered_offer_interaction, message)

        if not os.path.exists('DLT.json'):
            with open('DLT.json', 'a') as json_file:
                json.dump(string_data, json_file)
                json_file.close()

    def getLastTotalInteractionNumber(self, trusteeDID):
        """ Retrieve all interactions related to a Trustee"""

        last_total_iteraction_number = 1
        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))

                for i in new_interaction_list:
                    if i["trustorDID"] == trusteeDID and i["currentInteractionNumber"] > last_total_iteraction_number:
                        #print("PREVIOUS INTERACTION ---->", last_total_iteraction_number, trusteeDID)
                        last_total_iteraction_number = i["currentInteractionNumber"]
                    elif i["trusteeDID"] == trusteeDID and i["totalInteractionNumber"] > last_total_iteraction_number:
                        last_total_iteraction_number = i["totalInteractionNumber"]

        return last_total_iteraction_number

    def getCurrentInteractionNumber(self, trustorDID):
        
        current_iteraction_number = 0

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))

                for i in new_interaction_list:
                    if i["trustorDID"] == trustorDID and i["currentInteractionNumber"] > current_iteraction_number:
                        current_iteraction_number = i["currentInteractionNumber"]
                        #print("currentInteractionNumber INTERACTION ---->", current_iteraction_number, trustorDID)
                    elif i["trusteeDID"] == trustorDID and i["totalInteractionNumber"] > current_iteraction_number:
                        current_iteraction_number = i["totalInteractionNumber"]


        return current_iteraction_number+1

    def getInteractionNumber(self, trustorDID, trusteeDID):
        
        iteraction_number = 0

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))

                for i in new_interaction_list:
                    if i["trustorDID"] == trustorDID and i["trusteeDID"] == trusteeDID and i["interactionNumber"] > iteraction_number:
                        iteraction_number = i["interactionNumber"]
                        #print("InteractionNumber INTERACTION ---->", iteraction_number, "---", trustorDID, "---", trusteeDID)

        return iteraction_number+1


    def getRecommenderDLT(self, trustorDID, trusteeDID):
        """ This method recovers a recommender, who is reliable for us, that has recently interacted with a trustee.
        Return the last interaction in order to request the last trust value"""

        last_interaction = ""

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))

                #print(new_interaction_list)

                last_interaction = {}
                last_registered_interaction = True
                """ Starting from the end to identify the last recommender"""
                for interaction in reversed(new_interaction_list):
                    """ Check that the last recommender is not ourselves"""
                    if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID:
                        "Store the most recent interaction with the Trustee"
                        if last_registered_interaction:
                            last_interaction = interaction
                            last_registered_interaction = False
                        """Check if the Trustor is reliable for us"""
                        for trustworthy_candidate in reversed(new_interaction_list):
                            if trustworthy_candidate['trustorDID'] == trustorDID and trustworthy_candidate['trusteeDID'] == interaction['trustorDID']:
                                file.close()
                                #print("RECOMMENDER Trustowrthy ---> ", interaction['trustorDID'], "---->",trustorDID, "--->",trusteeDID)
                                return interaction
                        #json_file.close()
                        #return last_interaction

        file.close()
        return last_interaction

    def getRecommenderOfferDLT(self, trustorDID, trusteeDID, offerDID):
        """ This method recovers a recommender, who is reliable for us, that has recently interacted with a trustee.
        Return the last interaction in order to request the last trus value"""

        last_interaction = ""

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))

                #print(new_interaction_list)

                last_interaction = {}
                last_registered_interaction = True
                """ Starting from the end to identify the last recommender"""
                for interaction in reversed(new_interaction_list):
                    """ Check that the last recommender is not ourselves"""
                    if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID and interaction['offerDID'] == offerDID:
                        "Store the most recent interaction with the Trustee"
                        if last_registered_interaction:
                            last_interaction = interaction
                            last_registered_interaction = False
                        """Check if the Trustor is reliable for us"""
                        for trustworthy_candidate in reversed(new_interaction_list):
                            if trustworthy_candidate['trustorDID'] == trustorDID and trustworthy_candidate['trusteeDID'] == interaction['trustorDID'] and trustworthy_candidate['offerDID'] == offerDID:
                                file.close()
                                return interaction
                        #json_file.close()
                        #return last_interaction

        file.close()
        return last_interaction

    def getLastRecommendationValue(self, last_interaction):
        """This methods goes to a recommender kafka channel to request a trust score"""

        last_truste_value = 0.0

        trustor = last_interaction['trustorDID'].split(":")[2]
        trustee = last_interaction['trusteeDID'].split(":")[2]

        recommender_topic = trustor+"-"+trustee

        trust_information = consumer.readLastTrustValue(recommender_topic)
        #print("Provider-Recommender Topic ----> ", recommender_topic, "\n",trust_information)
        print("RECOMMENDER TRUST VALUE ----->", trust_information["trust_value"])
        last_truste_value = trust_information["trust_value"]

        #if not trust_information:
            #print("RECOMMENDER TOPIC DOES NOT EXIT ----->", trust_information)
            #self.generateHistoryTrustInformation(last_interaction['trustorDID'], last_interaction['trusteeDID'], last_interaction['offerDID'], recommender_topic, 1)
            #trust_information = consumer.read(recommender_topic)
            #print("RECOMMENDER TRUST VALUE ----->", trust_information["trust_value"])
            #last_truste_value = trust_information["trust_value"]

        return last_truste_value

    def getLastOfferRecommendationValue(self, last_interaction):
        """This methods goes to a recommender kafka channel to request a trust score"""

        last_truste_value = 0.0

        trustor = last_interaction['trustorDID'].split(":")[2]
        trustee = last_interaction['trusteeDID'].split(":")[2]
        offer = last_interaction['offerDID'].split(":")[2]
        recommender_topic = trustor+"-"+trustee+"-"+offer

        trust_information = consumer.readLastTrustValue(recommender_topic)
        #print("Offer-Recommender ----> ", recommender_topic, "\n",trust_information)
        print("RECOMMENDER Offer TRUST VALUE ----->", trust_information["trust_value"])
        last_truste_value = trust_information["trust_value"]

        #if not trust_information:
        #print("RECOMMENDER TOPIC DOES NOT EXIT ----->", trust_information)
        #self.generateHistoryTrustInformation(last_interaction['trustorDID'], last_interaction['trusteeDID'], last_interaction['offerDID'], recommender_topic, 1)
        #trust_information = consumer.read(recommender_topic)
        #print("RECOMMENDER TRUST VALUE ----->", trust_information["trust_value"])
        #last_truste_value = trust_information["trust_value"]

        return last_truste_value

    """ This method generates information that will be sent to trustor Kafka Topic"""
    def generateHistoryTrustInformation(self, producer, trustorDID, trusteeDID, offerDID, provider_topic_name, full_topic_name, topic_trusteeDID, registered_offer_interaction, previous_interaction_number):

        if previous_interaction_number != 0:
            trustInformationTemplate = TrustInformationTemplate()
            information = trustInformationTemplate.trustTemplate()
            """ !!!! Cambiar por el último número registrado en la DLT para el Trustor¡¡¡¡"""
            #interaction_number = 1
            """ Adding information related to the specific request """
            information["trustee"]["trusteeDID"] = trusteeDID
            information["trustee"]["offerDID"] = offerDID
            information["trustee"]["trusteeSatisfaction"] = round(random.uniform(0.8, 0.95),3)
            information["trustor"]["trustorDID"] = trustorDID
            information["trustor"]["trusteeDID"] = trusteeDID
            information["trustor"]["offerDID"] = offerDID
            information["trustor"]["credibility"] = 0.913
            information["trustor"]["transactionFactor"] = 0.856
            information["trustor"]["communityFactor"] = 0.865
            information["trustor"]["direct_parameters"]["userSatisfaction"] = 0.801
            direct_weighting = round(random.uniform(0.6, 0.7),2)
            information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
            information["trustor"]["indirect_parameters"]["recommendation_weighting"] = 1-direct_weighting
            information["trustor"]["direct_parameters"]["interactionNumber"] = self.getInteractionNumber(trustorDID, trusteeDID)
            information["trustor"]["direct_parameters"]["totalInteractionNumber"] = self.getLastTotalInteractionNumber(trusteeDID)
            information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],3)
            information["currentInteractionNumber"] = self.getCurrentInteractionNumber(trustorDID)
            information["initEvaluationPeriod"] = datetime.timestamp(datetime.now())-1000
            information["endEvaluationPeriod"] = datetime.timestamp(datetime.now())

            time.sleep(3)

            message = {"interaction": trustorDID+" has interacted with "+trusteeDID}
            producer.sendMessage(topic_trusteeDID, registered_offer_interaction, message)

            result = producer.sendMessage(provider_topic_name, provider_topic_name, information)
            result = producer.sendMessage(full_topic_name, full_topic_name, information)


            data = "}\\n{\\\"trustorDID\\\": \\\""+trustorDID+"\\\", \\\"trusteeDID\\\": \\\""+trusteeDID+"\\\", \\\"offerDID\\\": \\\""+offerDID+"\\\",\\\"userSatisfaction\\\": "+str(information["trustor"]["direct_parameters"]["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information["trustor"]["direct_parameters"]["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information["trustor"]["direct_parameters"]["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information["currentInteractionNumber"])+"}\""
            previous_file = ""

            with open('DLT.json', 'r') as file:
                file.seek(0)
                previous_file = file.read()
                file.close()

            with open('DLT.json', 'w') as file:
                new_file = previous_file.replace("}\"", data)
                file.write(new_file)
                file.close()

            for i in range(previous_interaction_number-1):
                interaction_number = self.getInteractionNumber(trustorDID, trusteeDID)
                trust_data = consumer.readLastTrustInterationValues(full_topic_name, interaction_number)
                information["trustee"]["trusteeDID"] = trusteeDID
                information["trustee"]["offerDID"] = offerDID
                information["trustee"]["trusteeSatisfaction"] = round((round(random.uniform(0.8, 0.9),3) + trust_data["trusteeSatisfaction"])/2, 3)
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

                message = {"interaction": trustorDID+" has interacted with "+trusteeDID}
                producer.sendMessage(topic_trusteeDID, registered_offer_interaction, message)
                result = producer.sendMessage(provider_topic_name, provider_topic_name, information)
                result = producer.sendMessage(full_topic_name, full_topic_name, information)

                data = "}\\n{\\\"trustorDID\\\": \\\""+trustorDID+"\\\", \\\"trusteeDID\\\": \\\""+trusteeDID+"\\\", \\\"offerDID\\\": \\\""+offerDID+"\\\",\\\"userSatisfaction\\\": "+str(information["trustor"]["direct_parameters"]["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information["trustor"]["direct_parameters"]["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information["trustor"]["direct_parameters"]["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information["currentInteractionNumber"])+"}\""
                previous_file = ""

                with open('DLT.json', 'r') as file:
                    file.seek(0)
                    previous_file = file.read()
                    file.close()

                with open('DLT.json', 'w') as file:
                    new_file = previous_file.replace("}\"", data)
                    file.write(new_file)
                    file.close()


        return None

    def generateTrusteeInformation(self, producer, trustorDID, trusteeDID, offerDID, interaction, availableAssets, totalAssets, availableAssetLocation, totalAssetLocation, managedViolations, predictedViolations, executedViolations, nonPredictedViolations, consideredOffers, totalOffers, consideredOfferLocation, totalOfferLocation, managedOfferViolations, predictedOfferViolations, executedOfferViolations, nonPredictedOfferViolations):
        """ """
        information = self.minimumTrustTemplate(trustorDID, trusteeDID, offerDID)
        print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")
        print("Trustor --->", trustorDID, "Truestee --->", trusteeDID, "offer --->", offerDID, "\n")

        information["trustor"]["credibility"] = self.credibility(trustorDID, trusteeDID)
        print("Credibility ---->", information["trustor"]["credibility"])
        information["trustor"]["transactionFactor"] = self.transactionContextFactor(trustorDID, trusteeDID, offerDID)
        print("Transaction Factor ---->", information["trustor"]["transactionFactor"])
        information["trustor"]["communityFactor"] = self.communityContextFactor(trustorDID, trusteeDID)
        print("Community Factor ---->", information["trustor"]["communityFactor"])
        information["trustor"]["direct_parameters"]["interactionNumber"] = self.getInteractionNumber(trustorDID, trusteeDID)

        direct_weighting = round(random.uniform(0.6, 0.7),2)
        print("Primer peso --->", direct_weighting)
        print("Segundo peso --->", 1-direct_weighting)
        information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
        information["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.75, 0.9), 3)

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
        #information["trustee"]["trusteeSatisfaction"] = self.getTrusteeSatisfactionDLT(trusteeDID)
        #print("PS ---->", ps_weighting)
        print("Provider Satisfaction ---->", provider_satisfaction)
        print("Provider Reputation ---->", provider_reputation)
        #print("OS ---->", os_weighting)
        print("Offer Satisfaction ---->", offer_satisfaction)
        print("Offer Reputation ---->", offer_reputation)
        #information["trustee"]["trusteeSatisfaction"] = ps_weighting * provider_satisfaction + os_weighting * offer_satisfaction
        information["trustee"]["trusteeSatisfaction"] = self.satisfaction(ps_weighting, os_weighting, provider_satisfaction, offer_satisfaction)
        print("Satisfaction ---->", information["trustee"]["trusteeSatisfaction"])

        information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],3)
        print("Final Trust Value ---->", information["trust_value"])
        print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")

        topic_trustorDID = trustorDID.split(":")[2]
        topic_trusteeDID = trusteeDID.split(":")[2]
        topic_offerDID = offerDID.split(":")[2]

        registered_offer_interaction = topic_trusteeDID + "-" + topic_offerDID
        producer.createTopic(topic_trusteeDID)

        provider_topic_name = topic_trustorDID+"-"+topic_trusteeDID
        result = producer.createTopic(provider_topic_name)
        full_topic_name = topic_trustorDID+"-"+topic_trusteeDID+"-"+topic_offerDID
        result = producer.createTopic(full_topic_name)

        if result == 1:
            message = {"interaction": trustorDID+" has interacted with "+trusteeDID}
            producer.sendMessage(topic_trusteeDID, registered_offer_interaction, message)
            result = producer.sendMessage(provider_topic_name, provider_topic_name, information)
            #print("NEW SEND --->",provider_topic_name,"\nValue --->", information)
            result = producer.sendMessage(full_topic_name, full_topic_name, information)
            #print("NEW SEND --->",full_topic_name,"\nValue --->", information)


        data = "}\\n{\\\"trustorDID\\\": \\\""+trustorDID+"\\\", \\\"trusteeDID\\\": \\\""+trusteeDID+"\\\", \\\"offerDID\\\": \\\""+offerDID+"\\\",\\\"userSatisfaction\\\": "+str(information["trustor"]["direct_parameters"]["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information["trustor"]["direct_parameters"]["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information["trustor"]["direct_parameters"]["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information["currentInteractionNumber"])+"}\""
        previous_file = ""

        with open('DLT.json', 'r') as json_file:
            json_file.seek(0)
            previous_file = json_file.read()
            json_file.close()

        with open('DLT.json', 'w') as json_file:
            new_file = previous_file.replace("}\"", data)
            #print("NUEVA DLT", new_file)
            json_file.write(new_file)
            json_file.close()

        #return {"userSatisfaction": information["trustor"]["direct_parameters"]["userSatisfaction"], "interactionNumber": information["trustor"]["direct_parameters"]["interactionNumber"], "totalInteractionNumber": information["trustor"]["direct_parameters"]["totalInteractionNumber"], "currentInteractionNumber": information["currentInteractionNumber"]}
        return None

    def setTrustee1Interactions(self, producer, trusteeDID):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """

        #information_1 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-1", 0, 1, 3, 4, 2, 3, 10, 18, 6, 2)
        #information_2 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-2", 1, 2, 3, 5, 2, 4, 16, 24, 6, 2)
        #information_3 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-1", 0, 4, 10, 11, 4, 6, 18, 21, 0, 3)
        #information_4 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-2", 0, 1, 2, 4, 1, 1, 6, 14, 6, 2)
        #information_5 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-1", 0, 1, 4, 4, 2, 2, 15, 18, 1, 2)
        #information_6 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-2", 1, 3, 3, 4, 2, 2, 18, 21, 1, 2)

        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-1", 1, 3, 4, 2, 3, 16, 18, 0, 2, 2, 3, 2, 2, 5, 6, 0, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-2", 2, 3, 5, 3, 3, 22, 24, 1, 1, 5, 6, 2, 4, 7, 8, 1, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-1", 1, 10, 11, 4, 6, 18, 21, 0, 3, 6, 6, 2, 2, 2, 8, 4, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-2", 1, 2, 4, 1, 1, 6, 14, 6, 2, 2, 2, 1, 1, 3, 4, 1, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-1", 1, 4, 4, 2, 2, 15, 18, 1, 2, 2, 5, 1, 2, 5, 8, 1, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-2", 2, 3, 4, 2, 2, 18, 21, 1, 2, 4, 8, 2, 2, 7, 11, 2, 2)


        return None

    def setTrustee2Interactions(self, producer, trusteeDID):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """

        #information_1 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-2", 0, 1, 3, 4, 2, 3, 10, 18, 6, 2)
        #information_2 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-1", 0, 2, 2, 5, 1, 4, 6, 8, 1, 1)
        #information_3 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-2", 1, 3, 4, 11, 2, 4, 18, 21, 2, 1)
        #information_4 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-1", 0, 1, 2, 4, 1, 1, 6, 14, 6, 2)
        #information_5 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-2", 1, 2, 4, 4, 2, 2, 10, 18, 6, 2)
        #information_6 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-2", 0, 3, 3, 4, 2, 2, 18, 21, 1, 2)

        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-2", 1, 3, 4, 2, 3, 16, 16, 0, 0, 4, 6, 2, 2, 2, 3, 1, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-1", 1, 2, 5, 1, 4, 6, 8, 1, 1, 3, 6, 1, 3, 2, 3, 0, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-2", 2, 4, 11, 2, 4, 18, 21, 2, 1, 5, 8, 3, 3, 5, 9, 2, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-1", 1, 2, 4, 1, 1, 6, 14, 6, 2, 2, 5, 1, 1, 5, 5, 0, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-2", 2, 4, 4, 2, 2, 10, 18, 6, 2, 5, 5, 1, 2, 6, 9, 1, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-2", 1, 3, 4, 2, 2, 18, 21, 1, 2, 2, 4, 2, 2, 7, 10, 1, 2)

        #data = "}\\n{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain5-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain5-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_1["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_1["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_1["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_1["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain6-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain6-RAN-1\\\",\\\"userSatisfaction\\\": "+str(information_2["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_2["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_2["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_2["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain6-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain6-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_3["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_3["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_3["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_3["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain7-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain7-RAN-1\\\",\\\"userSatisfaction\\\": "+str(information_4["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_4["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_4["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_4["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain7-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain7-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_5["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_5["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_5["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_5["currentInteractionNumber"])+"}\\n"+"{\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain8-RAN\\\", \"offerDID\\\": \\\"did:5gzorro:domain8-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_6["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_6["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_6["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_6["currentInteractionNumber"])+"}\""


        #previous_file=""

        """with open('DLT.json', 'r') as json_file:
            json_file.seek(0)
            previous_file = json_file.read()
            json_file.close()

        with open('DLT.json', 'w') as json_file:
            new_file = previous_file.replace("}\"", data)
            print("NUEVA DLT", new_file)
            json_file.write(new_file)
            json_file.close()"""

        return None

    def setTrustee3Interactions(self, producer, trusteeDID):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """
        #information_1 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-1", 0, 1, 1, 2, 1, 1, 6, 9, 1, 2)
        #information_2 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-2", 1, 2, 2, 5, 2, 2, 10, 14, 2, 2)
        #information_3 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-1", 0, 1, 4, 8, 2, 2, 18, 21, 2, 1)
        #information_4 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-2", 1, 2, 3, 8, 1, 1, 18, 23, 2, 3)
        #information_5 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-1", 0, 1, 4, 4, 2, 2, 10, 18, 6, 2)

        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-1", 1, 1, 2, 1, 1, 7, 9, 1, 1, 3, 4, 1, 2, 3, 3, 0, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-2", 2, 4, 5, 2, 2, 13, 14, 1, 0, 8, 10, 3, 5, 6, 9, 2, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-1", 1, 4, 8, 2, 2, 18, 21, 2, 1, 4, 8, 2, 2, 11, 11, 0, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain6-RAN", "did:5gzorro:domain6-RAN-2", 2, 3, 8, 1, 1, 18, 23, 2, 3, 5, 9, 2, 2, 4, 5, 0, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-1", 1, 4, 4, 2, 2, 10, 18, 6, 2, 7, 8, 3, 4, 4, 8, 4, 4)

        #data = "}\\n{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain5-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain5-RAN-1\\\",\\\"userSatisfaction\\\": "+str(information_1["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_1["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_1["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_1["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain5-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain5-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_2["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_2["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_2["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_2["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain6-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain6-RAN-1\\\",\\\"userSatisfaction\\\": "+str(information_3["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_3["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_3["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_3["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain6-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain6-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_4["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_4["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_4["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_4["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain8-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain8-RAN-1\\\",\\\"userSatisfaction\\\": "+str(information_5["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_5["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_5["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_5["currentInteractionNumber"])+"}\""


        #previous_file=""

        """with open('DLT.json', 'r') as json_file:
            json_file.seek(0)
            previous_file = json_file.read()
            json_file.close()

        with open('DLT.json', 'w') as json_file:
            new_file = previous_file.replace("}\"", data)
            print("NUEVA DLT", new_file)
            json_file.write(new_file)
            json_file.close()"""


        return None

    def setTrustee4Interactions(self, producer, trusteeDID):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """
        #information_1 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-2", 0, 1, 6, 8, 4, 5, 19, 19, 0, 0)
        #information_2 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-1", 0, 1, 3, 5, 2, 2, 14, 18, 2, 2)
        #information_3 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-2", 1, 2, 7, 8, 3, 4, 28, 35, 4, 3)
        #information_4 = self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-2", 4, 5, 4, 8, 1, 1, 19, 25, 3, 3)

        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain5-RAN", "did:5gzorro:domain5-RAN-2", 1, 6, 8, 4, 5, 19, 19, 0, 0, 3, 4, 1, 1, 4, 6, 1, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-1", 1, 3, 5, 2, 2, 14, 18, 2, 2, 4, 4, 2, 2, 8, 11, 2, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain7-RAN", "did:5gzorro:domain7-RAN-2", 2, 7, 8, 3, 4, 28, 35, 4, 3, 3, 6, 1, 2, 14, 15, 1, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain8-RAN", "did:5gzorro:domain8-RAN-2", 1, 4, 8, 1, 1, 19, 25, 3, 3, 1, 2, 1, 1, 9, 9, 0, 0)


        #data = "}\\n{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain5-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain5-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_1["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_1["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_1["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_1["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain7-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain7-RAN-1\\\",\\\"userSatisfaction\\\": "+str(information_2["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_2["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_2["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_2["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain7-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain7-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_3["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_3["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_3["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_3["currentInteractionNumber"])+"}\\n"+"{\\\"trustorDID\\\": \\\""+trusteeDID+"\\\", \\\"trusteeDID\\\": \\\"did:5gzorro:domain8-RAN\\\", \\\"offerDID\\\": \\\"did:5gzorro:domain8-RAN-2\\\",\\\"userSatisfaction\\\": "+str(information_4["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information_4["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information_4["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information_4["currentInteractionNumber"])+"}\""


        #previous_file=""

        """with open('DLT.json', 'r') as json_file:
            json_file.seek(0)
            previous_file = json_file.read()
            json_file.close()

        with open('DLT.json', 'w') as json_file:
            new_file = previous_file.replace("}\"", data)
            json_file.write(new_file)
            json_file.close()"""


        return None

    def getLastHistoryTrustValue(self, trustorDID, trusteeDID):
        last_truste_value = 0.0

        trustor = trustorDID.split(":")[2]
        trustee = trusteeDID.split(":")[2]

        recommender_topic = trustor+"-"+trustee

        trust_information = consumer.readLastTrustValue(recommender_topic)
        #print("Provider-Recommender Topic ----> ", recommender_topic, "\n",trust_information, len(trust_information))
        #print("RECOMMENDER TRUST VALUE ----->", trust_information["trust_value"])
        #last_truste_value = trust_information["trust_value"]

        if bool(trust_information):
            #print("EXIST VALUE --->", trust_information["trust_value"])
            last_truste_value = trust_information["trust_value"]
            return last_truste_value
        else:
            """In this case, Trustor didn't have an interaction with Trustee and 
            the provider recommendation is based on the last interaction registered in the DLT"""
            #print("NOT EXIST VALUE --->", recommender_topic)
            return 1

    def getLastOfferHistoryTrustValue(self, trustorDID, trusteeDID, offerDID):
        last_truste_value = 0.0

        trustor = trustorDID.split(":")[2]
        trustee = trusteeDID.split(":")[2]
        offer = offerDID.split(":")[2]

        recommender_topic = trustor+"-"+trustee+"-"+offer

        trust_information = consumer.readLastTrustValue(recommender_topic)
        #print("Offer-Recommender Topic ----> ", recommender_topic, "\n",trust_information, len(trust_information))
        #print("RECOMMENDER TRUST VALUE ----->", trust_information["trust_value"])
        #last_truste_value = trust_information["trust_value"]

        if bool(trust_information):
            #print("EXIST VALUE --->", trust_information["trust_value"])
            last_truste_value = trust_information["trust_value"]
            return last_truste_value
        else:
            """In this case, Trustor didn't have an interaction with Trustee and 
            the provider recommendation is based on the last interaction registered in the DLT"""
            #print("NOT EXIST VALUE --->", recommender_topic)
            return 1

    def getOfferTrusteeFeedbackDLT(self, trusteeDID, offerDID):
        """ This method recovers a recommender, who is reliable for us, that has recently interacted with a trustee.
        Return the last interaction in order to request the last trus value"""

        counter = 0

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))


                """ Starting from the end to identify the last recommender"""
                for interaction in reversed(new_interaction_list):
                    """ Check that the last recommender is not ourselves"""
                    if interaction['trusteeDID'] == trusteeDID and interaction['offerDID'] == offerDID:
                        counter += 1

            file.close()
        return counter

    def getTrusteeFeedbackDLT(self, trusteeDID):
        """ This method recovers a recommender, who is reliable for us, that has recently interacted with a trustee.
        Return the last interaction in order to request the last trust value"""

        counter = 0

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))


                """ Starting from the end to identify the last recommender"""
                for interaction in reversed(new_interaction_list):
                    """ Check that the last recommender is not ourselves"""
                    if interaction['trusteeDID'] == trusteeDID:
                        counter += 1

            file.close()
        return counter

    def getTrustworthyRecommendationDLT(self, trusteeDID, trustworthy_recommender_list):
        

        trustworthy_recommendations = []

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))


                """ Starting from the end to identify the last recommender"""
                for interaction in reversed(new_interaction_list):
                    """ Obtenemos el último valor de confianza de nuestros recommendadores fiable sobre el trustor dando el peso a las recomendaciones finales"""
                    if interaction['trusteeDID'] == trusteeDID and interaction['trustorDID'] in trustworthy_recommender_list:
                        trustworthy_recommendations.append(interaction['trustorDID'])
                        trustworthy_recommender_list.remove(interaction['trustorDID'])


            file.close()
        return trustworthy_recommendations

    def getLastCredibility(self, trustorDID, trusteeDID):
        


        topic_name = trustorDID.split(":")[2]+"-"+trusteeDID.split(":")[2]


        trust_information = consumer.readLastTrustValue(topic_name)
        #print("Credibility ----> ", topic_name, "\n",trust_information, len(trust_information))

        if bool(trust_information):
            #print("EXIST VALUE CREDIBILITY --->", trust_information["credibility"])
            last_credibility = trust_information["credibility"]
            return last_credibility
        else:
            """In this case, Trustor didn't have an interaction with Trustee and 
            the provider recommendation is based on the last interaction registered in the DLT"""
            #print("NOT EXIST VALUE Credibility --->", topic_name)
            return 1

    def getTrustorInteractions(self, trustorDID):

        interactions = []

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))


                """ Starting from the end to identify the last recommender"""
                for interaction in new_interaction_list:
                    if interaction["trustorDID"] == trustorDID:
                        interactions.append(interaction["trusteeDID"])

        return interactions

    def getTrusteeInteractions(self, trustorDID, trusteeDID):

        interactions = []

        if os.path.exists('DLT.json'):
            with open('DLT.json', 'r') as file:
                file.seek(0)
                interaction_list = file.read()
                """Convert string to a list of dictionaries"""

                new_interaction_list = []
                interaction_list = interaction_list.split("\\n")
                for interaction in interaction_list:
                    interaction = interaction.replace("\\\"","\"")
                    interaction = interaction.replace("\"{", "{")
                    interaction = interaction.replace("}\"", "}")
                    new_interaction_list.append(ast.literal_eval(interaction))


                """ Starting from the end to identify the last recommender"""
                for interaction in new_interaction_list:
                    if interaction["trusteeDID"] == trusteeDID and interaction["trustorDID"] != trustorDID:
                        interactions.append(interaction["trustorDID"])
                        return interactions

        return interactions

    """%%%%%%%%%%%%%%   PEERTRUST EQUATIONS %%%%%%%%%%%%%%%%%"""

    def credibility(self, trustorDID, trusteeDID):

        previous_trustor_interactions = list(set(self.getTrustorInteractions(trustorDID)))
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

        credibility = trustee_similarity/similarity_summation

        print("CREDIBILITY ---->", credibility, trustee_similarity, similarity_summation, trustorDID, trusteeDID)

        return credibility

    def similarity(self, trusteeDID):

        common_interaction = []
        trustor_interaction_list = self.getTrustorInteractions(trusteeDID)
        #print("Trustor interactions --->", trustor_interaction_list, "--->", trusteeDID)

        for interaction in trustor_interaction_list:
            common_interaction = self.getTrusteeInteractions(trusteeDID, interaction)
            if common_interaction:
                break
        #print("Primer trustee que tiene interacciones en comun --->", common_interaction)

        common_interaction_list = self.getTrustorInteractions(common_interaction[0])

        #print("Common interactions del anterior --->", common_interaction_list)

        IJS_counter = 0
        global_satisfaction_summation = 0.0

        for interaction in trustor_interaction_list:
            if interaction in common_interaction_list:
                """ Generating kafka topic name """
                trustor_topic = trusteeDID.split(":")[2]+"-"+interaction.split(":")[2]
                common_interaction_topic = common_interaction[0].split(":")[2]+"-"+interaction.split(":")[2]
                #print("TOPICS --->",trustor_topic, common_interaction_topic)

                trustor_satisfaction_summation = consumer.readSatisfactionSummation(trustor_topic)
                common_interaction_satisfaction_summation = consumer.readSatisfactionSummation(common_interaction_topic)

                satisfaction_summation = pow((trustor_satisfaction_summation - common_interaction_satisfaction_summation), 2)
                print("SATISFACTION AL CUADRADO --->", satisfaction_summation)
                global_satisfaction_summation = global_satisfaction_summation + satisfaction_summation
                print("GLOBAL SATISFACTION  --->", global_satisfaction_summation)
                IJS_counter = IJS_counter + 1

        final_similarity = 1 - math.sqrt(global_satisfaction_summation/IJS_counter)
        print("FINAL SATISFACTION  --->",final_similarity)

        return final_similarity


    def communityContextFactor(self, trustorDID, trusteeDID):
        trustworthy_recommender_list = ['did:5gzorro:domain5-RAN', 'did:5gzorro:domain6-RAN', 'did:5gzorro:domain7-RAN','did:5gzorro:domain8-RAN']

        topic_trusteeDID = trusteeDID.split(":")[2]
        total_registered_trustee_interaction = consumer.readTrusteeInteractions(topic_trusteeDID)
        number_trustee_feedbacks_DLT = self.getTrusteeFeedbackDLT(trusteeDID)

        trustee_interaction_rate = number_trustee_feedbacks_DLT / total_registered_trustee_interaction

        if trustorDID in trustworthy_recommender_list:
            trustworthy_recommender_list.remove(trustorDID)

        trustworthy_recommendations = self.getTrustworthyRecommendationDLT(trusteeDID, trustworthy_recommender_list)

        summation_trustworthy_recommendations = 0.0

        for recommender in trustworthy_recommendations:
            last_value = self.getLastHistoryTrustValue(recommender, trusteeDID)
            last_credibility = self.getLastCredibility(trustorDID, trusteeDID)
            summation_trustworthy_recommendations = summation_trustworthy_recommendations + (last_credibility*last_value)

        return round((trustee_interaction_rate+(summation_trustworthy_recommendations/len(trustworthy_recommendations)))/2,3)

    def transactionContextFactor(self, trustorDID, trusteeDID, offerDID):
        """ Currently, only one time-window is contemplated """
        topic_trusteeDID = trusteeDID.split(":")[2]
        offer_trustee = topic_trusteeDID+ "-" +offerDID.split(":")[2]

        total_registered_trustee_interaction = consumer.readTrusteeInteractions(topic_trusteeDID)
        total_registered_offer_interactions = consumer.readOfferTrusteeInteractions(topic_trusteeDID, offer_trustee)

        number_offer_trustee_feedbacks_DLT = self.getOfferTrusteeFeedbackDLT(trusteeDID, offerDID)
        number_trustee_feedbacks_DLT = self.getTrusteeFeedbackDLT(trusteeDID)

        transactionFactor = (number_offer_trustee_feedbacks_DLT / total_registered_offer_interactions + number_trustee_feedbacks_DLT / total_registered_trustee_interaction)/2

        return round(transactionFactor,3)


    def satisfaction(self, PSWeighting, OSWeighting, providerSatisfaction, offerSatisfaction):

        return PSWeighting*providerSatisfaction + OSWeighting*offerSatisfaction


    def providerSatisfaction(self, trustorDID, trusteeDID, providerReputation):
        """ This method computes the Provider's satisfaction considering its reputation and recommendations"""

        
        
        last_interaction = self.getRecommenderDLT(trustorDID, trusteeDID)

        provider_recommendation = self.getLastRecommendationValue(last_interaction)

        
        last_trust_score_recommender = self.getLastHistoryTrustValue(trustorDID, last_interaction['trustorDID'])

        provider_satisfaction = providerReputation * provider_recommendation * last_trust_score_recommender

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

        last_trust_score_recommender = self.getLastOfferHistoryTrustValue(last_interaction['trustorDID'], trusteeDID, offerDID)

        provider_satisfaction = offerReputation * provider_recommendation * last_trust_score_recommender

        return provider_satisfaction

    def offerReputation(self, consideredOffers, totalOffers, consideredOfferLocation, totalOfferLocation, managedOfferViolations, predictedOfferViolations, executedOfferViolations, nonPredictedOfferViolations):
        """ Currently, only one time-window is contemplated"""

        assets_percentage = consideredOffers / totalOffers

        assets_location_percentage = consideredOfferLocation / totalOfferLocation

        managed_violations_percentage = managedOfferViolations / predictedOfferViolations

        violations_percentage = (executedOfferViolations + nonPredictedOfferViolations) / predictedOfferViolations

        reputation = ((assets_percentage + assets_location_percentage + (2 * managed_violations_percentage) - (2 * violations_percentage)) + 2) / 6

        return reputation