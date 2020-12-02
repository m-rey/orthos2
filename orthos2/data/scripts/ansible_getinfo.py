#!/usr/bin/python3
#
# Script to import dumped json facts of a system and map them to orthos attributes
# Obtain the dump directly via:
# ansible localhost -m setup > /tmp/ansible_facts.json
# 
# Alternatively, use the ansible playbook to gather the ansible facts:
# ansible-playbook site.yml
#
# Usage of this script:
# sudo -u orthos /usr/lib/orthos2/manage.py runscript set_serverconfig --script-args /tmp/data.serverconfig.json
#


import json
from orthos2.data.models.serverconfig import ServerConfig

def run(*args):
    if not args:
        print("Use --script-args to pass ansible_facts file")
        exit(1)
        
    with open(args[0], 'r') as json_file:
        ansible_machine = json.load(json_file)

   db_machine = Machine.object.get(fqdn=ansible_machine.get("fqdn"))
   db_machine.fqdn = ansible_machine["fqdn"]
   db_machine.serial_number = ansible_machine["product_serial"]
   db_machine.architecture = ansible_machine["architecture"]
   db_machine.cpu_cores = ansible_machine["processor_cores"]
   db_machine.ram_amount = ansible_machine["memory_mb"]["total"]
   db_machine.bios_version = ansible_machine["bios_version"]
   db_machine.mac_address = ansible_machine["default_ipv4"]["macaddress"]

   db_machine.save()
