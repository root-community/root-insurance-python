import unittest
import context
from root.insurance import InsuranceClient, GadgetCover

class GadgetCoverTestCase(unittest.TestCase):

    def setUp(self):
        self.client = InsuranceClient(cover=GadgetCover)

    def test_list_models(self):
        result = self.client.quotes.list_models()
        assert result
        assert result.__len__()
        assert len(result) > 0
        assert any(x for x in result if 'Apple' in x.get('make'))

    def test_list_phone_brands(self):
        result = self.client.quotes.list_phone_brands()
        assert result
        assert result.__len__()
        assert any(x for x in result if 'Apple' in x)
        assert len(result) > 0

    def test_list_phones_by_brand(self):
        result = self.client.quotes.list_phones_by_brand('Apple')
        assert result
        assert result.__len__()
        assert len(result) > 0
        assert any(x for x in result if 'iPhone' in x)

    def test_get_phone_value(self):
        phones = self.client.quotes.list_phones_by_brand('Apple')
        print("Phones")
        print(type(phones))
        result = self.client.quotes.get_phone_value(list(phones)[0])
        assert int(result) > 0

    def test_get_phone_value_unknown_model(self):
        with self.assertRaises(IndexError) as context:
            self.client.quotes.get_phone_value("iPhone 600 Plus 128TB LTD")

