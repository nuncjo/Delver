# -*- coding: utf-8 -*-

from urllib.parse import urljoin

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

    Usage::

    >>> from lxml import html
    >>> import requests
    >>> session = requests.Session()
    >>> response = session.get('https://httpbin.org/forms/post')
    >>> html_tree = html.fromstring(response.content)
    >>> form = FormWrapper(html_tree.forms[0], session=session, url=response.url)
    >>> form.fields = {
    ...        'custname': 'aaa',
    ...        'delivery': '',
    ...        'custemail': 'test@email.com',
    ...        'comments': 'What a nice form to post!',
    ...        'size': 'medium',
    ...        'topping': ['bacon', 'cheese'],
    ...        'custtel': '+48606505888'
    ...    }
    >>> form.submit(extra_values={'extra_value': "I am your father."})
    <Response [200]>
    >>> form.check(
    ...        phrase="I am your father.",
    ...        url='https://httpbin.org/post',
    ...        status_codes=[200]
    ...     )
    True
    """

    def __init__(self, lxml_form, session=None, url=None):
        """FormWrapper initialization

        :param lxml_form: class::`FormElement <FormElement>` object
        :param session: session object required only if we want to submit form
        :param url: current base url used to assemble full action url
        """
        self._lxml_form = lxml_form
        self._fields = {}
        self._session = session
        self._result = None
        self._url = url or None

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
        self._lxml_form.fields = values

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
        return urljoin(
            self._url,
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

    def check(self, phrase=None, url=None, status_codes=None):
        """Checks if success conditions of form submit are met

        :return: bool
        """
        return any([
            phrase in self._result.text if phrase else True,
            self._result.url == url if url else True,
            self._result.status_code in status_codes if status_codes else True
        ])

    def __getattr__(self, item):
        """Wraps some chosen methods (PARENT_METHODS) from ``lxml.html.FormElement``

        :param item: method name
        :return: value of the attribute
        """
        if item in PARENT_METHODS:
            return getattr(self._lxml_form, item)
        return getattr(self, item)

    def submit(self, custom_action=None, extra_values=None):
        """Submits current form

        :param custom_action: custom action url
        :param extra_values: extra values to submit even if form has no matching inputs
        :return: submit result
        """
        action = custom_action or self.action_url()
        values = self.form_values()
        self.append_extra_values(values, extra_values)
        self._result = self._session.request(self.method, action, data=values)
        return self._result

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
