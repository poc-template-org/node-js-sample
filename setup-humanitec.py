import requests
import os
import sys
import time

try:
    humanitec_token = os.environ['HUMANITEC_TOKEN']
    humanitec_org = os.environ['HUMANITEC_ORG']
    humanitec_app_id = os.environ['HUMANITEC_APP_ID']
    repository_name = os.environ['REPOSITORY_NAME']
    github_token = os.environ['GITHUB_TOKEN']
    github_org = os.environ['GITHUB_ORG']
except Exception as e:
    print(f"Error: Could not read {e} from environment.")
    print(f"Please export {e} as environment variable.")
    sys.exit()

humanitec_url = "api.humanitec.io"

headers = {
    'Authorization': f'Bearer {humanitec_token}',
    'Content-Type': 'application/json'
}

################################################################
# Get information about the image / module pushed to Humanitec #
################################################################
url = f"https://{humanitec_url}/orgs/{humanitec_org}/images/{repository_name}"
response = requests.request("GET", url, headers=headers)
if response.status_code == 200:
    image = response.json()['builds'][0]['image']
else:
    sys.exit(f"Unable to obtain module data. GET {url} returned status code {response.status_code}.")

############################
# Create application draft #
############################
url = f"https://{humanitec_url}/orgs/{humanitec_org}/apps"
payload = {
    "id": f'{humanitec_app_id}',
    "name": f'{humanitec_app_id}'
}
response = requests.request("POST", url, headers=headers, json=payload)
if response.status_code==201:
    print(f"The application {humanitec_app_id} has been created.")
elif response.status_code==409:
    sys.exit(f"Unable to create application. Application with id {humanitec_app_id} already exists.")
else:
    sys.exit(f"Unable to create application. POST {url} returned status code {response.status_code}.")

###########################################################
# Create an empty configuration delta for the application #
###########################################################
url = f"https://{humanitec_url}/orgs/{humanitec_org}/apps/{humanitec_app_id}/deltas"
payload = {
    "modules": {
            "add": {
                f"{repository_name}": {
                    "externals": {
                        "my-dns-resource": {
                            "type": "dns"
                        }
                    },
                    "profile": "humanitec/default-module",
                    "spec": {
                        "containers": {
                            f"{repository_name}": {
                                "files": {},
                                "id": f"{repository_name}",
                                "image": f"{image}",
                                "resources": {
                                    "limits": {
                                        "cpu": "0.250",
                                        "memory": "256Mi"
                                    },
                                    "requests": {
                                        "cpu": "0.025",
                                        "memory": "64Mi"
                                    }
                                },
                                "variables": {},
                                "volume_mounts": {}
                            }
                        },
                        "ingress": {
                            "rules": {
                                "externals.my-dns-resource": {
                                    "http": {
                                        "/": {
                                            "port": 3000,
                                            "type": "exact"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "remove": [],
            "update": {}
        },
    }

response = requests.request("POST", url, headers=headers, json=payload)
if response.status_code==200:
    print(f"The delta for application {humanitec_app_id} has been created.")
    delta_id = response.json()
else:
    sys.exit(f"Unable to create delta. POST {url} returned status code {response.status_code}.")

################################################
# Trigger the deployment of the delta          #
################################################
url = f"https://{humanitec_url}/orgs/{humanitec_org}/apps/{humanitec_app_id}/envs/development/deploys"
payload = {
    "delta_id": f"{delta_id}",
    "comment": f"initial deployment of {repository_name}"
}
response = requests.request("POST", url, headers=headers, json=payload)
if response.status_code==201:
    print(f"The deployment for application {humanitec_app_id} has been triggered.")
else:
    sys.exit(f"Unable to trigger deployment. POST {url} returned status code {response.status_code}.")

################################################
# Add an auto deployment rule                  #
################################################
url = f"https://{humanitec_url}/orgs/{humanitec_org}/apps/{humanitec_app_id}/envs/development/rules"
payload = {
    "active": True,
    "type": "update",
    "images_filter": [
        f"{repository_name}"
    ],
    "exclude_images_filter": False,
    "update_to": "branch",
    "match": ""
}
response = requests.request("POST", url, headers=headers, json=payload)
if response.status_code==201:
    print(f"The auto deployment rule for application {humanitec_app_id} has been created.")
else:
    sys.exit(f"Unable to create auto deployment rule. POST {url} returned status code {response.status_code}.")

##################################
# Check for deployment to finish #
##################################
url = f"https://{humanitec_url}/orgs/{humanitec_org}/apps/{humanitec_app_id}/envs/development"
deployment_status = ""
while deployment_status != "succeeded":
    time.sleep(2)
    response = requests.request("GET", url, headers=headers)
    if response.status_code==200:
        deployment_status = response.json()['last_deploy']['status']
        print(f"Status for deployment of {humanitec_app_id}: {deployment_status}")
        if {deployment_status} == "failed":
            sys.exit(f"Deployment failed.")
    else:
        sys.exit(f"Unable to get deployment status. GET {url} returned status code {response.status_code}.")

#################################################    
# Get application runtime status and obtain url #
#################################################
url = f"https://{humanitec_url}/orgs/{humanitec_org}/apps/{humanitec_app_id}/envs/development/resources"
response = requests.request("GET", url, headers=headers)
if response.status_code==200:
    for resource in response.json():
        if resource['type'] == "dns":
            app_url = resource['resource']['host']
            print(f"You can access your application now: https://{app_url}")
else:
    sys.exit(f"Unable to obtain runtime status. GET {url} returned status code {response.status_code}.")

#################################################    
# Set app url in the github repo description    #
#################################################
url = f"https://api.github.com/repos/{github_org}/{repository_name}"
headers = {
    'Authorization': f'Bearer {github_token}',
    'Content-Type': 'application/json'
}
payload = {
    "homepage":f"https://{app_url}"
}
response = requests.request("PATCH", url, headers=headers, json=payload)
if response.status_code==200:
    print(f"Updated the repository description.")
else:
    sys.exit(f"Unable to update the repository description. PATCH {url} returned status code {response.status_code}.")