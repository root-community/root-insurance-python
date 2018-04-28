# 🌐👋 - Hello World  

Root is a company built by developers for developers. Open Source Software is part of our culture. We open-source as much of our codebase as we can.

Our SDKs are community maintained. (because we’re not experts in go, or lolcode, or ruby, or swift or rust or any of the plethora of wonderful languages living out in the wild).

This repo for the Python Insurance SDK is currently just a placeholder, but you can change that.


For help and support, please reach out to us on the Root Club Slack.

## Contributing
If you wish to contribute to this repository, please fork it and send a PR our way.

## Publishing

There are a few things to do if you want to publish this repository as an official Root package:

- [ ] Please ensure a Root Team member is able to publish a fix to the package should you be unavailable
- [ ] Write a short explanation on how to to publish in this README, or alternatively, set up a CI build which can automatically build and publish the package. 

## Code of Conduct
Root’s developers and our community are expected to abide by the [Contributor Covenant Code of Conduct](https://github.com/root-community/root-insurance-go/tree/master/CODE_OF_CONDUCT.md). Play nice.

## Install
```
pip install rootsdk
```
or for active development
```
git clone git@github.com:root-community/root-insurance-python.git
pip install -e root-insurance-python
```

## Environment Variables
```
ROOT_API_KEY
```

## Code

```python
from root.insurance import InsuranceClient,GadgetCover

client = InsuranceClient(cover=GadgetCover)
phone_brands = client.gadgets.list_phone_brands()

```

# Upload to pip
```
python setup.py bdist_wheel upload -r pypi
```