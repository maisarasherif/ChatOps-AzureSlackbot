import os
import requests
from threading import Thread
from flask import Flask, request, jsonify
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)

SLACK_BOT_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxx'
SLACK_SIGNING_SECRET = 'xxxxxxxxxxxxxxxxxxxxx'
SLACK_CHANNEL_ID = 'xxxxxxxxxxxxxxxxx'

@app.route('/execute', methods=['GET', 'POST'])
def execute_script():

    response_url = request.form.get('response_url')

   # Send an immediate response to Slack
    response_message = {"response_type": "ephemeral", "text": "Processing your request..."}
    Thread(target=process_and_post_vms_to_slack, args=(response_url,)).start()
    return jsonify(response_message), 200

def process_and_post_vms_to_slack(response_url):
    subscription_id = 'xxxxxxxxxxxxxxxxxx'
        
    # Use DefaultAzureCredential for authentication
    credentials = DefaultAzureCredential()

    # Create the ComputeManagementClient and NetworkManagementClient
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)

    # List VMs in the subscription
    vm_list = compute_client.virtual_machines.list_all()
    results = []
    for vm in vm_list:
        # Get the network interface ID
        nic_id = vm.network_profile.network_interfaces[0].id
        nic = network_client.network_interfaces.get(
            resource_group_name=vm.id.split('/')[4],
            network_interface_name=nic_id.split('/')[-1]
            )

    # Get the public IP address
        if nic.ip_configurations[0].public_ip_address:
            public_ip_id = nic.ip_configurations[0].public_ip_address.id
            public_ip = network_client.public_ip_addresses.get(
                resource_group_name=vm.id.split('/')[4],
                public_ip_address_name=public_ip_id.split('/')[-1]
                )
            vm_details = {
                "name": vm.name,
                "size": vm.hardware_profile.vm_size,
                "os_type": vm.storage_profile.os_disk.os_type,
                "public_ip_address_name": public_ip.ip_address
            }
        else:
            vm_details = {
                "name": vm.name,
                "size": vm.hardware_profile.vm_size,
                "os_type": vm.storage_profile.os_disk.os_type,
                "public_ip_address_name": "None"
            }    

        results.append(vm_details)

    # Format the message for Slack
    slack_message = "VM Information:\n"
    for vm in results:
        slack_message += f"\n*Name:* {vm['name']}\n*Size:* {vm['size']}\n*OS:* {vm['os_type']}\n*IP_Adress:* {vm['public_ip_address_name']}\n"

    response_payload = {"text": slack_message}
    requests.post(response_url, json=response_payload)  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
