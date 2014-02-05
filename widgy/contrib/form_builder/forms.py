from django import forms
from django.utils.translation import ugettext_lazy as _

from widgy.contrib.page_builder.forms import MiniCKEditorField, CKEditorField

import phonenumbers


class PhoneNumberField(forms.CharField):
    """
    A USA or international phone number field. Normalizes its value to
    a common US format '(303) 555-5555' for US phone numbers, and an
    international format for others -- '+86 10 6944 5464'. Also supports
    extensions -- '3035555555ex12' -> '(303) 555-5555 ext. 12.'

    If you do not wish to allow phone numbers with extensions, use
    `allow_extension=False`.
    """

    default_error_messages = {
        'invalid': 'Enter a valid phone number.',
        'extension': 'A phone number with an extension is not supported.',
    }

    def __init__(self, *args, **kwargs):
        self.allow_extension = kwargs.pop('allow_extension', True)
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(PhoneNumberField, self).clean(value)
        if not value:
            return value
        try:
            number = phonenumbers.parse(value, 'US')
        except phonenumbers.NumberParseException:
            raise forms.ValidationError(self.error_messages['invalid'])
        if not phonenumbers.is_valid_number(number):
            raise forms.ValidationError(self.error_messages['invalid'])
        if not self.allow_extension and number.extension is not None:
            raise forms.ValidationError(self.error_messages['extension'])

        if number.country_code == 1:
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)
        else:
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)


class FormFieldForm(forms.ModelForm):
    help_text = MiniCKEditorField(label=_('help text'), required=False)


class EmailSuccessHandlerBaseForm(forms.ModelForm):
    content = CKEditorField()


class EmailUserHandlerForm(EmailSuccessHandlerBaseForm):
    to_ident = forms.ChoiceField(label=_('To'), choices=[])

    class Meta:
        fields = ('to_ident', 'subject', 'content', 'include_form_data')

    def __init__(self, *args, **kwargs):
        super(EmailUserHandlerForm, self).__init__(*args, **kwargs)
        self.fields['to_ident'].choices = [('', _('------'))] + [(i.ident, i) for i in self.instance.get_email_fields()]


class FormInputForm(FormFieldForm):
    class Meta:
        fields = (
            'type',
            'required',
            'label',
            'help_text',
        )
