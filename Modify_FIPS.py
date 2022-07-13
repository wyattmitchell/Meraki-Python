""" Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

import meraki
import csv
import datetime

# Instructions:
# Set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.
# Input CSV must have columns as: NetworkID, Name, FIPSEnabled (true/false)
 
def select_org(dashboard):
    # Fetch and select the organization
    print('\n\nFetching organizations...\n')
    organizations = dashboard.organizations.getOrganizations()
    organizations.sort(key=lambda x: x['name'])
    counter = 0
    print('Select org to query:')
    for organization in organizations:
        orgName = organization['name']
        print(f'{counter} - {orgName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the organization ID you would like to query: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Organization Number\n')
        except:
            print('\tInvalid Organization Number\n')
    return(organizations[int(selected)]['id'], organizations[int(selected)]['name'])

# ---- Begin Script ----

# Connect to dashboard, select org
dashboard = meraki.DashboardAPI(suppress_logging=True)
selected_org, orgName = select_org(dashboard)

# Prompt for input file
in_path = input('Enter CSV file name: ')

with open(in_path, 'r') as infile:
    rows = []
    try:
        csvreader = csv.reader(infile)
        csvheader = next(csvreader)
        for row in csvreader:
            rows.append(row)
        print(f'\n{in_path} imported. Continuing...\n')
    except:
        print(f'\nCould not open or read {in_path}. Exiting script.\n')

with open('logs/fips_log.txt', 'a') as logfile:
    for row in rows:
        # print(row)
        network_id = row[0]
        netName = row[1]
        fipsEnabled = row[2]
        try:
            netSettings = dashboard.networks.getNetworkSettings(network_id)
            fipsSet = {'enabled': fipsEnabled}
            response = dashboard.networks.updateNetworkSettings(networkId=network_id, fips=fipsSet)
            logfile.write(f'\n{datetime.datetime.now()} - {netName} set FIPS Mode to {fipsEnabled}.')
            print(f'Modified {netName} FIPS mode to {fipsEnabled}.')
        except Exception as error:
            with open('logs/' + 'fips_error.txt', 'a') as outfile:
                outfile.write(f'\n{datetime.datetime.now()} - Could not write {network_id} FIPS setting.\n')
                outfile.write(str(error))
                outfile.write('\n')
            print('Errors encountered. See error log.')
        
        