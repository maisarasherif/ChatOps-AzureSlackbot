# ChatOps-AzureSlackbot
## prerequisite
- A VM with managed identity
- Azure CLI (logged in)
- Python and Pip
- Flask (for development and testing only)
- Some python packages such as (msrest, msrestazure, azure-identity, azure-mgmt-compute, azure-mgmt-network)
- A Slack App configured and installed to a workspace with the following scopes: "chat: write" & "chat: write.public"
- configure a slack command with a Request URL "http://<your-VM-public-IP>:5000/execute" (add a firewall rule to allow traffic on port 5000 on the VM)
## run the script, the app is listening on port 5000
## send a POST request to the URL using the slack command or test it with CURL.
