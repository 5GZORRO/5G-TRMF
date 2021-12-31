import json
import requests
import glob
import re
import ast
import rstr
import time
import os
import subprocess
import csv


usage_headers = ["timestamp","cpu_usage","memory_usage", "receive_network_usage", "transmit_network_usage", "offers"]
usage_file_name = 'tests/usage.csv'

while True:
    initial_timestamp = time.time()

    if not os.path.exists("tests"):
        os.makedirs("tests")

    #usage = subprocess.Popen("kubectl top pods trmf-76448bb879-n6gw6 -n domain-operator-a | tail -n +2", shell=True, stdout=subprocess.PIPE).stdout
    usage_1 = subprocess.Popen("kubectl get --raw /f44b61bf0bc2233923d4b5dea273d379/apis/metrics.k8s.io/v1beta1/namespaces/domain-operator-a/pods/trmf-76448bb879-n6gw6", shell=True, stdout=subprocess.PIPE).stdout
    #os.system("kubectl top pods trmf-76448bb879-n6gw6 -n domain-operator-a | tail -n +2 | cut -d " " -f 2- > tests/usage.txt")
    usage_json = json.loads(usage_1.read().decode())

    #print(usage_json["containers"][0]["usage"]["cpu"])
    #print(usage_json["containers"][0]["usage"]["memory"])
    #usage = usage.read().decode()
    #usage = ' '.join(usage.split())

    milicores = usage_json["containers"][0]["usage"]["cpu"]
    milicores = round(int(milicores.replace("n", ""))/1000000000, 3)

    memory = usage_json["containers"][0]["usage"]["memory"]
    #We are converting to MiB
    memory = round(int(memory.replace("Ki", ""))*0.000976563, 3)

    print("%CPU: ", milicores, "memory MiB: ", memory)

    if not os.path.exists(usage_file_name):
        with open(usage_file_name, 'w', encoding='UTF8', newline='') as time_data:
            writer = csv.DictWriter(time_data, fieldnames=usage_headers)
            writer.writeheader()
            data = {"timestamp": initial_timestamp, "cpu_usage": milicores,"memory_usage": memory,
                    "receive_network_usage": 0, "transmit_network_usage": 0, "offers": 1000}
            writer.writerow(data)
    else:
        with open(usage_file_name, 'a', encoding='UTF8', newline='') as time_data:
            writer = csv.DictWriter(time_data, fieldnames=usage_headers)
            data = {"timestamp": initial_timestamp, "cpu_usage": milicores,"memory_usage": memory,
                    "receive_network_usage": 0, "transmit_network_usage": 0, "offers": 1000}
            writer.writerow(data)

    time.sleep(30)