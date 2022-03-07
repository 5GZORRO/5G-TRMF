from kafka import KafkaConsumer, TopicPartition
import json
import logging
import time
import requests
import copy


class Consumer():

    consumer = None
    tp = None
    #name_server = 'kafka:9093'
    name_server = '172.28.3.196:9092'
    lastOffset = None

    def start(self, topic):
        """ This method initialises a KafkaConsumer reading messages from the beginning """
        global consumer
        global tp
        global lastOffset

        tp = TopicPartition(topic,0)
        self.consumer = KafkaConsumer(bootstrap_servers='172.28.3.196:9092', group_id=None, auto_offset_reset='earliest')

        self.consumer.assign([tp])
        self.consumer.seek_to_beginning(tp)

        # obtain the last offset value
        lastOffset = self.consumer.end_offsets([tp])[tp]
        #self.consumer = KafkaConsumer(topic, bootstrap_servers=self.name_servername_server, group_id=None,
                                      #enable_auto_commit=False, auto_offset_reset='earliest')

        return self.consumer

    def subscribe(self, topics):
        """" This method subscribes the 5G-TRMF to a set of interesting topics. The topics parameter must be a list """
        global consumer

        try:
            self.consumer.subscribe(topics)
            return 1
        except Exception as e:
            return 0

    def stop(self):
        """ This method finishes a KafkaConsumer connection as well as unsubscribing the topics registered """
        global consumer

        self.consumer.unsubscribe()
        self.consumer.close()

    def start_reading(self, trustorDID, offerDID):
        """ This method begins to retrieve messages from a KafkaTopic.
        IT MUST BE LAUNCHED AS A THREAD TO AVOID BLOCKING THE APP """
        logging.basicConfig(level=logging.INFO)
        global consumer
        global lastOffset

        external_recommendations = []

        for message in self.consumer:
            trust_information = json.loads(message.value.decode())
            if trust_information["offerDID"] == offerDID and trustorDID != trust_information["trustorDID"]:
                end_point = trust_information["endpoint"]

                response = requests.post(end_point, data=json.dumps(trust_information).encode("utf-8"))
                response = json.loads(response.text)

                new_object = {}
                new_object["trustorDID"] = trust_information["trustorDID"]
                new_object["trusteDID"] = trust_information["trusteeDID"]
                new_object["offerDID"] = trust_information["offerDID"]
                new_object["trust_value"] = response["trust_value"]

                if new_object not in external_recommendations:
                    "Adding a new recommendation if it was not previously taken into account"
                    external_recommendations.append(new_object)
                    #logging.info("New recomendation: %s", new_object)

            if message.offset == lastOffset - 1:
                return external_recommendations

    def start_reading_cold_start(self, offset):
        """ This method begins to retrieve messages from a KafkaTopic """
        logging.basicConfig(level=logging.INFO)
        global consumer
        global lastOffset

        additional_providers_and_offers = {}
        if lastOffset != 0:
            for message in self.consumer:
                trust_information = json.loads(message.value.decode())

                if trust_information["trusteeDID"] in additional_providers_and_offers and trust_information["offerDID"] \
                        not in additional_providers_and_offers[trust_information["trusteeDID"]]:
                    additional_providers_and_offers[trust_information["trusteeDID"]].append(trust_information["offerDID"])
                elif trust_information["trusteeDID"] not in additional_providers_and_offers:
                    additional_providers_and_offers[trust_information["trusteeDID"]] = [trust_information["offerDID"]]

                if message.offset == offset - 1:
                    return additional_providers_and_offers
        else:
            return additional_providers_and_offers

    def start_reading_minimum_interactions(self, offset):
        """ This method begins to retrieve messages from a KafkaTopic """
        logging.basicConfig(level=logging.INFO)
        global consumer
        global lastOffset

        minimum_interactions = []
        if lastOffset != 0:
            for message in self.consumer:
                trust_information = json.loads(message.value.decode())
                minimum_interactions.append(trust_information)

                if message.offset == offset - 1:
                    return minimum_interactions
        else:
            return minimum_interactions

    def start_reading_minimum_historical(self):
        """ This method begins to retrieve minimum historical info from a KafkaTopic and the miminum interactions """
        logging.basicConfig(level=logging.INFO)
        global consumer

        for message in self.consumer:
            trust_information = json.loads(message.value.decode())
            minimum_historical = trust_information
            return minimum_historical


    def readSLANotification(self, historical, trustor, trustee, offerDID):
        """ This function retrieves all notifications of potential SLA violations generated by the SLA Breach Predictor.
        Currently, we are simulating that the TMF is subscribed to the real SLA Breach Predictor Kafka topic.
        TODO -> Verify which trustor (5GZORRO Participant) the notification is associated with as the Trust Framework may be
         managing the trust of more than one at the same time. if message.key.decode('utf-8') =="""
        global consumer

        notifications = []
        for message in consumer:
            sla_information = json.loads(message.value.decode())
            notifications.append(sla_information)

        return notifications

    def readLastTrustValues(self, historical, trustor, trustee, last_interaction, current_interation_number):
        """ This method is utilised to retrieve all new trust information generated by a particular trustee on which we want
        to update our previous trust score. This method only retrieves new inputs """
        values = []

        """ Starting from the end to discover new trust information faster """
        for interactions in reversed(historical):

            interation_number = interactions["currentInteractionNumber"]

            """ Looking for all new interactions not previously contemplated"""
            if interactions["trustor"]["trustorDID"] == trustor and \
                        interactions["trustor"]["trusteeDID"] == trustee and \
                        int(interation_number) > int(last_interaction) and \
                        int(interation_number) == int(current_interation_number):
                data = {"trustorDID": interactions["trustor"]["trustorDID"],
                            "trusteeDID": interactions["trustor"]["trusteeDID"],
                            "offerDID": interactions["trustor"]["offerDID"],
                            "trusteeSatisfaction": interactions["trustee"]["trusteeSatisfaction"],
                            "credibility": interactions["trustor"]["credibility"],
                            "transactionFactor": interactions["trustor"]["transactionFactor"],
                            "communityFactor": interactions["trustor"]["communityFactor"],
                            "interaction_number": interactions["trustor"]["direct_parameters"]["interactionNumber"],
                            "totalInteractionNumber": interactions["trustor"]["direct_parameters"]["totalInteractionNumber"],
                            "userSatisfaction": interactions["trustor"]["direct_parameters"]["userSatisfaction"],
                            "trust_value": interactions["trust_value"],
                            "initEvaluationPeriod": interactions["initEvaluationPeriod"],
                            "endEvaluationPeriod": interactions["endEvaluationPeriod"]
                        }
                values.append(data)

        return values

    def readLastTrustInterationValues(self, historical, trustor, trustee, offer, current_interation_number):
        """ This method is utilised to retrieve all new trust information generated by a particular trustee on the current
         interaction number X """

        data = {}

        for interactions in reversed(historical):
            if interactions["trustor"]["trustorDID"] == trustor and \
                    interactions["trustor"]["trusteeDID"] == trustee and \
                    interactions["trustor"]["offerDID"] == offer and \
                    current_interation_number > 0:

                interation_number = interactions["trustor"]["direct_parameters"]["interactionNumber"]

                """ Checking whether the current interaction is the one we are looking for"""
                if interation_number == current_interation_number-1:
                    data = {"trustorDID": interactions["trustor"]["trustorDID"],
                                "trusteeDID": interactions["trustor"]["trusteeDID"],
                                "offerDID": interactions["trustor"]["offerDID"],
                                "trusteeSatisfaction": interactions["trustee"]["trusteeSatisfaction"],
                                "credibility": interactions["trustor"]["credibility"],
                                "transactionFactor": interactions["trustor"]["transactionFactor"],
                                "communityFactor": interactions["trustor"]["communityFactor"],
                                "interaction_number": interactions["trustor"]["direct_parameters"]["interactionNumber"],
                                "totalInteractionNumber": interactions["trustor"]["direct_parameters"]["totalInteractionNumber"],
                                "userSatisfaction": interactions["trustor"]["direct_parameters"]["userSatisfaction"],
                                "trust_value": interactions["trust_value"],
                                "initEvaluationPeriod": interactions["initEvaluationPeriod"],
                                "endEvaluationPeriod": interactions["endEvaluationPeriod"]
                             }
                    return data

        return data

    def readLastTrustValue(self, historical, trustor, trustee):
        """ This method obtains the last trust value recorded in the historical for a specific a trustor, and trustee.
        Only specific information is returned """

        data = {}

        for interactions in reversed(historical):
            if interactions["trustor"]["trustorDID"] == trustor and \
                        interactions["trustor"]["trusteeDID"] == trustee:
                data = {"trustorDID": interactions["trustor"]["trustorDID"],
                            "trusteeDID": interactions["trustor"]["trusteeDID"],
                            "offerDID": interactions["trustor"]["offerDID"],
                            "trusteeSatisfaction": interactions["trustee"]["trusteeSatisfaction"],
                            "credibility": interactions["trustor"]["credibility"],
                            "transactionFactor": interactions["trustor"]["transactionFactor"],
                            "communityFactor": interactions["trustor"]["communityFactor"],
                            "interaction_number": interactions["trustor"]["direct_parameters"]["interactionNumber"],
                            "totalInteractionNumber": interactions["trustor"]["direct_parameters"]["totalInteractionNumber"],
                            "userSatisfaction": interactions["trustor"]["direct_parameters"]["userSatisfaction"],
                            "trust_value": interactions["trust_value"],
                            "initEvaluationPeriod": interactions["initEvaluationPeriod"],
                            "endEvaluationPeriod": interactions["endEvaluationPeriod"]
                        }
                return data

        return data


    def readLastTrustValueOffer(self, historical, trustor, trustee, offer):
        """ This method obtains the last trust value recorded in the historical for a specific a trustor, trustee and offer.
        Only specific information is returned """

        data = {}
        last_interaction = 0

        for interactions in reversed(historical):
            if interactions["trustor"]["trustorDID"] == trustor and \
                    interactions["trustor"]["trusteeDID"] == trustee and \
                    interactions["trustor"]["offerDID"] == offer and \
                    int(interactions["trustor"]["direct_parameters"]["totalInteractionNumber"]) >= last_interaction:
                data = {"trustorDID": interactions["trustor"]["trustorDID"],
                        "trusteeDID": interactions["trustor"]["trusteeDID"],
                        "offerDID": interactions["trustor"]["offerDID"],
                        "trusteeSatisfaction": interactions["trustee"]["trusteeSatisfaction"],
                        "credibility": interactions["trustor"]["credibility"],
                        "transactionFactor": interactions["trustor"]["transactionFactor"],
                        "communityFactor": interactions["trustor"]["communityFactor"],
                        "interaction_number": interactions["trustor"]["direct_parameters"]["interactionNumber"],
                        "totalInteractionNumber": interactions["trustor"]["direct_parameters"]["totalInteractionNumber"],
                        "userSatisfaction": interactions["trustor"]["direct_parameters"]["userSatisfaction"],
                        "trust_value": interactions["trust_value"],
                        "initEvaluationPeriod": interactions["initEvaluationPeriod"],
                        "endEvaluationPeriod": interactions["endEvaluationPeriod"]
                        }
                last_interaction = int(interactions["trustor"]["direct_parameters"]["totalInteractionNumber"])
                #return data

        return data

    def readLastRecommendationTrustValue(self, historical, trustor, trustee, recommender):
        """ This method obtains the recommendation trust value recorded in the historical for a specific a trustor, trustee.
        Only specific information is returned """

        data = {}

        for interactions in reversed(historical):
            if interactions["trustor"]["trustorDID"] == trustor and interactions["trustor"]["trusteeDID"] == trustee and \
                    len(interactions["trustor"]["indirect_parameters"]["recommendations"]) > 0:
                for recommendation in interactions["trustor"]["indirect_parameters"]["recommendations"]:
                    if recommendation["recommender"] == recommender:
                        return float(recommendation["recommendation_trust"])

        return data

    def readAllRecommenders(self, historical, trustor, trustee):
        """ This method obtains all recommenders recorded in the historical for a specific a trustor, trustee """

        data = {}

        for interactions in reversed(historical):
            if interactions["trustor"]["trustorDID"] == trustor and interactions["trustor"]["trusteeDID"] == trustee and \
                    interactions["trustor"]["indirect_parameters"]["recommendations"][0]["recommender"] != 'string':
                return interactions["trustor"]["indirect_parameters"]["recommendations"]

        return data


    def readAllInformationTrustValue(self, historical, trustor, trustee, offer):
        """ This method obtains the last trust value recorded in Kafka for a specific a trustor, trustee and offer. All
         previously recorded trust information is returned """

        data = {}

        for interactions in reversed(historical):
            if interactions["trustor"]["trustorDID"] == trustor and \
                        interactions["trustor"]["trusteeDID"] == trustee and \
                        interactions["trustor"]["offerDID"] == offer:
                """data = {"trustorDID": interactions["trustor"]["trustorDID"],
                            "trusteeDID": interactions["trustor"]["trusteeDID"],
                            "offerDID": interactions["trustor"]["offerDID"],
                            "trusteeSatisfaction": interactions["trustee"]["trusteeSatisfaction"],
                            "credibility": interactions["trustor"]["credibility"],
                            "transactionFactor": interactions["trustor"]["transactionFactor"],
                            "communityFactor": interactions["trustor"]["communityFactor"],
                            "interaction_number": interactions["trustor"]["direct_parameters"]["interactionNumber"],
                            "totalInteractionNumber": interactions["trustor"]["direct_parameters"]["totalInteractionNumber"],
                            "userSatisfaction": interactions["trustor"]["direct_parameters"]["userSatisfaction"],
                            "trust_value": interactions["trust_value"],
                            "initEvaluationPeriod": interactions["initEvaluationPeriod"],
                            "endEvaluationPeriod": interactions["endEvaluationPeriod"]
                        }"""
                return interactions

        return data

    def readAllTemplateTrustValue(self, historical, trustor, trustee):
        """ This method obtains the last trust value recorded in Kafka for a specific a trustor and trustee. All
         previously recorded trust information is returned """

        data = {}

        for interactions in reversed(historical):
            if interactions["trustor"]["trustorDID"] == trustor and \
                    interactions["trustor"]["trusteeDID"] == trustee:
                """data = {"trustorDID": interactions["trustor"]["trustorDID"],
                            "trusteeDID": interactions["trustor"]["trusteeDID"],
                            "offerDID": interactions["trustor"]["offerDID"],
                            "trusteeSatisfaction": interactions["trustee"]["trusteeSatisfaction"],
                            "credibility": interactions["trustor"]["credibility"],
                            "transactionFactor": interactions["trustor"]["transactionFactor"],
                            "communityFactor": interactions["trustor"]["communityFactor"],
                            "interaction_number": interactions["trustor"]["direct_parameters"]["interactionNumber"],
                            "totalInteractionNumber": interactions["trustor"]["direct_parameters"]["totalInteractionNumber"],
                            "userSatisfaction": interactions["trustor"]["direct_parameters"]["userSatisfaction"],
                            "trust_value": interactions["trust_value"],
                            "initEvaluationPeriod": interactions["initEvaluationPeriod"],
                            "endEvaluationPeriod": interactions["endEvaluationPeriod"]
                        }"""
                return interactions

        return data

    def readTrusteeInteractions(self, historical, trustee):
        """ This function counts all interactions with a particular trustee in the historical"""

        counter = 0

        for interactions in reversed(historical):
            if interactions["trustor"]["trusteeDID"] == trustee:
                counter += 1

        return counter

    def readOfferTrusteeInteractions(self, historical, trustee, offerTrusteDIDs):
        """ This function counts all interactions with a particular offer in the historical """

        counter = 0

        for interactions in reversed(historical):
            if interactions["trustor"]["trusteeDID"] == trustee and \
                    interactions["trustor"]["offerDID"] == offerTrusteDIDs:
                counter += 1

        return counter

    def readSatisfaction(self, historical, trustor, trustee, offer):
        for interactions in reversed(historical):
            if interactions["trustor"]["trustorDID"] == trustor and \
                    interactions["trustor"]["trusteeDID"] == trustee and \
                    interactions["trustor"]["offerDID"] == offer:
                return float(interactions["trustor"]["direct_parameters"]["userSatisfaction"])

    def readSatisfactionSummation(self, historical, trustor, trustee):
        """ This method returns the satisfaction average rate between a trustor and a trustee  """

        counter = 0
        satisfactionsummation = 0.0
        iterations = 0

        for interactions in reversed(historical):
            iterations+=1
            if interactions["trustor"]["trustorDID"] == trustor and \
                        interactions["trustor"]["trusteeDID"] == trustee:
                counter += 1
                satisfactionsummation = satisfactionsummation + interactions["trustor"]["direct_parameters"]["userSatisfaction"]

        return round(satisfactionsummation/counter, 3)


"""consumer_instance = Consumer()
consumer_instance.start()
consumer_instance.subscribe("test1")
consumer_instance.start_reading("a","b")
consumer_instance.stop()"""