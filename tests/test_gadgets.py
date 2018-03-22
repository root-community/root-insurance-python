from context import insurance
import json

client = insurance.Client()

def test_list_models():
    result = client.gadgets.list_models()
    assert result
    assert result.__len__()
    assert len(result) > 0
    assert any(x for x in result if 'Apple' in x.get('make'))

def test_list_phone_brands():
    result = client.gadgets.list_phone_brands()
    assert result
    assert result.__len__()
    assert any(x for x in result if 'Apple' in x)
    assert len(result) > 0

def test_list_phones_by_brand():
    result = client.gadgets.list_phones_by_brand('Apple')
    assert result
    assert result.__len__()
    assert len(result) > 0
    assert any(x for x in result if 'iPhone' in x)


def test_get_phone_value():
    #phones = client.gadgets.list_phone_brands()
    phones = client.gadgets.list_phones_by_brand('Apple')
    print("Phones")
    print(type(phones))
    result = client.gadgets.get_phone_value(list(phones)[0])
    assert int(result) > 0
