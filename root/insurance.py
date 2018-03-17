import requests
import logging
import os

logging.basicConfig(level=logging.DEBUG)

class Client:
    def __init__(self):
        self.baseURL = "https://sandbox.root.co.za/v1/insurance"
        self.appID = os.environ.get('ROOT_APP_ID')
        self.appSecret = os.environ.get('ROOT_APP_SECRET')
        self.applications = Applications(self)
        self.claims = Claims(self)
        self.policyholders = PolicyHolders(self)
        self.policies = Policies(self)
        self.gadgets = Gadgets(self)
        self.quotes = Quotes(self)

    def call(self, method, path, params=None, **kwargs):
        resp = requests.request(method, f'{self.baseURL}/{path}', params=params, headers={"Content-Type": "application/json"}, auth=(self.appID, self.appSecret), **kwargs)
        if resp.status_code == 200 or resp.status_code == 201:
            return resp.json()
        raise Exception(resp.status_code, resp.json())


class Resource:
    def __init__(self, client):
        self.client = client
    
    def call(self, method, path, params=None, **kwargs):
        return self.client.call(method, path, params, **kwargs)


class Applications(Resource):
    def __init__(self, client):
         super().__init__(client)
    
    def create(self, policyholder_id, quote_package_id, monthly_premium, serial_number=None):
        data = {
            "policyholder_id":  policyholder_id,
            "quote_package_id": quote_package_id,
            "monthly_premium":  monthly_premium,
            "serial_number":    serial_number
        }
        return self.call("post", "applications", json=data)


class Claims(Resource):
    def __init__(self, client):
         super().__init__(client)

    def list(self, status=None, approval=None):
        params = {}
        if status:
            params["claim_status"] = status
        params = {}
        if approval:
            params["approval_status"] = approval
        
        return self.call("get", "claims", params=params)

    def get(self, id):
        return self.call("get", f'claims/{id}')

    def open(self, policy_id=None, policy_holder_id=None):
        data = {
            "policy_id": policy_id,
            "policy_holder_id": policy_holder_id
        }
        return self.call("post", "claims", json=data)

    def link_policy(self, claim_id, policy_id):
        data = {
            "policy_id": policy_id
        }
        return self.call("post", f'claims/{claim_id}/policy', json=data)

    def link_policy_holder(self, claim_id, policy_holder_id):
        data = {
            "policy_holder_id": policy_holder_id
        }
        return self.call("post", f'claims/{claim_id}/policyholder', json=data)

    def link_events(self, claim_id):
        return self.call("post", f'claims/{claim_id}/events')



class PolicyHolders(Resource):
    def __init__(self, client):
         super().__init__(client)

    def create(self, id, first_name, last_name, email=None, date_of_birth=None, cellphone=None):
        data = {
            "id":            id,
            "first_name":    first_name,
            "last_name":     last_name,
            "date_of_birth": date_of_birth,
            "email":         email,
            "cellphone":     cellphone
        }
        return self.call("post", "policyholders", json=data)

    def list(self):
        return self.call("get", "policyholders")

    def get(self, id):
        return self.call("get", f'policyholders/{id}')

    def update(self, id, email=None, cellphone=None):
        data = {
            "email":     email,
            "cellphone": cellphone
        }
        return self.call("patch", f'policyholders/{id}', json=data)

    def list_events(self, id):
        return self.call("get", f'policyholders/{id}/events')


class Policies(Resource):
    def __init__(self, client):
         super().__init__(client)    

    def issue(self, application_id):
        data = {
            "application_id": application_id,
        }
        return self.call("post", "policies", json=data)

    def add_beneficiary(self, policy_id, beneficiary_id, first_name, last_name, percentage):
        data = {
            "id":         beneficiary_id,
            "first_name": first_name,
            "last_name":  last_name,
            "percentage": percentage
        }
        return self.call("put", f'policies/{policy_id}/beneficiaries', json=data)
        
    def list(self):
        return self.call("get", "policies")

    def get(self, policy_id):
        return self.call("get", f'policies/{policy_id}')

    def cancel(self, policy_id, reason):
        data = {"reason": reason}
        return self.call("post", f'policies/{policy_id}/cancel', json=data)
        
    def replace(self, policy_id, quote_package_id):
        data = {"quote_package_id": quote_package_id}
        return self.call("post", f'policies/{policy_id}/replace', json=data)

    def update_billing_amount(self, policy_id, billing_amount):
        data = {"billing_amount": billing_amount}
        return self.call("post", f'policies/{policy_id}/billing_amount', json=data)

    def list_beneficiaries(self, policy_id):
        return self.call("get", f'policies/{policy_id}/beneficiaries')

    def list_events(self, policy_id):
        return self.call("get", f'policies/{policy_id}/events')


class Quotes(Resource):
    def __init__(self, client):
         super().__init__(client)

    def create(self, opts):
        data = {}
        type_ = opts["type"]
        if type_ == "root_gadgets":
            data = self._gadget_quote(opts)
        elif type_ == "root_term":
            data = self._term_quote(opts)
        elif type_ == "root_funeral":
            data = self._funeral_quote(opts)
        else:
            raise Exception("invalid quote type")
        return self.call("post", "quotes", json=data)

    def _gadget_quote(self, opts):
        return {
            "type": "root_gadgets",
            "model_name": opts["model_name"]
        }

    def _term_quote(self, opts):
        return {
            "type":             "root_term",
            "cover_amount":     opts["cover_amount"],
            "cover_period":     opts["cover_period"],
            "education_status": opts["education_status"],
            "smoker":           opts["smoker"],
            "gender":           opts["gender"],
            "age":              opts["age"],
            "basic_income_per_month": opts["basic_income_per_month"],
        }

    def _funeral_quote(self, opts):
        return {
            "type":                 "root_funeral",
            "cover_amount":         opts["cover_amount"],
            "has_spouse":           opts["has_spouse"],
            "number_of_children":   opts["number_of_children"],
            "extended_family_ages": opts["extended_family_ages"]
        }


class Gadgets(Resource):
    def __init__(self, client):
         super().__init__(client)

    def list_models(self):
        return self.call("get", "gadgets/models")

    def list_phone_brands(self):
        models = self.list_models()
        return set([phone['make'] for phone in models])

    def list_phones_by_brand(self, brand):
        models = self.list_models()
        return set([phone['name'] for phone in models if phone['make'] == brand])

    def get_phone_value(self, phone):
        models = self.list_models()
        return list(filter(lambda p: p['name'] == phone, models))[0]['value']/100
