import os
import logging
import requests
import json
import urllib
from fabric import Connection
from flask import request

def repository_changed():
    logging.debug('Event Received')
    post_json_data = request.get_data()
    string = str(post_json_data, 'utf-8')
    jsonFile = json.loads(string)
    pull_id = jsonFile["pull_request"]["head"]["sha"]
   url = 'https://raw.githubusercontent.com/MasterKr123/sd2018b-exam1/' + pull_id + '/packages.json'
    response = requests.get(url)
    packages_json = json.loads(response.content)
    install_packages = ""
    for i in packages_json:
        commands = i["commands"].split(";")
        for l in commands:
                install_packages = install_packages + " " + l
    text = Connection('vagrant@192.168.131.152').run('sudo yum install --downloadonly --downloaddir=/var/repo' + install_packages)
    logging.debug(text)
    result = {'command_return': 'Work!'}
    return result
