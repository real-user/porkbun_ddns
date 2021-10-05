import json
import requests
from requests.exceptions import ConnectionError
import re
import sys
import time
import os
import logging

def getRecords(domain):
    '''Grab all the records so we know which ones to delete to make room for our record. Also checks to make sure we've got the right domain'''
    allRecords=json.loads(requests.post(apiConfig["endpoint"] + '/dns/retrieve/' + domain, data = json.dumps(apiConfig)).text)
    if allRecords["status"]=="ERROR":
        log.info('Error getting domain. Check to make sure you specified the correct domain, and that API access has been switched on for this domain.');
        sys.exit();
    return(allRecords)
    
def getMyIP():
    '''Call Porkbun's API and return IP of the caller'''
    ping = json.loads(requests.post(apiConfig["endpoint"] + '/ping/', data = json.dumps(apiConfig)).text)
    return(ping["yourIp"])

def deleteRecord(rootDomain, fqdn):
    '''Delete a record in Porkbun'''
    for i in getRecords(rootDomain)["records"]:
        if i["name"]==fqdn and (i["type"] == 'A' or i["type"] == 'ALIAS' or i["type"] == 'CNAME'):
            log.info("Deleting existing " + i["type"] + " Record")
            deleteRecord = json.loads(requests.post(apiConfig["endpoint"] + '/dns/delete/' + rootDomain + '/' + i["id"], data = json.dumps(apiConfig)).text)

def createRecord(rootDomain, subDomain, fqdn, myIP):
    '''Create a new record in Porkbun with the IP address'''
    createObj=apiConfig.copy()
    createObj.update({'name': subDomain, 'type': 'A', 'content': myIP, 'ttl': 300})
    endpoint = apiConfig["endpoint"] + '/dns/create/' + rootDomain
    log.info("Creating record: " + fqdn + " with answer of " + myIP)
    create = json.loads(requests.post(apiConfig["endpoint"] + '/dns/create/'+ rootDomain, data = json.dumps(createObj)).text)
    return(create)

def run(myIP, rootDomain, subDomain=None):
    '''call Porkbun's API and point the domain to ip address'''
    if subDomain:
        fqdn=subDomain + "." + rootDomain
    else:
        subDomain=''
        fqdn=rootDomain
    deleteRecord(rootDomain, fqdn)
    status = createRecord(rootDomain, subDomain, fqdn, myIP)["status"]
    log.info(status)

def update_all_domains(ip_address, domains):
    '''update all domains to point to given ip address'''
    for domain in domains:
        run(ip_address, *domain)

def get_all_domains(domains_file):
    '''return list of domains to update'''
    domains = [line.split() for line in open(domains_file)]
    return domains

def load_porkbun_config(config):
    '''Load porkbun API config from file'''
    return json.load(open(config))

def get_logging():
    '''Set the logging and return the logger'''
    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO"),
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return(logging.getLogger("porkbun"))
    

def get_sleep_interval():
    '''Get user defined sleep interval from environment variable'''
    SLEEP=int(os.environ.get('SLEEP', '15'))
    log.info("Sleep interval set to %d minutes" % SLEEP)
    return(60*SLEEP)

def get_current_IP_address():
    '''Get user defined IP address from environment variable'''
    return(os.environ.get('CURRENT_IP', '1.1.1.1'))

def try_to_update_ip_address(new_IP_address, old_IP_address, domains):
    '''Updates the IP address if the IP has changed and return the currently used IP'''
    if not new_IP_address == old_IP_address:
        log.info('Public IP address have been updated from %s to %s' % (old_IP_address, new_IP_address))
        update_all_domains(new_IP_address, domains)
        old_IP_address = new_IP_address
    return(old_IP_address)

if __name__ == '__main__':
    log = get_logging()
    apiConfig = load_porkbun_config('config.json')
    domains = get_all_domains('domains.cfg')
    SLEEP = get_sleep_interval()
    old_IP_address = get_current_IP_address()

    while True:
        try:
            new_IP_address = getMyIP()
            old_IP_address = try_to_update_ip_address(new_IP_address, old_IP_address, domains)
        except ConnectionError as e:
            log.info("No connection to Porkbun API or Internet")
        time.sleep(SLEEP)
