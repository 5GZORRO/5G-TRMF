import sys
import json
import requests
import random
import datetime


from producer import *

def simulatedSLANotifications():
    """ This method simulates the generation of the SLA Breach predictor notifications and how they impact over the
    current trust score calculates of a particular trustee (stakeholder) and its offer. Not all this information could
    finally be obtained from the SLA Breach Predictor such as if a trustor was able to manage the SLA
    violation successfully """

    if len(sys.argv) != 4:
        print("Usage: python3 simulatedSLANotifications.py [trustorDID] [trusteeDID] [offerDID]")
    else:
        producer = Producer()

        trustorDID = sys.argv[1]
        trusteeDID = sys.argv[2]
        offerDID = sys.argv[3]

        topic_name = "potential-SLA-Breach-Predictions"
        producer.createTopic(topic_name)

        key = trustorDID.split(":")[2] + "-" + trusteeDID.split(":")[2] + "-" + offerDID.split(":")[2]

        """ The notification paramenter is not contemplated on the Breach notification mock JSON format. That information
        should be requested from other 5GZORRO components"""
        now = datetime.datetime.now()
        message = {"breachPredictionNotification": {"slaID": 294, "transactionID": 2715, "productId": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "instanceID": random.randint(1, 10), "ruleID": "availability", "metric": "http://www.provider.com/metrics/availability", "value": 0.44, "datatimeViolation":str(now.strftime("%Y-%m-%d %H:%M:%S")) ,"datatimePrediction": str(now.strftime("%Y-%m-%d %H:%M:%S"))}, "notification": "The "+offerDID.split(":")[2]+" was able to manage the SLA violation successfully."}
        producer.sendMessage(topic_name, key, message)

        now = datetime.datetime.now()
        message = {"breachPredictionNotification": {"slaID": 294, "transactionID": 2715, "productId": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "instanceID": random.randint(1, 10), "ruleID": "availability", "metric": "http://www.provider.com/metrics/availability", "value": 0.70, "datatimeViolation":str(now.strftime("%Y-%m-%d %H:%M:%S")) ,"datatimePrediction": str(now.strftime("%Y-%m-%d %H:%M:%S"))}, "notification": "The "+offerDID.split(":")[2]+" was not able to manage the SLA violation successfully."}
        #message = {"uuid": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "value": 0.70, "notification": "The "+offerDID.split(":")[2]+" was not able to manage the SLA violation successfully."}
        producer.sendMessage(topic_name, key, message)

        now = datetime.datetime.now()
        message = { "breachPredictionNotification": {"slaID": 294, "transactionID": 2715, "productId": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "instanceID": random.randint(1, 10), "ruleID": "availability", "metric": "http://www.provider.com/metrics/availability", "value": 0.93, "datatimeViolation":str(now.strftime("%Y-%m-%d %H:%M:%S")) ,"datatimePrediction": str(now.strftime("%Y-%m-%d %H:%M:%S"))}, "notification": "The "+offerDID.split(":")[2]+" was able to manage the SLA violation successfully."}
        #message = {"uuid": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "value": 0.93, "notification": "The "+offerDID.split(":")[2]+" was able to manage the SLA violation successfully."}
        producer.sendMessage(topic_name, key, message)

        data = {"SLABreachPredictor": topic_name, "key": key}
        requests.post("http://localhost:5002/update_trust_level", data=json.dumps(data).encode("utf-8"))

simulatedSLANotifications()