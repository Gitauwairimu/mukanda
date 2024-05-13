from django import forms
from .models import Member, Case, Rule, RuleProposal  # Import your member model



class ProposalRuleForm(forms.ModelForm):
  class Meta:
    model = RuleProposal
    fields = ['title', 'content', 'submitter']  # Adjust fields as needed

    def clean_title(self):
      """
      Custom validation for the title field.

      Ensures the title is not empty and has a minimum length.
      You can add more validation logic here as needed.
      """
      title = self.cleaned_data['title']
      if not title:
        raise forms.ValidationError('Please enter a title for the rule.')
      if len(title) < 3:
        raise forms.ValidationError('Title must be at least 3 characters long.')
      return title

class RuleForm(forms.ModelForm):
  class Meta:
    model = Rule
    fields = ['title', 'content', 'order']  # Adjust fields as needed

    def clean_title(self):
      """
      Custom validation for the title field.

      Ensures the title is not empty and has a minimum length.
      You can add more validation logic here as needed.
      """
      title = self.cleaned_data['title']
      if not title:
        raise forms.ValidationError('Please enter a title for the rule.')
      if len(title) < 3:
        raise forms.ValidationError('Title must be at least 3 characters long.')
      return title

from django.forms import ModelForm

class DependentForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'other_name', 'last_name', 'id_number', 'dob', 'gender', 'relationship', 'passport_photo',]  # Adjust as needed
      
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      # Exclude "Member" from relationship choices
      member_choices = list(self.fields['relationship'].choices)
      member_choices.remove(('Member', 'Member'))
      self.fields['relationship'].choices = member_choices



from django import forms
from .models import Case, Member

from django import forms
from django.contrib.auth.models import User
from django.forms import DateInput, ModelForm

class MembershipForm(forms.ModelForm):
    username = forms.CharField(label="Username", required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)
    
    dob = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Member  # Assuming your model is Member
        fields = ['username', 'password1', 'password2', 'first_name', 'other_name', 'last_name', 'id_number', 'dob', 'gender', 'phone_number', 'next_of_kin', 'next_of_kin_contact', 'address', 'email', 'passport_photo',]
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don\'t match.')
        return password2



# class MembershipForm(forms.ModelForm):
#   class Meta:
#     model = Member
#     fields = ('__all__')
#     # fields = ['first_name', 'other_name', 'last_name', 'id_number', 'dob', 'gender', 'phone_number', 'next_of_kin', 'next_of_kin_contact', 'address', 'email', 'passport_photo']  # Adjust as needed
    
 
#   # Consider using a separate form for dependent details if needed

#   def clean_phone_number(self):
#     # Optional: Implement custom validation logic for phone number format (optional)
#     phone_number = self.cleaned_data['phone_number']
#     # Add validation logic here (e.g., check for specific number format)
#     return phone_number


class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ('__all__')



class CaseForm(forms.ModelForm):
    date_of_death = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    contribution_window_start = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    contribution_window_end = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Case
        fields = ['deceased_name', 'date_of_death', 'contribution_window_start', 'contribution_window_end', 'membership_number']
        # widgets = {'deceased_name': forms.ModelChoiceField(queryset=Member.objects.all())}
        # date_of_death = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

        # fields = ['deceased_name', 'date_of_death', 'membership_number', 'contribution_window_start', 'contribution_window_end']
        # fields = '__all__'
    def cleanmemberstatus(self):
        cleaned_data = super().clean()
        member = cleaned_data.get('deceased_name')

        # Check if member is not None and has a 'DECEASED' status
        if member and member.status == 'DECEASED':
            raise forms.ValidationError('A case cannot be created for a deceased member.')
        return cleaned_data
    


