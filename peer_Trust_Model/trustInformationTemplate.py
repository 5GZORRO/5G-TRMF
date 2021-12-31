
class TrustInformationTemplate():
    def trustTemplate(self):
        """This methods introduces the general Trust template that will be used in order to generate a dataset,
    and also to compute new trust scores and provide recomendations """
        general_JSON = {
                        "trustor": {
                            "trustorDID": "string",
                            "trusteeDID": "string",
                            "credibility": "Unknown Type: double",
                            "transactionFactor": "Unknown Type: double",
                            "communityFactor": "Unknown Type: double",
                            "trust_propagation": True,
                            "trust_update": "Unknown",
                            "trust_evaluation": "PeerTrust",
                            "direct_parameters": {
                                "direct_weighting": "Unknown Type: double",
                                "userSatisfaction": "Unknown Type: double",
                                "providerSatisfaction": "Unknown Type: double",
                                "PSWeighting": "Unknown Type: double",
                                "offerSatisfaction": "Unknown Type: double",
                                "OSWeighting": "Unknown Type: double",
                                "providerReputation": "Unknown Type: double",
                                "offerReputation": "Unknown Type: double",
                                "availableAssets": "Unknown Type: double",
                                "totalAssets": "Unknown Type: double",
                                "availableAssetLocation": "Unknown Type: double",
                                "totalAssetLocation": "Unknown Type: double",
                                "managedViolations": "Unknown Type: double",
                                "predictedViolations": "Unknown Type: double",
                                "executedViolations": "Unknown Type: double",
                                "nonPredictedViolations": "Unknown Type: double",
                                "consideredOffers": "Unknown Type: double",
                                "totalOffers": "Unknown Type: double",
                                "consideredOfferLocation": "Unknown Type: double",
                                "totalOfferLocation": "Unknown Type: double",
                                "managedOfferViolations": "Unknown Type: double",
                                "predictedOfferViolations": "Unknown Type: double",
                                "executedOfferViolations": "Unknown Type: double",
                                "nonPredictedOfferViolations": "Unknown Type: double",
                                "interactionNumber": "int",
                                "totalInteractionNumber": "int",
                                "feedbackNumber": "int",
                                "feedbackOfferNumber": "int",
                                "location": "Unknown Type: geographicalAddress",
                                "validFor": "Unknown Type: timePeriod"
                            },
                            "indirect_parameters": {
                                "recommendation_weighting": "Unknown Type: double",
                                "recommendations": "Unknown Type: recommendationlist"
                            },
                            "offerDID": {
                                "type": "string"
                            }
                        },
                        "trustee": {
                            "trusteeDID": "string",
                            "recommendation": {
                                "recommender": "string",
                                "trust_level": "Unknown Type: double",
                                "location": "Unknown Type: geographicalAddress"
                            },
                            "offerDID": {
                                "type": "string"
                            },
                            "trusteeSatisfaction": "double"
                        },
                        "trust_value": "double",
                        "currentInteractionNumber": "int",
                        "evaluation_criteria": "Inter-domain",
                        "initEvaluationPeriod": "Unknown Type: timestamp",
                        "endEvaluationPeriod": "Unknown Type: timestamp"
                    }

        return general_JSON

    def trustTemplate2(self):
        """This methods introduces the general Trust template that will be used in order to generate a dataset,
    and also to compute new trust scores and provide recomendations """
        general_JSON = {
            "trustor": {
                "trustorDID": "string",
                "trusteeDID": "string",
                "credibility": "Unknown Type: double",
                "transactionFactor": "Unknown Type: double",
                "communityFactor": "Unknown Type: double",
                "trust_propagation": True,
                "trust_update": "Unknown",
                "trust_evaluation": "PeerTrust",
                "direct_parameters": {
                    "direct_weighting": "Unknown Type: double",
                    "userSatisfaction": "Unknown Type: double",
                    "providerSatisfaction": "Unknown Type: double",
                    "PSWeighting": "Unknown Type: double",
                    "offerSatisfaction": "Unknown Type: double",
                    "OSWeighting": "Unknown Type: double",
                    "providerReputation": "Unknown Type: double",
                    "offerReputation": "Unknown Type: double",
                    "availableAssets": "Unknown Type: double",
                    "totalAssets": "Unknown Type: double",
                    "availableAssetLocation": "Unknown Type: double",
                    "totalAssetLocation": "Unknown Type: double",
                    "managedViolations": "Unknown Type: double",
                    "predictedViolations": "Unknown Type: double",
                    "executedViolations": "Unknown Type: double",
                    "nonPredictedViolations": "Unknown Type: double",
                    "consideredOffers": "Unknown Type: double",
                    "totalOffers": "Unknown Type: double",
                    "consideredOfferLocation": "Unknown Type: double",
                    "totalOfferLocation": "Unknown Type: double",
                    "managedOfferViolations": "Unknown Type: double",
                    "predictedOfferViolations": "Unknown Type: double",
                    "executedOfferViolations": "Unknown Type: double",
                    "nonPredictedOfferViolations": "Unknown Type: double",
                    "interactionNumber": "int",
                    "totalInteractionNumber": "int",
                    "feedbackNumber": "int",
                    "feedbackOfferNumber": "int",
                    "location": "Barcelona, Spain",
                },
                "indirect_parameters": {
                    "recommendation_weighting": "Unknown Type: double",
                },
                "offerDID": {
                    "type": "string"
                }
            },
            "trustee": {
                "trusteeDID": "string",
                "offerDID": {
                    "type": "string"
                },
                "trusteeSatisfaction": "double"
            },
            "trust_value": "double",
            "currentInteractionNumber": "int",
            "evaluation_criteria": "Inter-domain",
            "initEvaluationPeriod": "Unknown Type: timestamp",
            "endEvaluationPeriod": "Unknown Type: timestamp"
        }

        return general_JSON

    def trustTemplate3(self):
        """This methods introduces the general Trust template that will be used for MongoDB in order to retrieve objects
         with the fields ordered """
        general_JSON = {
            "trustor": {
                "trustorDID": 1,
                "trusteeDID": 1,
                "credibility": 1,
                "transactionFactor": 1,
                "communityFactor": 1,
                "trust_propagation": 1,
                "trust_update": 1,
                "trust_evaluation": 1,
                "direct_parameters": {
                    "direct_weighting": 1,
                    "userSatisfaction": 1,
                    "providerSatisfaction": 1,
                    "PSWeighting": 1,
                    "offerSatisfaction": 1,
                    "OSWeighting": 1,
                    "providerReputation": 1,
                    "offerReputation": 1,
                    "availableAssets": 1,
                    "totalAssets": 1,
                    "availableAssetLocation": 1,
                    "totalAssetLocation": 1,
                    "managedViolations": 1,
                    "predictedViolations": 1,
                    "executedViolations": 1,
                    "nonPredictedViolations": 1,
                    "consideredOffers": 1,
                    "totalOffers": 1,
                    "consideredOfferLocation": 1,
                    "totalOfferLocation": 1,
                    "managedOfferViolations": 1,
                    "predictedOfferViolations": 1,
                    "executedOfferViolations": 1,
                    "nonPredictedOfferViolations": 1,
                    "interactionNumber": 1,
                    "totalInteractionNumber": 1,
                    "feedbackNumber": 1,
                    "feedbackOfferNumber": 1,
                    "location": 1,
                    "validFor": 1
                },
                "indirect_parameters": {
                    "recommendation_weighting": 1,
                    "recommendations": 1
                },
                "offerDID": {
                    "type": 1
                }
            },
            "trustee": {
                "trusteeDID": 1,
                "recommendation": {
                    "recommender": 1,
                    "trust_level": 1,
                    "location": 1
                },
                "offerDID": {
                    "type": 1
                },
                "trusteeSatisfaction": 1
            },
            "trust_value": 1,
            "currentInteractionNumber": 1,
            "evaluation_criteria": 1,
            "initEvaluationPeriod": 1,
            "endEvaluationPeriod": 1
        }

        return general_JSON
