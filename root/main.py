from insurance import Client
import os

def main():
    baseURL = "https://sandbox.root.co.za/v1/insurance"
    appID = os.environ.get('ROOT_APP_ID')
    appSecret = os.environ.get('ROOT_APP_SECRET')
    client = Client(baseURL, appID, appSecret)
    print(client.gadgets.get_phone_value("iPhone 6 Plus 128GB LTE"))


if __name__ == "__main__":
    main()
