import sys
import json
import requests

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
        message = {"uuid": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "value": 0.44, "notification": "The "+offerDID.split(":")[2]+" was able to manage the SLA violation successfully."}
        producer.sendMessage(topic_name, key, message)

        message = {"uuid": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "value": 0.93, "notification": "The "+offerDID.split(":")[2]+" was able to manage the SLA violation successfully."}
        producer.sendMessage(topic_name, key, message)

        message = {"uuid": trusteeDID.split(":")[2], "resourceId": offerDID.split(":")[2], "value": 0.70, "notification": "The "+offerDID.split(":")[2]+" was not able to manage the SLA violation successfully."}
        producer.sendMessage(topic_name, key, message)

        data = {"SLABreachPredictor": topic_name, "key": key}
        requests.post("http://localhost:5002/update_trust_level", data=json.dumps(data).encode("utf-8"))

simulatedSLANotifications()