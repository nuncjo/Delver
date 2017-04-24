# -*- coding: utf-8 -*-


MATCHINGS = {
    'IN': lambda value1, value2: value1 in value2,
    'NOT_IN': lambda value1, value2: value1 not in value2,
    'EQUAL': lambda value1, value2: value1 == value2,
    'NOT_EQUAL': lambda value1, value2: value1 != value2
}


def match_link(data, filters, match='EQUAL'):
    """ Matches links with filters

    :param data: dict
    :param filters: dict
    :param match: string
    :return: bool
    """
    return match_dict(data, filters, match=match)


def match_dict(data, filters, match='EQUAL'):
    """Matches filters values with data values using predefined matching types

    :param data: dict
    :param filters: dict
    :param match: string, one of  ``'IN', 'NOT_IN', 'EQUAL', 'NOT_EQUAL'``
    :return: bool

    Usage::

    >>> filters = {'class': 'class-120'}
    >>> data = {
    ...     'id': 'searchbox',
    ...     'class': '.what-anice-class-120'
    ... }
    >>> match_dict(data, filters, 'IN')
    True

    """
    for _filter, value in filters.items():
        if value and MATCHINGS[match](value, data.get(_filter)):
            continue
        else:
            return False
    return True


def match_form(wrapped_form, filters):
    """Matches filters values with <FormElement> attributes using predefined matching types

    example_filters = {
        'id': 'searchbox',
        'name': 'name,
        'action': 'action',
        'has_fields': ['field1', 'field2'],
    }

    :param wrapped_form: class::`FormElement <FormElement>` object
    :param filters: dict
    :return: bool
    """
    for name, value in filters.items():
        if name == 'has_fields':
            if not getattr(wrapped_form, name)(value):
                return False
        elif getattr(wrapped_form, name)() != value:
            return False
    return True


def typed_property(name, expected_type):
    """Common function used to creating arguments with forced type

    :param name: name of attribute
    :param expected_type: expected type of attribute value
    :return: property attribute
    """
    private_name = '_' + name

    @property
    def prop(self):
        return getattr(self, private_name)

    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type):
            raise TypeError(f'Expected {expected_type}')
        setattr(self, private_name, value)

    return prop

ForcedInteger = lambda name: typed_property(name, int)
ForcedString = lambda name: typed_property(name, str)
ForcedFloat = lambda name: typed_property(name, float)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
