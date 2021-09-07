
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
