from root.insurance import Client


def main():
    # start insurance client
    client = Client()
    phone = "iPhone 6 Plus 128GB LTE"
    print(f"The value of a {phone} is R{client.gadgets.get_phone_value(phone)}")


if __name__ == "__main__":
    main()
