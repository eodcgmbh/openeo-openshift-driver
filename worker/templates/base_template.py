''' Base for OpenShift Templates '''

from os import environ
from json import dumps, loads
from requests import post, get
from re import match
from service.api.api_exceptions import TemplateError
from time import sleep
from abc import ABC, abstractmethod

class BaseTemplate(ABC):
    ''' Base Class for OpenShift Templates '''

    def __init__(self, namespace, template_id, path, kind, api_version):
        self.namespace = namespace
        self.template_id = template_id
        self.path = path.format(namespace)
        self.status = "Initialized"

        self.template = {
            "kind": kind,
            "apiVersion": api_version,
            "metadata": {
                "name": template_id
            }
        }

    def get_json(self):
        ''' Generates JSON from the member template '''
        return dumps(self.template)

    def create(self, token, watch=True):
        ''' Parses and send the template to the OpenShift API'''

        auth = {"Authorization": "Bearer " + token}
        verify = True if environ.get("VERIFY") == "true" else False

        # Execute template
        url = environ.get("OPENSHIFT_API") + self.path
        response = post(url, data=self.get_json(), headers=auth, verify=verify)

        if response.ok == False:
            self.raise_error(response.text)

        self.status = "Created"

        # Watch template execution till finish
        if watch:
            while True:
                # TODO: Paramters in config file
                sleep(0.5)

                url = "{0}{1}/{2}".format(environ.get("OPENSHIFT_API"), self.path, self.template_id)
                response = get(url, headers=auth, verify=verify)

                if response.ok == False:
                    self.raise_error(response.text)

                if self.check_status(loads(response.text), auth):
                    break

    @abstractmethod
    def check_status(self, response, auth=None):
        return True

    def raise_error(self, msg):
        self.status = "Error"
        print(msg)
        raise TemplateError(409, "Could not process " + self.template_id)

        
