# Trust-management-framework
5GZORRO's trust management component manages the computation of trust values among different stakeholders based on previous experiences and the trust chain with other intermediary entities involved in the trust link. By means of this framework, end-to-end trustworthiness relationships can be established.

## Trust Management Framework REST API

* The current methods and information are available [here](https://5gzorro.github.io/Trust-management-framework/)

## Pre-Requisites

* Python 3
* Docker
* Docker-compose

## Getting started

#### Step 1 - Download the Trust Management Framework repo

```
git clone https://github.com/5GZORRO/Trust-management-framework.git
```

#### Step 2 - Install requirements.txt

This project is written in Python, and consequently, Python 3 is required to deploy its funcionalities. In addition, multiple libraries such as Kafka, PyMongo, Flask, Flask Restful, Gevent, and Werkzeug are needeed in order to utilise such a framework. These dependencies can be installed through the _requirements.txt_ file.

```
pip install -r requirements.txt
```

#### Step 3 - Create all docker images

First of all, we should move to the main Trust Management Framework folder where the _docker-compose.yml_ file is located. Then, we generate the four docker images.

```
docker-compose up --build
```

#### Step 4 - Launch the Trust Management Framework

In order to start all functionalities of the TMF such as gathering information, computing trust scores, storing trust information, and updating trust scores from new events, it is required to launch the _trustManagementFramework.py_ in the port _5002_ inside docker container.

```
python3 trustManagementFramework.py 5002
```

#### Step 5 - Send a list of product offers

In order to check the proper funcionality of the TMF, it is possible to simulate the requests that will be received from the SRSD. In particular, the _simulatedSRSD.py_ file sends a list of product offers and the requester's DID to the TMF. At that time, the TMF will assess the product offers and send the final trust scores back to the SRSD. Note that the TMF is launched at a given time _t_ where trust information regarding previous interactions is already available in the system. Therefore, it includes the trust information of 8 different domains. 

```
python3 simulatedSRSD.py
```

#### Step 6 - Trus evolution with the time (dinamicity)

After computing the trust scores, the TMF is subscribed to the SLA Breach Prediction Kafka where potential breach predictions are notified. Thus, the TMF will add a set of new policies to interpret the SLA events. By means of these events, we attempt to demostrate how some events could decrease or increase a calculated trust score of an Operator.

```
python3 simulatedSLANotifications.py
``` 
