# 5G-enabled Trust and Reputation Management Framework (5G-TRMF)

## Introduction
5GZORRO's trust and reputation management component manages the computation of trust values among different stakeholders based on previous experiences and the trust chain with other intermediary entities involved in the trust link. By means of this framework, end-to-end trustworthiness relationships can be established.
The current methods and information are available [here](https://5gzorro.github.io/5G-TRMF/).


![alt text](https://github.com/5GZORRO/5G-TRMF/blob/main/images/5G-TRMF.png?raw=true)
## Pre-requisites

#### System Requirements

* **Number of vCPUs**: 1
* **RAM (GB)**: 1
* **Storage (GB)**: 10
* **Deployment/Virtualization technology**: containers

### Software dependecies

In order to run the 5G-TRMF, the following libraries, included in the _requirements.txt_ file, are mandatory:
* kafka-python
* flask, flask_restful
* gevent
* Werkzeug
* requests
* pymongo
* rstr
* threaded
* pandas
* matplotlib
* seaborn
* python-dotenv
* pyit2fls
* pyvim


### 5GZORRO Module dependencies
Due to the fact that the 5G-TRMF interacts with the Resource & Service Offer Catalog, the Security Analysis Service, the Data Lake Platform and the Intelligent SLA Monitoring and Breach Predictor, these 5GZORRO modules should be up and running for the proper 5G-TRMF behaviour. In order to install the aforementioned 5G-ZORRO modules, please, check the README.md file of each one:

* [Resource & Service Offer Catalog](https://github.com/5GZORRO/resource-and-service-offer-catalog)
* [Security Analysis Service](https://github.com/5GZORRO/intrasecurity)
* [Data Lake Platform](https://github.com/5GZORRO/datalake)
* [SLA Monitoring](https://github.com/5GZORRO/SLA-Monitor)
* [SLA Breach Predictor](https://github.com/5GZORRO/sla-breach-predictor)

It should be pointed out that the 5G-TRMF is consumed by the Smart Resource and Service Discovery, therefore, it should be previously installed to activate the 5G-TRMF activities.

* [Smart Resource and Service Discovery](https://github.com/5GZORRO/Smart-Resource-and-Service-Discovery-application)

Finally, once a final resource or service has been selected, the Intelligent Slice and Service Manager (ISSM) will activate a continuous update process on the selected resource/service to monitor the trust during the relationship. Thence, the 5G-TRMF is also triggered by the ISSM and this module should be properly installed.  

* [Intelligent Slice and Service Manager](https://github.com/5GZORRO/issm)

## Installation
Since the 5G-TRMF is being used in a Kubernetes cluster, below you can find the necessary steps to install 5G-TRMF module.
### Kubernetes installation
#### Step 1 - Download the 5G-enabled Trust and Reputation Management Framework repo

```
git clone https://github.com/5GZORRO/5G-TRMF.git
```

#### Step 2 - Deploy 5G-TRMF in Kubernetes
Since 5GZORRO has two different testbeds in which its modules can be installed, we should select the proper YAML file depending on if we want to deploy the 5G-TRMF in 5GBarcelona or 5TONIC. To find out the configuration file to be executed, we should go to the _kubernetes_deployment_ folder and open inside the _5GBarcelona_ folder or the _5TONIC_ folder. Finally, we should **execute all YAML files** contained in such a folder as 5GZORRO has defined multiple operators and the 5G-TRMF should be part of them all. 

```
cd 5G-TRMF/kubernetes_deployment/5GBarcelona
kubectl apply -f trust-management-framework-kubernetes-domain-A.yaml
```

#### Step 3 - Install requirements.txt - (optional)
Despite the previous YAML files downloaded and installed a docker image which contains all 5G-TRMF requirements installed, if some requirement is still needed, we can install the dependencies through the _requirements.txt_ file.
```
pip install -r requirements.txt
```



## Configuration
Before starting the 5G-TRMF, an additional configuration step should be carried out. 

We need to uncomment the proper endpoint to be consulted, 31113 for operator-A, 31114 for operator-B, 31115 for operator-C. Similarly, it should be also uncomment the proper Kafka endpoint based on the deployment testbed. These endpoints are declared in the _.env_ file as part of the root folder.

```
pyvim .env
```


## Maintainers
**José María Jorquera Valero** - *Developer and Designer* - josemaria.jorquera@um.es


## License
This 5GZORRO component is published under Apache 2.0 license.