from kafka import KafkaConsumer
import json

class Consumer():

    consumer = None
    name_server = 'kafka:9093'
    historical = []
    topics = []

    def start(self):
        self.consumer = KafkaConsumer(bootstrap_servers=self.name_server, group_id=None)
        #self.consumer = KafkaConsumer(topic, bootstrap_servers=self.name_servername_server, group_id=None,
                                      #enable_auto_commit=False, auto_offset_reset='earliest')

        return self.consumer

    def subscribe(self, topic):
        """" Topics must be a list """

        self.topics.append(topic)
        try:
            self.consumer.subscribe(self.topics)
            return 1
        except Exception as e:
            return 0

    def stop(self):
        self.consumer.unsubscribe()
        self.consumer.close()

    def start_reading(self):

        for message in self.consumer:
            trust_information = json.loads(message.value.decode())

            if trust_information["trustor"]["trustorDID"] in self.historical:
                self.historical[trust_information["trustor"]["trustorDID"]].append(trust_information)
            else:
                self.historical[trust_information["trustor"]["trustorDID"]] = [trust_information]


    def readSLANotification(self, trustor, trustee, offerDID):
        """ This function retrieves all notifications of potential SLA violations generated by the SLA Breach Predictor.
        Currently, we are simulating that the TMF is subscribed to the real SLA Breach Predicto Kafka topic.
        TODO -> Verify which trustor (5GZORRO Participant) the notification is associated with as the Trust Framework may be
         managing the trust of more than one at the same time. if message.key.decode('utf-8') =="""

        notifications = []
        for message in self.consumer:
            sla_information = json.loads(message.value.decode())
            notifications.append(sla_information)

        return notifications

    def readLastTrustValues(self, trustor, trustee, last_interaction, current_interation_number):
        """ This method is utilised to retrieve all new trust information generated by a particular trustee on which we want
        to update our previous trust score. This method only retrieves new inputs """
        values = []

        #if trustor in self.historical:
            #for interactions in reversed(self.historical[trustor]):

        if trustor in self.historical:
            for interactions in reversed(self.historical[trustor]):

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

    def readLastTrustInterationValues(self, trustor, trustee, offer, current_interation_number):
        """ This method is utilised to retrieve all new trust information generated by a particular trustee on the current
         interaction number X """

        data ={}

        if trustor in self.historical:
            for interactions in reversed(self.historical[trustor]):
                if interactions["trustor"]["trusteeDID"] == trustee and \
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

    def readLastTrustValue(self, trustor, trustee):
        """ This method obtains the last trust value recorded in Kafka for a specific a trustor, and trustee. Only
         specific information is returned """
        data = {}
        lastValue = 0

        if trustor in self.historical:
            for interactions in reversed(self.historical[trustor]):
                if interactions["trustor"]["trusteeDID"] == trustee:
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
                break

        return data


    def readLastTrustValueOffer(self, trustor, trustee, offer):
        """ This method obtains the last trust value recorded in Kafka for a specific a trustor, trustee and offer. Only
         specific information is returned """
        data = {}
        lastValue = 0

        if trustor in self.historical:
            for interactions in reversed(self.historical[trustor]):
                if interactions["trustor"]["trusteeDID"] == trustee and interactions["trustor"]["offerDID"] == offer:
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
                break

        return data


    def readAllInformationTrustValue(self, trustor, trustee, offer):
        """ This method obtains the last trust value recorded in Kafka for a specific a trustor, trustee and offer. All
         previously recorded trust information is returned """
        lastValue = 0
        data = {}

        if trustor in self.historical:
            for interactions in reversed(self.historical[trustor]):
                if interactions["trustor"]["trusteeDID"] == trustee and interactions["trustor"]["offerDID"] == offer:
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
                break

        return data

    def readTrusteeInteractions(self, trustee):
        """ This function counts all interactions with a particular trustee in its Kafka channel """
        counter = 0

        for trustor in self.historical:
            for interactions in reversed(self.historical[trustor]):
                if interactions["trustor"]["trusteeDID"] == trustee:
                    counter += 1

        return counter

    def readOfferTrusteeInteractions(self, trustee, offerTrusteDIDs):
        """ This function counts all interactions with a particular offer in its Kafka channel """
        counter = 0

        for trustor in self.historical:
            for interactions in reversed(self.historical[trustor]):
                if interactions["trustor"]["trusteeDID"] == trustee and \
                        interactions["trustor"]["offerDID"] == offerTrusteDIDs:
                    counter += 1

        return counter

    def readSatisfactionSummation(self, trustor, trustee):
        """ This method returns the satisfaction average rate between a trustor and a trustee  """

        counter = 0
        satisfactionsummation = 0.0

        if trustor in self.historical:
            for interactions in reversed(self.historical[trustor]):
                if interactions["trustor"]["trusteeDID"] == trustee and \
                        interactions["trustor"]["trustorDID"] == trustor:

                    counter += 1
                    satisfactionsummation = satisfactionsummation + interactions["trustor"]["direct_parameters"]["userSatisfaction"]


        return round(satisfactionsummation/counter, 3)