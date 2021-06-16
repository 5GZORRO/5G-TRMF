import json
import sys
import logging
import random
import time
import ast
import math
import consumer
import os.path


from producer import *
from trustInformationTemplate import *
from peerTrust import *
from datetime import datetime
#logging.basicConfig(level=logging.INFO)

""" This file contains all methods necessary to obtain the minimum information required by the peerTrust model """
class PeerTrust():

    def minimumTrustTemplate(self, trustorDID, trusteeDID, offerDID):
        """ This method initialises a set of minimum trust parameters to ensure that the system does not start from
         scratch as well as define a common trust template which will then be updated """
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

        time.sleep(1)

        return information

    def minimumTrustValuesDLT(self, producer):
        """ This method establishes multiple trust relationships from domain 5 to domain 8 in order to start the trust
         model with a set of minimum relationships. In addition, it also simulates the registration of such interactions
         in the DLT """
        user_satisfaction_1 = round(random.uniform(0.8, 0.9), 3)
        user_satisfaction_2 = round(random.uniform(0.6, 0.8), 3)
        user_satisfaction_3 = round(random.uniform(0.75, 0.8), 3)
        user_satisfaction_4 = round(random.uniform(0.6, 0.75), 3)
        user_satisfaction_5 = round(random.uniform(0.85, 0.95), 3)
        user_satisfaction_6 = round(random.uniform(0.85, 0.95), 3)
        user_satisfaction_7 = round(random.uniform(0.80, 0.99), 3)
        user_satisfaction_8 = round(random.uniform(0.80, 0.95), 3)
        user_satisfaction_9 = round(random.uniform(0.85, 0.99), 3)
        user_satisfaction_10 = round(random.uniform(0.83, 0.92), 3)
        user_satisfaction_11 = round(random.uniform(0.86, 0.91), 3)
        user_satisfaction_12 = round(random.uniform(0.76, 0.95), 3)


        data = [{"trustorDID": "did:5gzorro:domain-F", "trusteeDID": "did:5gzorro:domain-G", "offerDID": "did:5gzorro:domain-G-RAN-1",
                 "userSatisfaction": user_satisfaction_1, "interactionNumber": 1, "totalInteractionNumber": 6, "currentInteractionNumber": 8},
                {"trustorDID": "did:5gzorro:domain-F", "trusteeDID": "did:5gzorro:domain-I", "offerDID": "did:5gzorro:domain-I-RAN-2",
                 "userSatisfaction": user_satisfaction_2, "interactionNumber": 1, "totalInteractionNumber": 7, "currentInteractionNumber": 9},
                {"trustorDID": "did:5gzorro:domain-F", "trusteeDID": "did:5gzorro:domain-B", "offerDID": "did:5gzorro:domain-B-RAN-1",
                 "userSatisfaction": user_satisfaction_3, "interactionNumber": 1, "totalInteractionNumber": 1, "currentInteractionNumber": 10},
                {"trustorDID": "did:5gzorro:domain-G", "trusteeDID": "did:5gzorro:domain-H", "offerDID": "did:5gzorro:domain-H-RAN-1",
                 "userSatisfaction": user_satisfaction_4, "interactionNumber": 1, "totalInteractionNumber": 10, "currentInteractionNumber": 7},
                {"trustorDID": "did:5gzorro:domain-G", "trusteeDID": "did:5gzorro:domain-I", "offerDID": "did:5gzorro:domain-I-RAN-1",
                 "userSatisfaction": user_satisfaction_5, "interactionNumber": 1, "totalInteractionNumber": 7, "currentInteractionNumber": 8},
                {"trustorDID": "did:5gzorro:domain-G", "trusteeDID": "did:5gzorro:domain-C", "offerDID": "did:5gzorro:domain-C-RAN-2",
                 "userSatisfaction": user_satisfaction_6, "interactionNumber": 1, "totalInteractionNumber": 1, "currentInteractionNumber": 9},
                {"trustorDID": "did:5gzorro:domain-H", "trusteeDID": "did:5gzorro:domain-F", "offerDID": "did:5gzorro:domain-F-RAN-2",
                 "userSatisfaction": user_satisfaction_7, "interactionNumber": 1, "totalInteractionNumber": 10, "currentInteractionNumber": 11},
                {"trustorDID": "did:5gzorro:domain-H", "trusteeDID": "did:5gzorro:domain-G", "offerDID": "did:5gzorro:domain-G-RAN-2",
                 "userSatisfaction": user_satisfaction_8, "interactionNumber": 1, "totalInteractionNumber": 9, "currentInteractionNumber": 12},
                {"trustorDID": "did:5gzorro:domain-H", "trusteeDID": "did:5gzorro:domain-D", "offerDID": "did:5gzorro:domain-D-RAN-1",
                 "userSatisfaction": user_satisfaction_9, "interactionNumber": 1, "totalInteractionNumber": 1, "currentInteractionNumber": 13},
                {"trustorDID": "did:5gzorro:domain-I", "trusteeDID": "did:5gzorro:domain-H", "offerDID": "did:5gzorro:domain-H-RAN-2",
                 "userSatisfaction": user_satisfaction_10, "interactionNumber": 1, "totalInteractionNumber": 13, "currentInteractionNumber": 8},
                {"trustorDID": "did:5gzorro:domain-I", "trusteeDID": "did:5gzorro:domain-F", "offerDID": "did:5gzorro:domain-F-RAN-1",
                 "userSatisfaction": user_satisfaction_11, "interactionNumber": 1, "totalInteractionNumber": 10, "currentInteractionNumber": 9},
                {"trustorDID": "did:5gzorro:domain-I", "trusteeDID": "did:5gzorro:domain-E", "offerDID": "did:5gzorro:domain-E-RAN-1",
                 "userSatisfaction": user_satisfaction_12, "interactionNumber": 1, "totalInteractionNumber": 1, "currentInteractionNumber": 10}
                ]
        print("\n\nSet of previous trust interactions between 5GZORRO domains\n")
        print(data, "\n")

        string_data = "{\"trustorDID\": \"did:5gzorro:domain-F\", \"trusteeDID\": \"did:5gzorro:domain-G\", \"offerDID\": \"did:5gzorro:domain-G-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_1)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 6, \"currentInteractionNumber\": 8}\n"+"{\"trustorDID\": \"did:5gzorro:domain-F\", \"trusteeDID\": \"did:5gzorro:domain-I\", \"offerDID\": \"did:5gzorro:domain-I-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_2)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 7, \"currentInteractionNumber\": 9}\n"+"{\"trustorDID\": \"did:5gzorro:domain-F\", \"trusteeDID\": \"did:5gzorro:domain-B\", \"offerDID\": \"did:5gzorro:domain-B-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_3)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 1, \"currentInteractionNumber\": 10}\n"+"{\"trustorDID\": \"did:5gzorro:domain-G\", \"trusteeDID\": \"did:5gzorro:domain-H\", \"offerDID\": \"did:5gzorro:domain-H-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_4)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 10, \"currentInteractionNumber\": 7}\n"+"{\"trustorDID\": \"did:5gzorro:domain-G\", \"trusteeDID\": \"did:5gzorro:domain-I\", \"offerDID\": \"did:5gzorro:domain-I-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_5)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 7, \"currentInteractionNumber\": 8}\n"+"{\"trustorDID\": \"did:5gzorro:domain-G\", \"trusteeDID\": \"did:5gzorro:domain-C\", \"offerDID\": \"did:5gzorro:domain-C-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_6)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 1, \"currentInteractionNumber\": 9}\n"+"{\"trustorDID\": \"did:5gzorro:domain-H\", \"trusteeDID\": \"did:5gzorro:domain-F\", \"offerDID\": \"did:5gzorro:domain-F-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_7)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 10, \"currentInteractionNumber\": 11}\n"+"{\"trustorDID\": \"did:5gzorro:domain-H\", \"trusteeDID\": \"did:5gzorro:domain-G\", \"offerDID\": \"did:5gzorro:domain-G-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_8)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 9, \"currentInteractionNumber\": 12}\n"+"{\"trustorDID\": \"did:5gzorro:domain-H\", \"trusteeDID\": \"did:5gzorro:domain-D\", \"offerDID\": \"did:5gzorro:domain-D-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_9)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 1, \"currentInteractionNumber\": 13}\n"+"{\"trustorDID\": \"did:5gzorro:domain-I\", \"trusteeDID\": \"did:5gzorro:domain-H\", \"offerDID\": \"did:5gzorro:domain-H-RAN-2\",\"userSatisfaction\": "+str(user_satisfaction_10)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 13, \"currentInteractionNumber\": 8}\n"+"{\"trustorDID\": \"did:5gzorro:domain-I\", \"trusteeDID\": \"did:5gzorro:domain-F\", \"offerDID\": \"did:5gzorro:domain-F-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_11)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 10, \"currentInteractionNumber\": 9}\n"+"{\"trustorDID\": \"did:5gzorro:domain-I\", \"trusteeDID\": \"did:5gzorro:domain-E\", \"offerDID\": \"did:5gzorro:domain-E-RAN-1\",\"userSatisfaction\": "+str(user_satisfaction_12)+", \"interactionNumber\": 1, \"totalInteractionNumber\": 1, \"currentInteractionNumber\": 10}"

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
                for i in range(random.randint(0, 1)):
                    producer.sendMessage(registered_interaction, registered_offer_interaction, message)
                producer.sendMessage(provider_topic_name, provider_topic_name, trust_informartion)
                producer.sendMessage(full_topic_name, full_topic_name, trust_informartion)

        if not os.path.exists('DLT.json'):
            with open('DLT.json', 'a') as json_file:
                json.dump(string_data, json_file)
                json_file.close()

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

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            for i in new_interaction_list:
                if i["trustorDID"] == trusteeDID and i["currentInteractionNumber"] > last_total_iteraction_number:
                    last_total_iteraction_number = i["currentInteractionNumber"]
                elif i["trusteeDID"] == trusteeDID and i["totalInteractionNumber"] > last_total_iteraction_number:
                    last_total_iteraction_number = i["totalInteractionNumber"]

        return last_total_iteraction_number

    def getCurrentInteractionNumber(self, trustorDID):
        """ This method returns the next interaction number for a trustor """
        current_iteraction_number = 0

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            for i in new_interaction_list:
                if i["trustorDID"] == trustorDID and i["currentInteractionNumber"] > current_iteraction_number:
                    current_iteraction_number = i["currentInteractionNumber"]
                elif i["trusteeDID"] == trustorDID and i["totalInteractionNumber"] > current_iteraction_number:
                    current_iteraction_number = i["totalInteractionNumber"]

        return current_iteraction_number+1

    def getInteractionNumber(self, trustorDID, trusteeDID):
        """ This method retrieves the number of interactions between two entities and adds one more interaction """
        iteraction_number = 0

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            for i in new_interaction_list:
                if i["trustorDID"] == trustorDID and i["trusteeDID"] == trusteeDID and i["interactionNumber"] > iteraction_number:
                    iteraction_number = i["interactionNumber"]

        return iteraction_number+1


    def getRecommenderDLT(self, trustorDID, trusteeDID):
        """ This method recovers a recommender, who is reliable for us, that has recently interacted with a trustee.
        Return the last interaction in order to request the last trust value. In this case, reliable means
        other trustees with whom we have previously interacted with """

        last_interaction = {}

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            last_registered_interaction = True
            """ Starting from the end to identify the last recommender"""
            for interaction in reversed(new_interaction_list):
                """ Check that the last recommender is not ourselves"""
                if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID:
                    """ Store the most recent interaction with the Trustee to return it in the case of no trustworthy 
                    recommenders can be found"""
                    if last_registered_interaction:
                        last_interaction = interaction
                        last_registered_interaction = False
                    """Check if the Trustor is reliable for us"""
                    for trustworthy_candidate in reversed(new_interaction_list):
                        if trustworthy_candidate['trustorDID'] == trustorDID and trustworthy_candidate['trusteeDID'] == interaction['trustorDID']:
                            return interaction

        return last_interaction

    def getRecommenderOfferDLT(self, trustorDID, trusteeDID, offerDID):
        """ This method recovers an offer associated with a recommender, who is reliable for us, that has recently
        interacted with a trustee. Return the last interaction in order to request the last trust value.
        In this case, reliable means other trustees with whom we have previously interacted with"""

        last_interaction = {}

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            last_registered_interaction = True
            """ Starting from the end to identify the last recommender """
            for interaction in reversed(new_interaction_list):
                """ Check that the last recommender is not ourselves"""
                if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID and interaction['offerDID'] == offerDID:
                    """ Store the most recent interaction with the Trustee """
                    if last_registered_interaction:
                        last_interaction = interaction
                        last_registered_interaction = False
                    """ Check if the Trustor is reliable for us """
                    for trustworthy_candidate in reversed(new_interaction_list):
                        if trustworthy_candidate['trustorDID'] == trustorDID and trustworthy_candidate['trusteeDID'] == interaction['trustorDID'] and trustworthy_candidate['offerDID'] == offerDID:
                            return interaction

        return last_interaction

    def getLastRecommendationValue(self, last_interaction):
        """ This methods goes to a recommender kafka channel to request a trust score """

        last_truste_value = 0.0

        trustor = last_interaction['trustorDID'].split(":")[2]
        trustee = last_interaction['trusteeDID'].split(":")[2]

        recommender_topic = trustor+"-"+trustee

        trust_information = consumer.readLastTrustValue(recommender_topic)
        #print("RECOMMENDER TRUST VALUE ----->", trust_information["trust_value"])
        last_truste_value = trust_information["trust_value"]

        return last_truste_value

    def getLastOfferRecommendationValue(self, last_interaction):
        """ This methods goes to an offer recommender kafka channel to request a trust score """

        last_truste_value = 0.0

        trustor = last_interaction['trustorDID'].split(":")[2]
        trustee = last_interaction['trusteeDID'].split(":")[2]
        offer = last_interaction['offerDID'].split(":")[2]
        recommender_topic = trustor+"-"+trustee+"-"+offer

        trust_information = consumer.readLastTrustValue(recommender_topic)
        #print("RECOMMENDER Offer TRUST VALUE ----->", trust_information["trust_value"])
        last_truste_value = trust_information["trust_value"]

        return last_truste_value

    def getTrusteeSatisfactionDLT(self, trusteeDID):

        last_interaction = {}
        counter = 0
        general_satisfaction = 0.0

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            """ Starting from the end to identify the last recommender """
            for interaction in new_interaction_list:
                if interaction['trustorDID'] == trusteeDID:
                    general_satisfaction = general_satisfaction + interaction['userSatisfaction']
                    counter = counter + 1

        return round(general_satisfaction/counter, 3)


    def generateHistoryTrustInformation(self, producer, trustorDID, trusteeDID, offerDID, provider_topic_name, full_topic_name, topic_trusteeDID, registered_offer_interaction, previous_interaction_number):
        """ This method generates trust information that will be sent to trustor Kafka Topic. In particular,
        it is adding _n_ previous interactions (history) to be contemplated in future assessments"""

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

            time.sleep(1)

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
        """ This method introduces Trustee information based on peerTrust equations and using the minimum
        values previously established"""

        information = self.minimumTrustTemplate(trustorDID, trusteeDID, offerDID)
        print("\t* Provider ---> "+trusteeDID+" -- Product offer ---> "+offerDID)

        #print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ \n")
        #print("Trustor --->", trustorDID, "Truestee --->", trusteeDID, "offer --->", offerDID, "\n")

        information["trustor"]["credibility"] = self.credibility(trustorDID, trusteeDID)
        #print("Credibility ---->", information["trustor"]["credibility"])
        information["trustor"]["transactionFactor"] = self.transactionContextFactor(trustorDID, trusteeDID, offerDID)
        #print("Transaction Factor ---->", information["trustor"]["transactionFactor"])
        information["trustor"]["communityFactor"] = self.communityContextFactor(trustorDID, trusteeDID)
        #print("Community Factor ---->", information["trustor"]["communityFactor"])

        direct_weighting = round(random.uniform(0.6, 0.7),2)
        #print("Primer peso --->", direct_weighting)
        #print("Segundo peso --->", 1-direct_weighting)
        information["trustor"]["direct_parameters"]["direct_weighting"] = direct_weighting
        #information["trustor"]["direct_parameters"]["userSatisfaction"] = round(random.uniform(0.75, 0.9), 3)

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

        #information["trustee"]["trusteeSatisfaction"] = self.getTrusteeSatisfactionDLT(trusteeDID)
        #print("PS ---->", ps_weighting)
        #print("Provider Satisfaction ---->", provider_satisfaction)
        #print("Provider Reputation ---->", provider_reputation)
        #print("OS ---->", os_weighting)
        #print("Offer Satisfaction ---->", offer_satisfaction)
        #print("Offer Reputation ---->", offer_reputation)
        information["trustor"]["direct_parameters"]["userSatisfaction"] = self.satisfaction(ps_weighting, os_weighting, provider_satisfaction, offer_satisfaction)
        #print("Satisfaction ---->", information["trustor"]["direct_parameters"]["userSatisfaction"])

        information["trust_value"] = round(information["trustor"]["direct_parameters"]["direct_weighting"]*(information["trustee"]["trusteeSatisfaction"]*information["trustor"]["credibility"]*information["trustor"]["transactionFactor"])+information["trustor"]["indirect_parameters"]["recommendation_weighting"]*information["trustor"]["communityFactor"],3)
        #print("Final Trust Value ---->", information["trust_value"])
        #print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")

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
            producer.sendMessage(provider_topic_name, provider_topic_name, information)
            producer.sendMessage(full_topic_name, full_topic_name, information)

        data = "}\\n{\\\"trustorDID\\\": \\\""+trustorDID+"\\\", \\\"trusteeDID\\\": \\\""+trusteeDID+"\\\", \\\"offerDID\\\": \\\""+offerDID+"\\\",\\\"userSatisfaction\\\": "+str(information["trustor"]["direct_parameters"]["userSatisfaction"])+", \\\"interactionNumber\\\": "+str(information["trustor"]["direct_parameters"]["interactionNumber"])+", \\\"totalInteractionNumber\\\": "+str(information["trustor"]["direct_parameters"]["totalInteractionNumber"])+", \\\"currentInteractionNumber\\\": "+str(information["currentInteractionNumber"])+"}\""
        previous_file = ""

        with open('DLT.json', 'r') as json_file:
            json_file.seek(0)
            previous_file = json_file.read()
            json_file.close()

        with open('DLT.json', 'w') as json_file:
            new_file = previous_file.replace("}\"", data)
            json_file.write(new_file)
            json_file.close()

        return None

    def setTrustee1Interactions(self, producer, trusteeDID):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """
        print("The "+trusteeDID+" trust interactions with other 5GZORRO domains are:\n")
        #print("%%%%%%%%%%%%%% Principal PeerTrust equation %%%%%%%%%%%%%%\n")
        #print("\tT(u) = α * ((∑ S(u,i) * Cr(p(u,i) * TF (u,i)) / I(u)) + β * CF(u)\n")
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-F", "did:5gzorro:domain-F-RAN-1", 1, 3, 4, 2, 3, 16, 18, 0, 2, 2, 3, 2, 2, 5, 6, 0, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-F", "did:5gzorro:domain-F-RAN-2", 2, 3, 5, 3, 3, 22, 24, 1, 1, 5, 6, 2, 4, 7, 8, 1, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-I", "did:5gzorro:domain-I-RAN-1", 1, 4, 4, 2, 2, 15, 18, 1, 2, 2, 5, 1, 2, 5, 8, 1, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-G", "did:5gzorro:domain-G-RAN-1", 1, 10, 11, 4, 6, 18, 21, 0, 3, 6, 6, 2, 2, 2, 8, 4, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-H", "did:5gzorro:domain-H-RAN-2", 1, 2, 4, 1, 1, 6, 14, 6, 2, 2, 2, 1, 1, 3, 4, 1, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-I", "did:5gzorro:domain-I-RAN-2", 2, 3, 4, 2, 2, 18, 21, 1, 2, 4, 8, 2, 2, 7, 11, 2, 2)


    def setTrustee2Interactions(self, producer, trusteeDID):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """
        print("The "+trusteeDID+" trust interactions with other 5GZORRO domains are:\n")
        #print("%%%%%%%%%%%%%% Principal PeerTrust equation %%%%%%%%%%%%%%\n")
        #print("\tT(u) = α * ((∑ S(u,i) * Cr(p(u,i) * TF (u,i)) / I(u)) + β * CF(u)\n")
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-F", "did:5gzorro:domain-F-RAN-2", 1, 3, 4, 2, 3, 16, 16, 0, 0, 4, 6, 2, 2, 2, 3, 1, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-H", "did:5gzorro:domain-H-RAN-2", 2, 4, 4, 2, 2, 10, 18, 6, 2, 5, 5, 1, 2, 6, 9, 1, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-G", "did:5gzorro:domain-G-RAN-2", 2, 4, 11, 2, 4, 18, 21, 2, 1, 5, 8, 3, 3, 5, 9, 2, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-H", "did:5gzorro:domain-H-RAN-1", 1, 2, 4, 1, 1, 6, 14, 6, 2, 2, 5, 1, 1, 5, 5, 0, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-I", "did:5gzorro:domain-I-RAN-2", 1, 3, 4, 2, 2, 18, 21, 1, 2, 2, 4, 2, 2, 7, 10, 1, 2)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-G", "did:5gzorro:domain-G-RAN-1", 1, 2, 5, 1, 4, 6, 8, 1, 1, 3, 6, 1, 3, 2, 3, 0, 1)


    def setTrustee3Interactions(self, producer, trusteeDID):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """
        print("The "+trusteeDID+" trust interactions with other 5GZORRO domains are:\n")
        #print("%%%%%%%%%%%%%% Principal PeerTrust equation %%%%%%%%%%%%%%\n")
        #print("\tT(u) = α * ((∑ S(u,i) * Cr(p(u,i) * TF (u,i)) / I(u)) + β * CF(u)\n")
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-F", "did:5gzorro:domain-F-RAN-1", 1, 1, 2, 1, 1, 7, 9, 1, 1, 3, 4, 1, 2, 3, 3, 0, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-G", "did:5gzorro:domain-G-RAN-1", 1, 4, 8, 2, 2, 18, 21, 2, 1, 4, 8, 2, 2, 11, 11, 0, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-I", "did:5gzorro:domain-I-RAN-1", 1, 4, 4, 2, 2, 10, 18, 6, 2, 7, 8, 3, 4, 4, 8, 4, 4)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-F", "did:5gzorro:domain-F-RAN-2", 2, 4, 5, 2, 2, 13, 14, 1, 0, 8, 10, 3, 5, 6, 9, 2, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-G", "did:5gzorro:domain-G-RAN-2", 2, 3, 8, 1, 1, 18, 23, 2, 3, 5, 9, 2, 2, 4, 5, 0, 1)


    def setTrustee4Interactions(self, producer, trusteeDID):
        """ This method introduces interactions to the DLT in order to avoid a cold start of all system """
        print("The "+trusteeDID+" trust interactions with other 5GZORRO domains are:\n")
        #print("%%%%%%%%%%%%%% Principal PeerTrust equation %%%%%%%%%%%%%%\n")
        #print("\tT(u) = α * ((∑ S(u,i) * Cr(p(u,i) * TF (u,i)) / I(u)) + β * CF(u)\n")
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-F", "did:5gzorro:domain-F-RAN-2", 1, 6, 8, 4, 5, 19, 19, 0, 0, 3, 4, 1, 1, 4, 6, 1, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-H", "did:5gzorro:domain-H-RAN-1", 1, 3, 5, 2, 2, 14, 18, 2, 2, 4, 4, 2, 2, 8, 11, 2, 1)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-I", "did:5gzorro:domain-I-RAN-2", 1, 4, 8, 1, 1, 19, 25, 3, 3, 1, 2, 1, 1, 9, 9, 0, 0)
        self.generateTrusteeInformation(producer, trusteeDID, "did:5gzorro:domain-H", "did:5gzorro:domain-H-RAN-2", 2, 7, 8, 3, 4, 28, 35, 4, 3, 3, 6, 1, 2, 14, 15, 1, 0)

    def getLastHistoryTrustValue(self, trustorDID, trusteeDID):
        """ This method retrieves the last trust score that a trustor has stored about a trustee in its Kafka topic"""
        last_truste_value = 0.0

        trustor = trustorDID.split(":")[2]
        trustee = trusteeDID.split(":")[2]

        recommender_topic = trustor+"-"+trustee

        trust_information = consumer.readLastTrustValue(recommender_topic)

        if bool(trust_information):
            last_truste_value = trust_information["trust_value"]
            return last_truste_value
        else:
            """In this case, Trustor didn't have an interaction with Trustee and 
            the provider recommendation is based on the last interaction registered in the DLT"""
            return 1

    def getLastOfferHistoryTrustValue(self, trustorDID, trusteeDID, offerDID):
        """ This method retrieves the last trust score that a trustor has stored about an offer trustee
        in its Kafka topic"""

        last_truste_value = 0.0

        trustor = trustorDID.split(":")[2]
        trustee = trusteeDID.split(":")[2]
        offer = offerDID.split(":")[2]

        recommender_topic = trustor+"-"+trustee+"-"+offer

        trust_information = consumer.readLastTrustValue(recommender_topic)

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

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            """ Starting from the end to identify the last recommender"""
            for interaction in reversed(new_interaction_list):
                """ Check that the last recommender is not ourselves"""
                if interaction['trusteeDID'] == trusteeDID and interaction['offerDID'] == offerDID:
                    counter += 1

        return counter

    def getTrusteeFeedbackNumberDLT(self, trusteeDID):
        """ This method counts the number of feedbacks registered in the DLT for a particular trustee """

        counter = 0

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            """ Starting from the end to identify the last recommender"""
            for interaction in reversed(new_interaction_list):
                """ Check that the last recommender is not ourselves"""
                if interaction['trusteeDID'] == trusteeDID:
                    counter += 1

        return counter

    def getTrustworthyRecommendationDLT(self, trustorDID, trusteeDID, trustworthy_recommender_list):
        """ This method returns from a trusted list those recommender that have interacted with the trustor """

        trustworthy_recommendations = []

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            """ Starting from the end to identify the last recommender"""
            for interaction in reversed(new_interaction_list):
                """ Obtenemos el último valor de confianza de nuestros recommendadores fiable sobre el trustor dando el peso a las recomendaciones finales"""
                if interaction['trustorDID'] != trustorDID and interaction['trusteeDID'] == trusteeDID and interaction['trustorDID'] in trustworthy_recommender_list:
                    trustworthy_recommendations.append(interaction['trustorDID'])
                    trustworthy_recommender_list.remove(interaction['trustorDID'])

        return trustworthy_recommendations

    def getLastCredibility(self, trustorDID, trusteeDID):
        """ This method recovers the last credibility value registered in the DLT for a particular trustee"""

        topic_name = trustorDID.split(":")[2]+"-"+trusteeDID.split(":")[2]

        trust_information = consumer.readLastTrustValue(topic_name)

        if bool(trust_information):
            last_credibility = trust_information["credibility"]
            return last_credibility
        else:
            """In this case, Trustor didn't have an credibility with Trustee and 
            the provider recommendation is based on the last history value registered in its Kafka topic"""
            return 1

    def getTrustorInteractions(self, trustorDID):
        """ This methods return all trustor's interactions registered in the DLT"""
        interactions = []

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            """ Starting from the end to identify the last recommender"""
            for interaction in new_interaction_list:
                if interaction["trustorDID"] == trustorDID:
                    interactions.append(interaction["trusteeDID"])

        return interactions

    def getTrusteeInteractions(self, trustorDID, trusteeDID):
        """ This methods return all entities that have interacted with a trustee and
        have published feedbacks in the DLT"""
        interactions = []

        if os.path.exists('DLT.json'):
            """ Convert string to a list of dictionaries """
            new_interaction_list = self.stringToDictionaryList()

            """ Starting from the beginning to identify the last recommender"""
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

        credibility = trustee_similarity/(similarity_summation/summation_counter)

        #print("CREDIBILITY ---->", credibility, trustee_similarity, similarity_summation/summation_counter, trustorDID, trusteeDID)

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
                """ Generating kafka topic name """
                trustor_topic = trusteeDID.split(":")[2]+"-"+interaction.split(":")[2]
                common_interaction_topic = common_interaction[0].split(":")[2]+"-"+interaction.split(":")[2]

                trustor_satisfaction_summation = consumer.readSatisfactionSummation(trustor_topic)
                common_interaction_satisfaction_summation = consumer.readSatisfactionSummation(common_interaction_topic)

                satisfaction_summation = pow((trustor_satisfaction_summation - common_interaction_satisfaction_summation), 2)
                global_satisfaction_summation = global_satisfaction_summation + satisfaction_summation
                #print("GLOBAL SATISFACTION  --->", global_satisfaction_summation)
                IJS_counter = IJS_counter + 1

        final_similarity = 1 - math.sqrt(global_satisfaction_summation/IJS_counter)
        #print("FINAL SATISFACTION  --->", final_similarity)

        return final_similarity


    def communityContextFactor(self, trustorDID, trusteeDID):
        """ Static list of recommender based on the domains registered in the DLT. TODO dynamic """
        trustworthy_recommender_list = ['did:5gzorro:domain-F', 'did:5gzorro:domain-G', 'did:5gzorro:domain-H','did:5gzorro:domain-I']

        topic_trusteeDID = trusteeDID.split(":")[2]
        total_registered_trustee_interaction = consumer.readTrusteeInteractions(topic_trusteeDID)
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

        trustworthy_recommender_list = ['did:5gzorro:domain-F', 'did:5gzorro:domain-G', 'did:5gzorro:domain-H','did:5gzorro:domain-I']

        topic_trusteeDID = trusteeDID.split(":")[2]
        total_registered_trustee_interaction = consumer.readTrusteeInteractions(topic_trusteeDID)
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
        """ Currently, only one time-window is contemplated """
        topic_trusteeDID = trusteeDID.split(":")[2]
        offer_trustee = topic_trusteeDID+ "-" +offerDID.split(":")[2]

        total_registered_trustee_interaction = consumer.readTrusteeInteractions(topic_trusteeDID)
        total_registered_offer_interactions = consumer.readOfferTrusteeInteractions(topic_trusteeDID, offer_trustee)

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

        #print("Provider Reputation --->", providerReputation, "Provider Recommendation -->", provider_recommendation, "Last Trust Recommender -->", last_trust_score_recommender)

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