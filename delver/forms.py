# -*- coding: utf-8 -*-

import io

from urllib.parse import urljoin, urlparse

from lxml.html import (
    CheckboxGroup,
    CheckboxValues,
    SelectElement,
    RadioGroup
)

PARENT_METHODS = ['form_values', 'action', 'method']


def prepare_field(field):
    data = {
        'value': field.value,
        'tag': field.tag if hasattr(field, 'type') else None,
        'type': field.type if hasattr(field, 'type') else None,
    }
    if isinstance(field, CheckboxValues):
        data['value_options'] = field.group.value_options
    elif isinstance(field, CheckboxGroup):
        data.update({
            'value': list(field.value),
            'value_options': field.value_options
        })
    elif isinstance(field, SelectElement):
        data.update({
            'value': list(field.value) if field.multiple else field.value,
            'value_options': field.value_options
        })
    elif isinstance(field, RadioGroup):
        data['value_options'] = field.value_options
    return data


class FormWrapper:
    """Wrapper for ``lxml.html.FormElement``.

    Represents a <form> element.
    Basically, it's FormElement with added:
    - Ability to submit itself - method ``submit``
    - Success/Fail check after submit form - method ``check``
    - Readable representation of fields - property ``fields``
    - Prepare full action url - method ``action_url``
    - Checking if there are specific fields in form - method ``has_fields``
    - Simplified api to access form attributes like ``id``, ``name``

    """

    def __init__(self, lxml_form, session=None, url=None):
        """FormWrapper initialization

        :param lxml_form: class::`FormElement <FormElement>` object
        :param session: session object required only if we want to submit form
        :param url: current base url used to assemble full action url
        """
        self._lxml_form = lxml_form
        self._fields = {}
        self._files = {}
        self._session = session
        self._result = None
        self._url = url or None

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

    @property
    def files(self):
        return self._files

    @files.getter
    def files(self):
        return self._files

    @files.setter
    def files(self, value):
        self._files = value

    @property
    def fields(self):
        """Readable representation of fields as a ``dict``.

        :return: dict
        """
        for name, field in dict(self._lxml_form.inputs).items():
            self._fields[name] = prepare_field(field)
        return self._fields

    @fields.setter
    def fields(self, values):
        """Sets form fields (inputs) values.

        :param values: dict with form
        :return:
        """
        text_values = {}
        for name, val in values.items():
            if isinstance(val, io.IOBase):
                self._files[name] = val
            else:
                text_values[name] = val

        self._lxml_form.fields = text_values

    def id(self):
        """Returns form id attribute

        :return: str
        """
        return self._lxml_form.attrib.get('id')

    def name(self):
        """Returns form name attribute

        :return: str
        """
        return self._lxml_form.attrib.get('name')

    def action_url(self):
        """Assembles full action url

        :return: str
        """
        action_url = self.action
        return urljoin(
            self._url if urlparse(action_url).scheme else '',
            self.action
        )

    def has_fields(self, fields):
        """Return ``True`` if all fields are present

        :return: bool
        """
        for field in fields:
            if field not in dict(self._lxml_form.inputs):
                return False
        return True

    def __getattr__(self, item):
        """Wraps some chosen methods (PARENT_METHODS) from ``lxml.html.FormElement``

        :param item: method name
        :return: value of the attribute
        """
        if item in PARENT_METHODS:
            return getattr(self._lxml_form, item)
        return getattr(self, item)

    def append_extra_values(self, values, extra_values):
        """ Extends form values by adding extra values.

        :param values: current form fields values
        :param extra_values: additional values extending current values
        :return: None
        """
        if extra_values:
            if hasattr(extra_values, 'items'):
                extra_values = extra_values.items()
            values.extend(extra_values)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
