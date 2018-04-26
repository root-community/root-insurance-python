from root.exceptions import RootIdentificationException


class Policyholder(object):
    """An object for a person's details in the format the Root Insurance API wants
    A person's ID, first name, and last name are always required.

    Example:

    # create object
    >>> person = Policyholder(Policyholder.identification('id','6801015800084','ZA'),...)
    # send in correct format using
    >>> data = person.details()
    >>> data['extra'] = 'extra details'
    >>> from root.resources import Resource
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
    def identification(id_type: str, id_num: str, country_code: str):
        """Helper method to correctly form the 'id' object dict

        Example:
            person = Policyholder(Policyholder.identification('id','6801015800084','ZA'),...)

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


class Beneficiary(Policyholder):
    def __init__(self, id_object, first_name, last_name, percentage=0.0, *args, **kwargs):
        super().__init__(id_object, first_name, last_name, *args, **kwargs)
        assert 0 <= percentage <= 100
        self._details['percentage'] = percentage
