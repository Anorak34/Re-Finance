from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import *


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")

    class Meta:
        model = User
        fields = ("username","first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                self.fields[field_name].widget.attrs.update({"placeholder": field.label})
                self.fields[field_name].label = False

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
    

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                self.fields[field_name].widget.attrs.update({"placeholder": field.label})
                self.fields[field_name].label = False


class ChangeUserDetailsForm(forms.ModelForm):   
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class DeleteAccountForm(forms.Form):   
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({"placeholder": 'Password'})
        self.fields['password'].label = False


class CashForm(forms.Form):
    month_choices = []
    year_choices = []

    for i in range(1, 13):
        month_choices.append((i, i))
    month_choices = tuple(month_choices)
    for i in range(2023, 2031):
        year_choices.append((i, i))
    year_choices = tuple(year_choices)
    
    cash = forms.IntegerField(required=True, min_value=1, widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder': '$', 'id':'cash', 'name':'cash'}))
    number = forms.CharField(required=True, max_length=19, widget=forms.TextInput(attrs={'class':'form-control','onkeypress': 'return event.charCode >= 48 && event.charCode <= 57', 'id':'number', 'name':'number', 'oninput':'handleNumber()'}))
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control','id':'name', 'name':'name', 'oninput':'handleName()'}))
    cvv = forms.CharField(required=True, max_length=3, widget=forms.TextInput(attrs={'class':'form-control cvv','placeholder': 'CVV', 'id':'cvv', 'name':'cvv', 'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'}))
    month = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-select','id':'month', 'name':'month', 'onchange':'handleDate()'}), choices=month_choices)
    year = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-select','id':'year', 'name':'year', 'onchange':'handleDate()'}), choices=year_choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                self.fields[field_name].label = False


class ChangeCurrencyForm(forms.ModelForm):
    default_currency = forms.CharField(max_length=3, help_text='Enter a valid currency code')   
    class Meta:
        model = Profile
        fields = ('default_currency', )


class BuyForm(forms.Form):
    symbol = forms.CharField(required=True, max_length=5, label="Symbol")
    shares = forms.IntegerField(required=True, min_value=1, label="Shares")
    page = forms.CharField(widget=forms.HiddenInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                self.fields[field_name].widget.attrs.update({"placeholder": field.label})
                self.fields[field_name].label = False


class SellForm(forms.Form):
    symbol = forms.ChoiceField(required=True, label="Symbol")
    shares = forms.IntegerField(required=True, min_value=1, label="Shares")
    page = forms.CharField(widget=forms.HiddenInput())
    def __init__(self, choices_, *args, **kwargs):
        super(SellForm, self).__init__(*args, **kwargs)
        self.fields['symbol'].choices = choices_
        self.fields['shares'].widget.attrs.update({"placeholder": 'Shares'})
        self.fields['shares'].label = False
