from root.insurance.exceptions import RootInsufficientDataException
from root.insurance.policyholder import Policyholder, Beneficiary


class Resource(object):
    """Super class for resources within the API
    Each resource should be its own sub-class which is then instantiated within the main InsuranceClient class, thus
        the InsuranceClient remains the interface for the API
    Each sub-class can conveniently set a default REST method for API calls, as well as it's hierarchical URL path
    There are a number of possible ways to validate data (at UI, in a new class (such as Policyholder),
        in a Resource sub-class explicitly, or in sub-class by overriding validate method).
        The choice shall be left up to the user depending on requirements.
    """

    def __init__(self, client, method: str = 'get', path: str = ''):
        self.client = client
        self.method = method
        self.path = path

    def call(self, method=None, sub_path="", params=None, path=None, **kwargs):
        if method is None:
            method = self.method
        if path is None:
            path = "{}/{}".format(self.path, sub_path) if sub_path != "" else self.path
        return self.client.call(method, path, params, **kwargs)


class Quotes(Resource):
    """Super class for generating quotes of the insurance product. Sub-classes can be bare-bones with just a simple
    init method. But can be usefully expanded to have extra useful features for the user, see GadgetCover.
    """
    def __init__(self, client, module_id: str, data_fields: list):
        super().__init__(client, "post", "quotes")
        if "type" not in data_fields:
            data_fields.insert(0, "type")
        self.data_fields = set(data_fields)
        self.module_id = module_id

    def generate(self, data: dict = None, **kwargs) -> dict:
        """Generate a quote using either a dictionary or keyword arguments as data
            (using both will merge them keyword precedence).
        Raises a `RootInsufficientDataException` if not all required fields were provided. E
        xtra fields are ignored by the API
        :param data: data required for the quote in dictionary form
        :param kwargs: data required for the quote in keyword form
        :return: A quote in dictionary format
        """
        if data is None:
            data = {}
        for kw, val in kwargs.items():
            data[kw] = val
        if "type" not in data:
            data["type"] = self.module_id
        if self.data_fields < set(data):
            raise RootInsufficientDataException()
        return self.call(json=data)


class GadgetCover(Quotes):
    """Cover for smartphones.
    All that is required is the model_name, which must be fully-formed to get a response from the API.
    Additional methods are provided to list the models available to be insured.
    """
    def __init__(self, client):
        super().__init__(client, "root_gadgets", ["model_name"])

    def list_models(self):
        """ List the models available in the root_gadgets module
        :return: list of models available, each model is in dict format with keys 'make','name','value'
        """
        return self.call("get", path="modules/root_gadgets/models")

    def list_phone_brands(self):
        models = self.list_models()
        return set([phone['make'] for phone in models])

    def list_phones_by_brand(self, brand):
        models = self.list_models()
        return set([phone['name'] for phone in models if phone['make'] == brand])

    def get_phone_value(self, phone):
        models = self.list_models()
        return list(filter(lambda p: p['name'] == phone, models))[0]['value'] / 100


class FuneralCover(Quotes):
    def __init__(self, client):
        super().__init__(client, "root_funeral",
                         ["cover_amount", "has_spouse", "number_of_children", "extended_family_ages"])


class TermCover(Quotes):
    def __init__(self, client):
        super().__init__(client, "root_term",
                         ["cover_amount", "cover_period", "education_status", "smoker", "gender", "age",
                          "basic_income_per_month"])


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

    def create(self, policyholder: Policyholder):
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
