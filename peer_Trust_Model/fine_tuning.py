import numpy as np
import fuzzy_sets
import csv



def fine_tuning_reward():
    trust_score = 0.43008959207166125
    SLA_rate = 2.4609
    metric = "availability"
    header = ['Forgetting_Factor', 'New_SLAVRRate', "Historical_SLAVRate_Start", "Number_Current_Violations", "Updated_trust_score", "N"]

    RP_SLA = {metric+'_violations': 2.456, metric+'_historical_violation': 2.456}

    with open ('fine_tuning_reward.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        for n in range(1, 11):
            for eigen_factor in np.arange(0.01,1.0,0.01):
                trust_score = 0.43008959207166125
                number_iterations = 1
                SLA_rate = 2.4609
                writer.writerow(["{:.3f}".format(eigen_factor), "2.456", "2.456", number_iterations, 0.749, n])
                number_iterations+=1
                writer.writerow(["{:.3f}".format(eigen_factor), SLA_rate, "2.456", number_iterations, trust_score, n])
                while (trust_score < 0.74):
                    SLA_rate = ((SLA_rate * number_iterations) + (eigen_factor * SLA_rate)) / (number_iterations + 1)
                    trust_score = trust_score + eigen_factor * ((1-trust_score)/n)
                    number_iterations += 1
                    writer.writerow(["{:.3f}".format(eigen_factor), SLA_rate, "2.456", number_iterations, trust_score, n])
            #writer.writerow(["{:.3f}".format(eigen_factor), SLA_rate, "2.456", number_iterations, final_result, n])

def fine_tuning_SLAVRate():
    offerDID = "JZ7RGGdeimrxZraEvv59Qm"
    metric = "availability"
    last_offset_violations = 1
    n_total_interactions_SLAV_rate = 100
    n_total_interactions = 0
    violation_notification_list = []
    violation_list = []
    last_trust_score = 0.749
    BPRate = 0.378
    ITrust = 0.879
    updated_trust_score = 0

    header = ['Forgetting_Factor', 'New_SLAVRRate', "Previous_SLAVRRate", "Historical_SLAVRate_Start","Number_Current_Violations", "Number_interactions", "Last_trust_score", "Updated_trust_score", "N"]

    RP_SLA = {metric+'_violations': 2.456, metric+'_historical_violation': 2.456}
    message = {
        "id": "uuidv4()",
        "productDID": offerDID,
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

    for i in range(4):
        violation_notification_list.append(message)

    violation_list.append(metric)
    with open ('fine_tuning.csv', 'w', encoding='UTF8') as f:

        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        for n in range(1, 11):
            for eigen_factor in np.arange(0.1,1.0,0.01):
                writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(RP_SLA[metric+'_violations']), RP_SLA[metric+'_historical_violation'], len(violation_notification_list), n_total_interactions, last_trust_score, last_trust_score, n])
                current_sla_rate = sla_violation_rate(eigen_factor, last_offset_violations, RP_SLA, violation_notification_list, violation_list, n_total_interactions_SLAV_rate)
                n_total_interactions+=1
                RP_SLA[metric+'_violations'] = current_sla_rate

                while (current_sla_rate <= float(len(violation_notification_list))):
                    #print("Eigen_Factor: ","{:.3f}".format(eigen_factor), "-- New SLAVRRate: ", "{:.4f}".format(RP_SLA[metric+'_violations']), "-- Previous SLAVRRate: ","{:.4f}".format(current_sla_rate), "-- Number_Current_Violations:", len(violation_notification_list), "-- Number_interactions: ", n_total_interactions)
                    punishment = (BPRate + ITrust * current_sla_rate)/2
                    updated_trust_score = last_trust_score - punishment * ((1-last_trust_score)/n)
                    writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), RP_SLA[metric+'_historical_violation'], len(violation_notification_list), n_total_interactions, last_trust_score, updated_trust_score, n])
                    current_sla_rate = sla_violation_rate(eigen_factor, last_offset_violations, RP_SLA, violation_notification_list, violation_list, n_total_interactions_SLAV_rate)
                    n_total_interactions+=1
                    RP_SLA[metric+'_violations'] = current_sla_rate

                writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), RP_SLA[metric+'_historical_violation'], len(violation_notification_list), n_total_interactions, last_trust_score, updated_trust_score, n])
                n_total_interactions = 0
                RP_SLA[metric+'_violations'] =  2.456

            punishment = (BPRate + ITrust * current_sla_rate)/2

            """if current_sla_rate > float(len(violation_notification_list)):
                    #print("Current SLA: ", int(current_sla_rate), "-- New SLA: ", len(violation_list))
                    RP_SLA[metric+'_violations'] = current_sla_rate
                    print("Eigen_Factor: ","{:.3f}".format(eigen_factor), "-- New SLAVRRate: ", "{:.4f}".format(RP_SLA[metric+'_violations']), "-- Previous SLAVRRate: ","{:.4f}".format(current_sla_rate), "-- Number_Current_Violations:", len(violation_notification_list), "-- Number_interactions: ", n_total_interactions)
                    writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), len(violation_notification_list), n_total_interactions])
                    break
                else:
                    print("Eigen_Factor: ","{:.3f}".format(eigen_factor), "-- New SLAVRRate: ", "{:.4f}".format(RP_SLA[metric+'_violations']), "-- Previous SLAVRRate: ","{:.4f}".format(current_sla_rate), "-- Number_Current_Violations:", len(violation_notification_list), "-- Number_interactions: ", n_total_interactions)
                    writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), len(violation_notification_list), n_total_interactions])
                    n_total_interactions+=1
                    RP_SLA[metric+'_violations'] = current_sla_rate"""
            updated_trust_score = last_trust_score - punishment * ((1-last_trust_score)/n)
            writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), RP_SLA[metric+'_historical_violation'], len(violation_notification_list), n_total_interactions, last_trust_score, updated_trust_score, n])


def fine_tuning_specific_value(given_eigen_factor,number_interactions, N):
    offerDID = "JZ7RGGdeimrxZraEvv59Qm"
    metric = "availability"
    last_offset_violations = 1
    n_total_interactions_SLAV_rate = 100
    n_total_interactions = 0
    violation_notification_list = []
    violation_list = []
    last_trust_score = 0.749
    BPRate = 0.378
    ITrust = 0.879
    updated_trust_score = 0

    header = ['Forgetting_Factor', 'New_SLAVRRate', "Previous_SLAVRRate", "Historical_SLAVRate_Start","Number_Current_Violations", "Number_interactions", "Last_trust_score", "Updated_trust_score", "N"]

    RP_SLA = {metric+'_violations': 2.456, metric+'_historical_violation': 2.456}
    message = {
        "id": "uuidv4()",
        "productDID": offerDID,
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

    for i in range(6):
        violation_notification_list.append(message)

    violation_list.append(metric)
    with open ('fine_tuning_specific_value'+str(N)+'_'+str(given_eigen_factor)+'.csv', 'w', encoding='UTF8') as f:

        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        for n in range(N, N+1):
            for eigen_factor in np.arange(given_eigen_factor,given_eigen_factor+0.01,0.01):
                writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(RP_SLA[metric+'_violations']), RP_SLA[metric+'_historical_violation'], len(violation_notification_list), n_total_interactions, last_trust_score, last_trust_score, n])
                current_sla_rate = sla_violation_rate(eigen_factor, last_offset_violations, RP_SLA, violation_notification_list, violation_list, n_total_interactions_SLAV_rate)
                n_total_interactions+=1
                RP_SLA[metric+'_violations'] = current_sla_rate

                while (n_total_interactions <= number_interactions):
                    #print("Eigen_Factor: ","{:.3f}".format(eigen_factor), "-- New SLAVRRate: ", "{:.4f}".format(RP_SLA[metric+'_violations']), "-- Previous SLAVRRate: ","{:.4f}".format(current_sla_rate), "-- Number_Current_Violations:", len(violation_notification_list), "-- Number_interactions: ", n_total_interactions)
                    punishment = (BPRate + ITrust * current_sla_rate)/2
                    updated_trust_score = last_trust_score - punishment * ((1-last_trust_score)/n)
                    writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), RP_SLA[metric+'_historical_violation'], len(violation_notification_list), n_total_interactions, last_trust_score, updated_trust_score, n])
                    current_sla_rate = sla_violation_rate(eigen_factor, last_offset_violations, RP_SLA, violation_notification_list, violation_list, n_total_interactions_SLAV_rate)
                    n_total_interactions+=1
                    RP_SLA[metric+'_violations'] = current_sla_rate

                writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), RP_SLA[metric+'_historical_violation'], len(violation_notification_list), n_total_interactions, last_trust_score, updated_trust_score, n])
                n_total_interactions = 0
                RP_SLA[metric+'_violations'] =  2.456

            punishment = (BPRate + ITrust * current_sla_rate)/2

            """if current_sla_rate > float(len(violation_notification_list)):
                    #print("Current SLA: ", int(current_sla_rate), "-- New SLA: ", len(violation_list))
                    RP_SLA[metric+'_violations'] = current_sla_rate
                    print("Eigen_Factor: ","{:.3f}".format(eigen_factor), "-- New SLAVRRate: ", "{:.4f}".format(RP_SLA[metric+'_violations']), "-- Previous SLAVRRate: ","{:.4f}".format(current_sla_rate), "-- Number_Current_Violations:", len(violation_notification_list), "-- Number_interactions: ", n_total_interactions)
                    writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), len(violation_notification_list), n_total_interactions])
                    break
                else:
                    print("Eigen_Factor: ","{:.3f}".format(eigen_factor), "-- New SLAVRRate: ", "{:.4f}".format(RP_SLA[metric+'_violations']), "-- Previous SLAVRRate: ","{:.4f}".format(current_sla_rate), "-- Number_Current_Violations:", len(violation_notification_list), "-- Number_interactions: ", n_total_interactions)
                    writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), len(violation_notification_list), n_total_interactions])
                    n_total_interactions+=1
                    RP_SLA[metric+'_violations'] = current_sla_rate"""
            updated_trust_score = last_trust_score - punishment * ((1-last_trust_score)/n)
            writer.writerow(["{:.3f}".format(eigen_factor), "{:.4f}".format(RP_SLA[metric+'_violations']), "{:.4f}".format(current_sla_rate), RP_SLA[metric+'_historical_violation'], len(violation_notification_list), n_total_interactions, last_trust_score, updated_trust_score, n])



def sla_violation_rate(eigen_factor, last_offset_violations, RP_SLA, violation_notification_list, violation_list, n_total_interactions_SLAV_rate):
    "Sliding window weighting with respect to the forgetting factor"
    global newSLAViolation

    TOTAL_RW = eigen_factor
    NOW_RW = 1 - TOTAL_RW

    SLAV_rate_per_metric = {}

    if last_offset_violations == 0:
        for violation_notification in violation_notification_list:
            type_metric = violation_notification["rule"]["metric"]
            if type_metric not in RP_SLA:
                RP_SLA[type_metric+'_violations'] = 1
            else:
                RP_SLA[type_metric+'_violations'] +=1

        for violation in violation_list:
            SLAV_rate_per_metric[violation+'_violations'] = RP_SLA[violation+'_violations']

        if len(violation_list) > 0:
            newSLAViolation = True

        return SLAV_rate_per_metric

    for violation in violation_list:
        "Computing SLAVRate^t(u,m)"
        "Update the violation of a metric depending on if it previously had measured in the system"
        if violation+'_violations' in RP_SLA:
            previous_SLAVRate = RP_SLA[violation+'_violations']
        else:
            previous_SLAVRate = 0

        new_SLAViolations = 0
        for violation_notification in violation_notification_list:
            if violation_notification["rule"]["metric"] == violation:
                new_SLAViolations = new_SLAViolations + 1
                newSLAViolation = True

        if previous_SLAVRate == 0:
            #SLAV_rate_per_metric[violation+'_violations'] = new_SLAViolations
            new_SLAViolations
        else:
            #new_SLAVRate = TOTAL_RW * previous_SLAVRate + NOW_RW * (increment(new_SLAViolations, previous_SLAVRate)* fuzzy_sets.violation_fuzzy_set(new_SLAViolations, previous_SLAVRate))
            new_SLAVRate = ((previous_SLAVRate * n_total_interactions_SLAV_rate) + (TOTAL_RW * (increment(new_SLAViolations, previous_SLAVRate)* fuzzy_sets.violation_fuzzy_set(new_SLAViolations, previous_SLAVRate))))/(n_total_interactions_SLAV_rate)
            #SLAV_rate_per_metric[violation+'_violations'] = new_SLAVRate
            #print("Eigen_Factor: ","{:.1f}".format(eigen_factor), "-- New SLAVRRate: ", "{:.2f}".format(new_SLAVRate), "-- Previous SLAVRRate: ",previous_SLAVRate, "-- Number_Current_Violations:", len(violation_notification_list), "-- Increment: ", increment(new_SLAViolations, previous_SLAVRate), "-- Fuzzy_set: ", fuzzy_sets.violation_fuzzy_set(new_SLAViolations, previous_SLAVRate))

    return new_SLAVRate/len(violation_list)

def increment(new_SLAViolations, previous_SLAVRate):
    if new_SLAViolations > previous_SLAVRate:
        return new_SLAViolations/previous_SLAVRate
    return 0


fine_tuning_reward()
#fine_tuning_SLAVRate()
#fine_tuning_specific_value(0.6,1000, 5)
#fine_tuning_specific_value(0.6,1000, 4)
#fine_tuning_specific_value(0.65,1000, 5)
#fine_tuning_specific_value(0.65,1000, 4)
