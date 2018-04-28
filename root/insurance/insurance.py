import requests
import logging
import os
from root.insurance.exceptions import RootCredentialsException
from root.insurance.policyholder import Policyholder
from root.insurance.resources import GadgetCover, Applications, Claims, PolicyHolders, Policies

logging.basicConfig(level=logging.DEBUG)


class InsuranceClient(object):
    def __init__(self, api_key=False, cover=GadgetCover):
        """Provide an interface to access the Root Insurance API.

        With an interface, client=InsuranceClient(), one can get
        1. Quotes (client.quotes), such as for GadgetCover
        2. Policy Holders  (client.policyholders)
        3. Applications (client.applications)
        4. Policies (client.policies)

        To issue a policy follow these steps:
        0. Create an insurance client
        >>> client = InsuranceClient()
        1. Issue a quote for the thing to be insured.
        >>> quotes_data = client.quotes.generate(model_name="iPhone 6s 64GB LTE")
        2. Create a policy holder
        >>> policyholder = Policyholder(Policyholder.identification(...),...)
        >>> policyholder_data = client.policyholders.create(policyholder=policyholder)
        3. Create an application. For this, a generated quote is required.
        >>> chosen_quote = quotes_data[0]
        >>> chosen_quote_id = chosen_quote['quote_package_id']
        >>> policyholder_id = policyholder_data['policyholder_id']
        >>> application_data = client.applications.create(policyholder_id=policyholder_id,
                                                          quote_package_id=chosen_quote_id,
                                                          monthly_premium=chosen_quote['suggested_premium'],
                                                          serial_number='random_serial')
        4. Issue policy, if application is approved (this check is not done here)
        >>> policy_data = client.policies.issue(application_id=application_data['application_id'])
        5. Add beneficiaries
        >>> updated_policy_data = client.policies.add_beneficiary(policy_data['policy_id'],
                                                                 [Beneficiary(percentage=100.0,...)])
        6. Link credit card
        See API docs https://app.root.co.za/docs/insurance/api#linking-credit-card


        :param api_key: for those struggling with ENVIRONMENT VARIABLES, the key can be passed directly
                        WARNING: do *NOT* make the API_KEY publicly visible
        """
        self.sandbox = os.environ.get('ROOT_SANDBOX', True)
        self.production = False if self.sandbox else True
        self.prod_url = "https://api.root.co.za/v1/insurance"
        self.base_url = "https://sandbox.root.co.za/v1/insurance" if self.sandbox else self.prod_url
        self.api_key = os.environ.get('ROOT_API_KEY', api_key)
        self.applications = Applications(self)
        self.claims = Claims(self)
        self.policyholders = PolicyHolders(self)
        self.policies = Policies(self)
        self.quotes = cover(self)
        if not self.api_key:
            raise RootCredentialsException
        print("[{warning}] Running in production mode: {mode}".format(warning="WARNING" if self.production else "INFO",
                                                                      mode=self.production))

    def call(self, method: str, path: str, params: str = None, **kwargs):
        """Send a request to the Root API.
        :param method: any method supported by requests lib.
        :param path: url of api from root.co.za/{version}/insurance/{path}
        :param params: optional params
        :param kwargs: other keywords of note include 'json' for payload
        :return: JSON-like response
        """
        resp = requests.request(method,
                                '{base_url}/{path}'.format(base_url=self.base_url, path=path),
                                params=params,
                                headers={"Content-Type": "application/json"},
                                auth=(self.api_key, ""),
                                **kwargs
                                )
        if resp.status_code == requests.codes.ok:
            return resp.json()
        logging.error('{} {}'.format(resp.status_code, resp.text))
        if self.sandbox:
            resp.raise_for_status()
