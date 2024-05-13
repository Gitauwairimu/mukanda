from django import forms
from .models import Case, Payment, Account, Transfer
from people.models import Member

class PaymentForm(forms.ModelForm):
    # case_number = forms.ModelChoiceField(queryset=Case.objects.filter(status='ACTIVE'))
    member = forms.ModelChoiceField(queryset=Member.objects.exclude(status='DECEASED'))
    



    class Meta:
        model = Payment
        # fields = ['amount', 'payer', 'payment_method', 'receiver', 'member', 'case_number']
        fields = ['amount', 'payer', 'payment_method', 'member', 'case_number']
        # fields = ['amount', 'payer', 'payment_method', 'receiver', 'member', 'case_number', 'account']


from django import forms
from .models import Account  # Assuming your model is in models.py
# from django.contrib.auth.models import User


class TransferForm(forms.ModelForm):
    from_account = forms.ModelChoiceField(queryset=Account.objects.all(), label="From Account")
    to_account = forms.ModelChoiceField(queryset=Account.objects.all(), label="To Account")
    amount = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2, label="Amount", required=True)
    reason = forms.ChoiceField(
        label="Reason",
        choices=(
            ('consolidate_for_cash_out', 'Consolidate for Cash Out'),
            # Add more choices as needed, following the format (value, label)
        ),
        required=True
    )
    # transfered_by = None
    # transfered_by = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Transfer
        fields = ['from_account', 'to_account', 'amount', 'reason']  # Explicitly list all fields






from django import forms
from .models import CashOut, Case  # Assuming Case model

class CashOutForm(forms.ModelForm):
    class Meta:
        model = CashOut
        # fields = ['case', 'amount', 'to_whom', 'mpesa_id', 'from_account']
        fields = ['case', 'to_whom', 'mpesa_id', 'from_account']
        # widgets = {
        #     'amount': forms.NumberInput(attrs={'min': 0}),  # Ensure non-negative amount
        # }
       

    # def clean_amount(self):
    #     """
    #     Custom validation to ensure amount is greater than zero.
    #     """
    #     amount = self.cleaned_data['amount']
    #     if amount <= 0:
    #         raise forms.ValidationError('Cash out amount must be greater than zero.')
    #     return amount

    # def __init__(self, *args, **kwargs):
    #     super(CashOutForm, self).__init__(*args, **kwargs)
    #     # Filter case choices based on user or other criteria (optional)
    #     # self.fields['case'].queryset = Case.objects.filter(/* your filter criteria */)
