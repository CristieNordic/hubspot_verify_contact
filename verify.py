# Import all modukes that needed for this solution

import requests
import json
import urllib
import os
import pandas as pd
from dns import resolver
import re
import socket
import smtplib

# Import Configuration
from config import apikey as hapikey
from config import smtp_host
from config import filename
from config import my_email
from config import list_url
from config import contact_info as contact_info_url

# Setup configuration

offset = 0
count = 250
has_more = True
headers = {}

np_none = []
np_success = []
np_bad = []

hs_contact_url = []
hs_vid = []
email_list = []
smtp_list = []

# Creating couple of internal functions.
def verify_email(email_address):
    """ Verify if it is a true email """
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_address)
    if match == None:
        return(False)
    else:
        return(True)

def get_domain(email_address):
    """ Split out the domian from the meial address """
    return (email_address.split('@'))

def get_smtp_server(domain):
    """ Find our the MX record and the SMTP Server for the domain """
    try:
        mx_record = resolver.query(domain, 'MX')
        exchanges = [exchange.to_text().split() for exchange in mx_record]
    except (resolver.NoAnswer, resolver.NXDOMAIN, resolver.NoNameservers):
        exchanges = None

    return (exchanges)

def dump_to_file(filename, data):
    """ Funtion to dump out the data to a CSV file """
    data.to_csv(filename, index=True)
    print ('*' * 100)
    print('Save all data in to file: ' + filename)
    print ('\n')
    return(True)

def get_contacts(url, count, offset):
    """ Collect all details who belongs to the list """
    parameter_dict = {'hapikey': hapikey, 'includeAssociations': 'true', 'count': count, 'vidOffset': offset}
    parameters = urllib.parse.urlencode(parameter_dict)
    get_url = url + parameters
    r = requests.get(url= get_url, headers = headers)
    return(json.loads(r.text))

def welcome():
    print ('\n')
    print ('*' * 47)
    print ('**  Created by Christian @ Cristie Nordic AB **')
    print ('*' * 47)
    print ('\n')

def sleep(delay):
    """ Created a Sleep function because of Hubspot API and SMTP Server timeout some times """
    import time
    time.sleep(delay)

def get_contact_details(url, vid):
    """ Get all contact details from Hubspot per contact """
    parameter_dict = {'hapikey': hapikey, 'includeAssociations': 'true'}
    parameters = urllib.parse.urlencode(parameter_dict)
    get_url = url + '/' + vid + '/profile?' + parameters
    r = requests.get(url= get_url, headers = headers)
    return(json.loads(r.text))

### Software starts ###

welcome()

""" Collect data who belongs to the Quarantine list """
while has_more:
    contacts = get_contacts(list_url, count, offset)
    subject = 'vid,url'
    has_more = contacts['has-more']
    for c in contacts['contacts']:
        contact_url = c['profile-url']
        offset = c['vid']
        hs_contact_url.append(contact_url)
        hs_vid.append(offset)
        #data = str(offset)+ "," + str(contact_url)
    offset += 1

print ('*' * 100)
print('Finding number of contacts in the list: ' + str(len(hs_vid)))
print ('\n')

data = pd.DataFrame(list(zip(hs_vid, hs_contact_url)), columns=['vid','url'])

""" Creating the email list to validate """
email_list = []
for vid in data['vid']:
    subject = 'email'
    try:
        contact_info = get_contact_details(contact_info_url, str(vid))
        email_list.append(contact_info['properties']['email']['value'])
    except:
        sleep(30)
        contact_info = get_contact_details(contact_info_url, str(vid))
        email_list.append(contact_info['properties']['email']['value'])

data['email'] = email_list

""" Building and verify the email address """
smtp_list = []
for e in data['email']:
    email_status = verify_email(e)
    subject = 'smtp'
    if email_status == False:
        print('*' * 100)
        print('Email address ' + e + ' is not a working email')
        print('*' * 100)
        smtp_srv = None
    else:
        try:
            domain = get_domain(e)
            smtp_servers = get_smtp_server(domain[1])
        except:
            smtp_servers = None

        if smtp_servers == None:
            sleep(30)
            try:
                domain = get_domain(e)
                smtp_servers = get_smtp_server(domain[1])
                for s in smtp_servers:
                    smtp_srv = s[1]
            except:
                smtp_srv = None

        else:
            for s in smtp_servers:
                smtp_srv = s[1]
    smtp_list.append(smtp_srv)

print ('*' * 100)
print('Number of the contact connected with a SMTP Servers: ' + str(len(smtp_list)))
print ('\n')

data['smtp'] = smtp_list

# SMTP lib setup (use debug level for full output)
server = smtplib.SMTP()
server.set_debuglevel(0)

"""  Verify the email with their SMTP Server """
for index, row in data.iterrows():
    if row['smtp'] == None:
        np_none.append(1)
        np_success.append(0)
        np_bad.append(0)
    else:
        # SMTP Conversation
        try:
            server.connect(row['smtp'])
            server.helo(smtp_host)
            server.mail(my_email)
            code, message = server.rcpt(str(row['email']))
            server.quit()

            # Assume 250 as Success
            if code == 250:
                np_none.append(0)
                np_success.append(1)
                np_bad.append(0)
            else:
                np_none.append(0)
                np_success.append(0)
                np_bad.append(1)
        except:
            np_none.append(1)
            np_success.append(0)
            np_bad.append(0)

data['Success'] = np_success
data['Bad'] = np_bad
data['None'] = np_none

dump_to_file(filename, data)
