import requests
import logging
import os
from exceptions import RootCredentialsException, RootIdentificationException

logging.basicConfig(level=logging.DEBUG)


class Client:
    def __init__(self, api_key=False):
        """Provide an interface to access the Root Insurance API.

        With an interface, client=Client(), one can get
        1. Quotes (client.quotes), such as for Gadgets (client.gadgets)
        2. Policy Holders  (client.policyholders)
        3. Applications (client.applications)
        4. Policies (client.policies)


        :param api_key:
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
        self.gadgets = Gadgets(self)
        self.quotes = Quotes(self)
        if not self.api_key:
            raise RootCredentialsException
        print("[{warning}] Running in production mode: {mode}".format(warning="WARNING" if self.production else "INFO",
                                                                      mode=self.production))

    def call(self, method, path, params=None, **kwargs):
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


class Resource(object):
    """
    Super class for
    """

    def __init__(self, client, method, path):
        self.client = client
        self.method = method
        self.path = path

    def call(self, method=None, path="", params=None, **kwargs):
        if method is None:
            method = self.method
        full_path = "{}/{}".format(self.path, path) if path != "" else self.path
        return self.client.call(method, full_path, params, **kwargs)


class Person(object):
    """An object for a person's details in the format the Root Insurance API wants

    # create object
    >>> person = Person(Person.id_data('id','6801015800084','ZA'),...)
    # send in correct format using
    >>> data = person.details()
    >>> data['extra'] = 'extra details'
    >>> Resource.call(json=data)

    """

    def __init__(self, id_object, first_name, last_name, date_of_birth=None, gender=None, email=None, cellphone=None,
                 *args, **kwargs):
        if not ('type' in id_object and 'number' in id_object and 'country' in id_object):
            raise RootIdentificationException()

        self._details = {'id': id_object,
                         'first_name': first_name,
                         'last_name': last_name}
        if date_of_birth is not None:
            self._details['date_of_birth'] = date_of_birth
        if gender is not None:
            self._details['gender'] = gender
        if email is not None:
            self._details['email'] = email
        if cellphone is not None:
            self._details['cellphone'] = cellphone
        for kw, val in kwargs.items():
            self._details[kw] = val

    @staticmethod
    def id_data(id_type: str, id_num: str, country_code: str):
        """Helper method to correctly form the 'id' object dict

        Example:
            person = Person(Person.id_data('id','6801015800084','ZA'),...)

        API docs:
        type        string. Either 'id' or 'passport'.
        number      string. The ID or passport number.
        country     string. The ISO Alpha-2 country code of the country of the id/passport number.
        """
        if id_type != 'id' and id_type != 'passport':
            raise RootIdentificationException("identification id_type was neither 'id' nor 'passport'")
        assert len(country_code) == 2
        return {'type': id_type,
                'number': id_num,
                'country': country_code}

    def details(self):
        return self._details


class Beneficiary(Person):
    def __init__(self, percentage=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 0 <= percentage <= 100
        self._details['percentage'] = percentage


class Gadgets(Resource):
    def __init__(self, client):
        super().__init__(client, "get", "modules/root_gadgets/models")

    def list_models(self):
        """ List the models available in the root_gadgets module
        :return: list of models available, each model is in dict format with keys 'make','name','value'
        """
        return self.call()

    def list_phone_brands(self):
        models = self.list_models()
        return set([phone['make'] for phone in models])

    def list_phones_by_brand(self, brand):
        models = self.list_models()
        return set([phone['name'] for phone in models if phone['make'] == brand])

    def get_phone_value(self, phone):
        models = self.list_models()
        return list(filter(lambda p: p['name'] == phone, models))[0]['value'] / 100


class Quotes(Resource):
    def __init__(self, client):
        super().__init__(client, "post", "quotes")
        self.gadget_create = self.module_create("root_gadgets")
        self.funeral_create = self.module_create("root_funeral")
        self.term_create = self.module_create("root_term")

    def module_create(self, module_id=None):
        def create(opts):
            nonlocal module_id
            data = {}
            if module_id is None:
                module_id = opts["type"]
            if module_id == "root_gadgets":
                data = self.gadget_data(opts)
            elif module_id == "root_term":
                data = self.term_data(opts)
            elif module_id == "root_funeral":
                data = self.funeral_data(opts)
            else:
                raise Exception("invalid quote type")
            return self.call(json=data)

        return create

    @staticmethod
    def gadget_data(opts):
        return {
            "type": "root_gadgets",
            "model_name": opts["model_name"]
        }

    @staticmethod
    def term_data(opts):
        return {
            "type": "root_term",
            "cover_amount": opts["cover_amount"],
            "cover_period": opts["cover_period"],
            "education_status": opts["education_status"],
            "smoker": opts["smoker"],
            "gender": opts["gender"],
            "age": opts["age"],
            "basic_income_per_month": opts["basic_income_per_month"],
        }

    @staticmethod
    def funeral_data(opts):
        return {
            "type": "root_funeral",
            "cover_amount": opts["cover_amount"],
            "has_spouse": opts["has_spouse"],
            "number_of_children": opts["number_of_children"],
            "extended_family_ages": opts["extended_family_ages"]  # integer list
        }


class Applications(Resource):
    def __init__(self, client):
        super().__init__(client, "post", "applications")

    def create(self, policyholder_id, quote_package_id, monthly_premium, serial_number=None):
        data = {
            "policyholder_id": policyholder_id,
            "quote_package_id": quote_package_id,
            "monthly_premium": monthly_premium,
            "serial_number": serial_number
        }
        return self.call(json=data)


class Claims(Resource):
    def __init__(self, client):
        super().__init__(client, "get", "claims")

    def list(self, status=None, approval=None):
        params = {}
        if status:
            params["claim_status"] = status
        params = {}
        if approval:
            params["approval_status"] = approval

        return self.call(params=params)

    def get(self, claim_id):
        return self.call('{claim_id}'.format(claim_id=claim_id))

    def open(self, policy_id=None, policy_holder_id=None):
        data = {
            "policy_id": policy_id,
            "policy_holder_id": policy_holder_id
        }
        return self.call("post", json=data)

    def link_policy(self, claim_id, policy_id):
        data = {
            "policy_id": policy_id
        }
        return self.call("post", '{claim_id}/policy'.format(claim_id=claim_id), json=data)

    def link_policy_holder(self, claim_id, policy_holder_id):
        data = {
            "policy_holder_id": policy_holder_id
        }
        return self.call("post", '{claim_id}/policyholder'.format(claim_id=claim_id), json=data)

    def link_events(self, claim_id):
        return self.call("post", '{claim_id}/events'.format(claim_id=claim_id))


class PolicyHolders(Resource):
    def __init__(self, client):
        super().__init__(client, "get", "policyholders")

    def list(self):
        return self.call()

    def get(self, policyholder_id):
        return self.call('{policyholder_id}'.format(policyholder_id=policyholder_id))

    def list_events(self, policyholder_id):
        return self.call('{policyholder_id}/events'.format(policyholder_id=policyholder_id))

    def create(self, policyholder: Person):
        data = policyholder.details()
        return self.call("post", json=data)

    def update(self, policyholder_id, email=None, cellphone=None):
        data = {
            "email": email,
            "cellphone": cellphone
        }
        return self.call("patch", '{policyholder_id}'.format(policyholder_id=policyholder_id), json=data)


class Policies(Resource):
    def __init__(self, client):
        super().__init__(client, "get", "policies")

    def list(self):
        return self.call()

    def get(self, policy_id):
        return self.call('{policy_id}'.format(policy_id=policy_id))

    def issue(self, application_id):
        data = {
            "application_id": application_id,
        }
        return self.call("post", json=data)

    def list_beneficiaries(self, policy_id):
        return self.call('{policy_id}/beneficiaries'.format(policy_id=policy_id))

    def list_events(self, policy_id):
        return self.call('{policy_id}/events'.format(policy_id=policy_id))

    def add_beneficiary(self, policy_id, beneficiaries: [Beneficiary]):
        """

        After a policy has been issued, the beneficiaries that will receive payment on a claim payout can be added.
        Updating a policy's beneficiaries replaces any beneficiaries added to the policy in the past.

        The number of beneficiaries that can be added and the details required for beneficiaries may differ depending
        on the insurance module type of the policy.

        When updating beneficiaries, the percentage of a claim payout
        that each beneficiary should receive must be provided. The sum of percentages for beneficiaries added must be
        100.

        :param policy_id:
        :param beneficiaries:

        """
        data = [beneficiary.details() for beneficiary in beneficiaries]
        total = sum([datum['percentage'] for datum in data])
        assert total == 100, "Beneficiary percentages must add to 100"
        return self.call("put", '{policy_id}/beneficiaries'.format(policy_id=policy_id), json=data)

    def cancel(self, policy_id, reason):
        data = {"reason": reason}
        return self.call("post", '{policy_id}/cancel'.format(policy_id=policy_id), json=data)

    def replace(self, policy_id, quote_package_id):
        data = {"quote_package_id": quote_package_id}
        return self.call("post", '{policy_id}/replace'.format(policy_id=policy_id), json=data)

    def update_billing_amount(self, policy_id, billing_amount):
        data = {"billing_amount": billing_amount}
        return self.call("post", '{policy_id}/billing_amount'.format(policy_id=policy_id), json=data)
