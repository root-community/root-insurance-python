from insurance import Client
import os

def main():
    client = Client()
    print(client.gadgets.get_phone_value("iPhone 6 Plus 128GB LTE"))


if __name__ == "__main__":
    main()
