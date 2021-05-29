from kafka import KafkaConsumer
import json

def read(topic_name):
    consumer = KafkaConsumer(topic_name, bootstrap_servers='kafka:9093', group_id=None, enable_auto_commit=False, auto_offset_reset='earliest', consumer_timeout_ms=1000)

    for message in consumer:
        print ("key= %s value= %s" % (message.key, message.value))
    consumer.close()

def readLastTrustValues(topic_name, current_iteration_number):
    """ This method is employed when trust information should be generated as a dataset.
    In particular, this method recovers some previous values registered in Kafka to update the new ones.
    """
    consumer = KafkaConsumer(topic_name, bootstrap_servers='kafka:9093', group_id=None, enable_auto_commit=False, auto_offset_reset='earliest', consumer_timeout_ms=1000)
    values = []
    for message in consumer:
        #print(message.value.decode())
        trust_information = json.loads(message.value.decode())
        iteration_number = trust_information["currentInteractionNumber"]

        if iteration_number > current_iteration_number:
            data = {"trustorDID": trust_information["trustor"]["trustorDID"],
                    "trusteeDID": trust_information["trustor"]["trusteeDID"],
                    "offerDID": trust_information["trustor"]["offerDID"],
                    "trusteeSatisfaction": trust_information["trustee"]["trusteeSatisfaction"],
                    "credibility": trust_information["trustor"]["credibility"],
                    "transactionFactor": trust_information["trustor"]["transactionFactor"],
                    "communityFactor": trust_information["trustor"]["communityFactor"],
                    "interaction_number": trust_information["trustor"]["direct_parameters"]["interactionNumber"],
                    "totalInteractionNumber": trust_information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                    "userSatisfaction": trust_information["trustor"]["direct_parameters"]["userSatisfaction"],
                    "trust_value": trust_information["trust_value"],
                    "initEvaluationPeriod": trust_information["initEvaluationPeriod"],
                    "endEvaluationPeriod": trust_information["endEvaluationPeriod"]
                    }
            values.append(data)
            #consumer.close()
            #print("Última interacción registrada -->", data)
            #return data
    consumer.close()
    return values

def readLastTrustInterationValues(topic_name, current_interation_number):
    """ This method is employed when trust information should be generated as a dataset.
    In particular, this method recovers a previous value registered in Kafka to update the new one.
    """
    consumer = KafkaConsumer(topic_name, bootstrap_servers='kafka:9093', group_id=None, enable_auto_commit=False, auto_offset_reset='earliest', consumer_timeout_ms=1000)

    for message in consumer:
        #print(message.value.decode())
        trust_information = json.loads(message.value.decode())
        if current_interation_number > 0:
            interation_number = trust_information["trustor"]["direct_parameters"]["interactionNumber"]
            if interation_number == current_interation_number-1:
                data = {"trustorDID": trust_information["trustor"]["trustorDID"],
                        "trusteeDID": trust_information["trustor"]["trusteeDID"],
                        "offerDID": trust_information["trustor"]["offerDID"],
                        "trusteeSatisfaction": trust_information["trustee"]["trusteeSatisfaction"],
                        "credibility": trust_information["trustor"]["credibility"],
                        "transactionFactor": trust_information["trustor"]["transactionFactor"],
                        "communityFactor": trust_information["trustor"]["communityFactor"],
                        "interaction_number": trust_information["trustor"]["direct_parameters"]["interactionNumber"],
                        "totalInteractionNumber": trust_information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                        "userSatisfaction": trust_information["trustor"]["direct_parameters"]["userSatisfaction"],
                        "trust_value": trust_information["trust_value"],
                        "initEvaluationPeriod": trust_information["initEvaluationPeriod"],
                        "endEvaluationPeriod": trust_information["endEvaluationPeriod"]
                        }
                consumer.close()
                #print("Última interacción registrada -->", data)
                return data
    consumer.close()

def readLastTrustValue(topic_name):
    """ This method is employed to recover some previous values registered in Kafka """
    consumer = KafkaConsumer(topic_name, bootstrap_servers='kafka:9093', group_id=None, enable_auto_commit=False, auto_offset_reset='earliest', consumer_timeout_ms=1000)
    data = {}
    for message in consumer:
        trust_information = json.loads(message.value.decode())
        if trust_information:
            data = {"trustorDID": trust_information["trustor"]["trustorDID"],
                    "trusteeDID": trust_information["trustor"]["trusteeDID"],
                    "offerDID": trust_information["trustor"]["offerDID"],
                    "trusteeSatisfaction": trust_information["trustee"]["trusteeSatisfaction"],
                    "credibility": trust_information["trustor"]["credibility"],
                    "transactionFactor": trust_information["trustor"]["transactionFactor"],
                    "communityFactor": trust_information["trustor"]["communityFactor"],
                    "interaction_number": trust_information["trustor"]["direct_parameters"]["interactionNumber"],
                    "totalInteractionNumber": trust_information["trustor"]["direct_parameters"]["totalInteractionNumber"],
                    "userSatisfaction": trust_information["trustor"]["direct_parameters"]["userSatisfaction"],
                    "trust_value": trust_information["trust_value"],
                    "initEvaluationPeriod": trust_information["initEvaluationPeriod"],
                    "endEvaluationPeriod": trust_information["endEvaluationPeriod"]
                    }

    consumer.close()
    return data

def readTrusteeInteractions(topic_name):
    """ This method is employed to recover some previous values registered in Kafka """
    consumer = KafkaConsumer(topic_name, bootstrap_servers='kafka:9093', group_id=None, enable_auto_commit=False, auto_offset_reset='earliest', consumer_timeout_ms=1000)
    counter = 0

    for message in consumer:
        counter += 1

    #print("READ COUNTER --->", counter, topic_name)
    consumer.close()
    return counter

def readOfferTrusteeInteractions(topic_name, offerTrusteDIDs):
    """ This method is employed to recover some previous values registered in Kafka """
    consumer = KafkaConsumer(topic_name, bootstrap_servers='kafka:9093', group_id=None, enable_auto_commit=False, auto_offset_reset='earliest', consumer_timeout_ms=1000)
    counter = 0

    for message in consumer:
        #print ("key= %s ---->" % message.key)
        #print ("key= %s ---->" % message.key.decode('utf-8'))
        if message.key.decode('utf-8') == offerTrusteDIDs:
            counter += 1

    #print("READ OFFER COUNTER --->", counter, offerTrusteDIDs)
    consumer.close()
    return counter

def readSatisfactionSummation(topic_name):
    """ This method is employed to recover some previous values registered in Kafka """
    consumer = KafkaConsumer(topic_name, bootstrap_servers='kafka:9093', group_id=None, enable_auto_commit=False, auto_offset_reset='earliest', consumer_timeout_ms=1000)
    counter = 0
    satisfactionsummation = 0.0

    for message in consumer:
        trust_information = json.loads(message.value.decode())
        if trust_information:
            counter += 1
            satisfactionsummation = satisfactionsummation + trust_information["trustee"]["trusteeSatisfaction"]

    consumer.close()
    print("SUMATORIO SATISFACTION ---->", satisfactionsummation, counter)
    #data = {"satisfactionsummation": satisfactionsummation,"counter": counter}

    return round(satisfactionsummation/counter, 3)


if __name__ == "__main__":
    read()
