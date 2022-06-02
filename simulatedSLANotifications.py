import sys
import json
#import requests
#import random
#import datetime


from peer_Trust_Model.producer import *

def simulatedBreachPredictions():
    """ This method simulates the generation of the SLA Breach predictor notifications and how they impact over the
    current trust score calculates of a particular trustee (stakeholder) and its offer. Not all this information could
    finally be obtained from the SLA Breach Predictor such as if a trustor was able to manage the SLA
    violation successfully """

    if len(sys.argv) != 2:
        print("Usage: python3 simulatedSLANotifications.py [trustorDID] [trusteeDID] [offerDID]")
    else:
        producer = Producer()

        #trustorDID = sys.argv[1]
        #trusteeDID = sys.argv[2]
        offerDID = sys.argv[1]

        topic_name = "isbp-topic-out"
        metric = "requests"

        producer.createTopic(topic_name)
        message = {"breachPredictionNotification": {"metric": metric, "datatimeViolation": "02-06-2022T06:00", "datatimePrediction": "02-06-2022T05:55", "transactionID": "f4e04bcc9d824dd9bc9a4971a8d4dcb3", "productID": offerDID, "instanceID": "012", "place": {"city": "Barcelona", "country": "Spain", "locality": "Barcelona", "geographicLocation": {"name": "Barcelona i2CAT Area, Spain ", "geometryType": "string", "geometry": [{"x": "41.3879", "y": "2.1699", "z": "3388.0"}]}}}}
        producer.sendMessage(topic_name, offerDID, message)

        simulatedSLAViolations_afterPrediction(producer, offerDID, metric)

        """ The notification paramenter is not contemplated on the Breach notification mock JSON format. That information
        should be requested from other 5GZORRO components"""
        #now = datetime.datetime.now()
        #message = {"breachPredictionNotification": {"slaID": 294, "transactionID": 2715, "productId": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "instanceID": random.randint(1, 10), "ruleID": "availability", "metric": "http://www.provider.com/metrics/availability", "value": 0.44, "datatimeViolation":str(now.strftime("%Y-%m-%d %H:%M:%S")) ,"datatimePrediction": str(now.strftime("%Y-%m-%d %H:%M:%S"))}, "notification": "The "+offerDID.split(":")[2]+" was able to manage the SLA violation successfully."}
        #producer.sendMessage(topic_name, offerDID, message)

        #now = datetime.datetime.now()
        #message = {"breachPredictionNotification": {"slaID": 294, "transactionID": 2715, "productId": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "instanceID": random.randint(1, 10), "ruleID": "availability", "metric": "http://www.provider.com/metrics/availability", "value": 0.70, "datatimeViolation":str(now.strftime("%Y-%m-%d %H:%M:%S")) ,"datatimePrediction": str(now.strftime("%Y-%m-%d %H:%M:%S"))}, "notification": "The "+offerDID.split(":")[2]+" was not able to manage the SLA violation successfully."}
        #message = {"uuid": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "value": 0.70, "notification": "The "+offerDID.split(":")[2]+" was not able to manage the SLA violation successfully."}
        #producer.sendMessage(topic_name, key, message)

        #now = datetime.datetime.now()
        #message = { "breachPredictionNotification": {"slaID": 294, "transactionID": 2715, "productId": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "instanceID": random.randint(1, 10), "ruleID": "availability", "metric": "http://www.provider.com/metrics/availability", "value": 0.93, "datatimeViolation":str(now.strftime("%Y-%m-%d %H:%M:%S")) ,"datatimePrediction": str(now.strftime("%Y-%m-%d %H:%M:%S"))}, "notification": "The "+offerDID.split(":")[2]+" was able to manage the SLA violation successfully."}
        #message = {"uuid": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "value": 0.93, "notification": "The "+offerDID.split(":")[2]+" was able to manage the SLA violation successfully."}
        #producer.sendMessage(topic_name, key, message)

        #data = {"SLABreachPredictor": topic_name, "trustorDID": trustorDID, "trusteeDID": trusteeDID, "offerDID": offerDID}
        #requests.post("http://localhost:5002/update_trust_level", data=json.dumps(data).encode("utf-8"))

def simulatedSLAViolations():
    """ This method simulates the generation of the SLA Breach predictor notifications and how they impact over the
    current trust score calculates of a particular trustee (stakeholder) and its offer. Not all this information could
    finally be obtained from the SLA Breach Predictor such as if a trustor was able to manage the SLA
    violation successfully """

    if len(sys.argv) != 2:
        print("Usage: python3 simulatedSLANotifications.py [trustorDID] [trusteeDID] [offerDID]")
    else:
        producer = Producer()

        #trustorDID = sys.argv[1]
        #trusteeDID = sys.argv[2]
        offerDID = sys.argv[1]

        topic_name = "sla-monitor-topic-out"
        producer.createTopic(topic_name)
        message = {
            "id": "uuidv4()",
            "productID": offerDID,
            "sla": {
                "id": "slaId",
                "href": "slaHref"
            },
            "rule": {
                "id": "string",
                "metric": "string",
                "unit": "string",
                "referenceValue": "string",
                "operator": "string",
                "tolerance": "string",
                "consequence": "string"
            },
            "violation": {
                "actualValue": "string"
            }
        }
        producer.sendMessage(topic_name, offerDID, message)

def simulatedSLAViolations_afterPrediction(producer, offerDID, metric):
    """ This method generates SLA Violations after Breach Predictions"""

    topic_name = "sla-monitor-topic-out"
    producer.createTopic(topic_name)
    message = {
        "id": "uuidv4()",
        "productID": offerDID,
        "sla": {
            "id": "slaId",
            "href": "slaHref"
        },
        "rule": {
            "id": "string",
            "metric": metric,
            "unit": "string",
            "referenceValue": "string",
            "operator": "string",
            "tolerance": "string",
            "consequence": "string"
        },
        "violation": {
            "actualValue": "string"
        }
    }
    producer.sendMessage(topic_name, offerDID, message)


#simulatedSLAViolations()
simulatedBreachPredictions()