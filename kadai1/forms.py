from django import forms
from django.contrib.auth.hashers import make_password
from .models import Employee
from .models import Shiiregyosha
from .models import Medicine

class EmployeeRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Employee
        fields = ['empid', 'empfname', 'emplname', 'emppaswd', 'emprole']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("emppaswd")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class ShiiregyoshaEditForm(forms.ModelForm):
    class Meta:
        model = Shiiregyosha
        fields = ['shiiretel']

class CapitalSearchForm(forms.Form):
    capital = forms.IntegerField(label='資本金', required=True)

class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(label='新しいパスワード', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='パスワード確認', widget=forms.PasswordInput)

    from django import forms

class PatientSearchForm(forms.Form):
    patname = forms.CharField(label='患者名', max_length=64, required=True)

class MedicineForm(forms.Form):
    medicine = forms.ModelChoiceField(queryset=Medicine.objects.all(), label='薬剤名')
    quantity = forms.IntegerField(label='数量', min_value=1)
