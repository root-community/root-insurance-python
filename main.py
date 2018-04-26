from pprint import pprint
from root.insurance import InsuranceClient
from root.policyholder import Policyholder, Beneficiary


def main():
    # 0. Create an insurance client
    client = InsuranceClient()
    phone = "iPhone 6 Plus 128GB LTE"
    phone_value = client.quotes.get_phone_value(phone)
    print("The value of a {} is R{}".format(phone, phone_value))
    # 1. Issue a quote for the thing to be insured.
    quotes_data = client.quotes.generate(model_name=phone)
    print("The quotes for {} are".format(phone))
    pprint(quotes_data)

    # 2. Create a policy holder
    policyholder = Policyholder(Policyholder.identification("id", "6801015800084", "ZA"), "Erlich", "Bachman")
    policyholder_data = client.policyholders.create(policyholder=policyholder)
    print("Person holding policy is")
    pprint(policyholder_data)
    # 3. Create an application. For this, a generated quote is required.
    chosen_quote = quotes_data[0]
    chosen_quote_id = chosen_quote['quote_package_id']
    policyholder_id = policyholder_data['policyholder_id']
    application_data = client.applications.create(policyholder_id=policyholder_id,
                                                  quote_package_id=chosen_quote_id,
                                                  monthly_premium=chosen_quote['suggested_premium'],
                                                  serial_number='random_serial')
    print("Application data to insure {} is ".format(phone))
    pprint(application_data)
    # 4. Issue policy, if application is approved (this check is not done here)
    policy_data = client.policies.issue(application_id=application_data['application_id'])
    print("Congratulations, your policy looks as follows:")
    pprint(policy_data)
    # 5. Add beneficiaries (if supported, which root_gadgets do not)
    # updated_policy_data = client.policies.add_beneficiary(policy_data['policy_id'],
    #                                                       [Beneficiary(
    #                                                        Policyholder.identification("id", "6801015800084", "ZA"),
    #                                                       "Erlich", "Bachman", percentage=100.0)])
    # 6. Link credit card
    # See API docs https://app.root.co.za/docs/insurance/api#linking-credit-card


if __name__ == "__main__":
    main()
