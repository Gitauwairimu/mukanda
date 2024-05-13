from django.db import models
from django.utils import timezone
from django.urls import reverse
# from pesa.models import Payment


# Create your models here.

class Rule(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    # Add a number field with a descriptive name (e.g., order, priority)
    order = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

class RuleProposal(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    submitter = models.CharField(max_length=255)
        # submitter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('proposed', 'Proposed'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='proposed')


    def __str__(self):
        return self.title

from django.contrib.auth.models import User
import re
from django.core.exceptions import ValidationError
from django.db.models import DecimalField

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    # Auto-incrementing membership number
    membership_number = models.AutoField(primary_key=True)
    # membership_number = models.AutoField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255, blank=True) 
    address = models.CharField(max_length=100)
    id_number = models.CharField(max_length=100, unique=True)
    dob = models.DateField(blank=True, null=True, default='1987-12-12')  # Optional date of birth
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default='NA')
    dependent = models.CharField(max_length=20, choices=(('NOT DEPENDENT', 'not_dependent'), ('DEPENDENT', 'dependent')), default='NOT DEPENDENT')
    relationship = models.CharField(max_length=10, choices=(('Child', 'Child'), ('Member', 'Member'), ('Spouse', 'Spouse'), ('Parent', 'Parent')), default = 'Member')
    passport_photo = models.ImageField(blank=True, null=True, upload_to='passports/',  default='default_passport.jpg')
    status = models.CharField(max_length=20, choices=(('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('DECEASED', 'Deceased')), default='ACTIVE')
    next_of_kin = models.CharField(max_length=100)
    next_of_kin_contact = models.CharField(max_length=20)
    penalized = models.CharField(max_length=20, choices=(('NOT PENALIZED', 'not_penalized'), ('PENALIZED', 'penalized')), default='NOT PENALIZED')
    
    total_penalties = DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Contact information
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True, unique=True)  # Optional email address

    # Dependents (consider using a OneToManyField relationship for dependents)
    number_of_dependents = models.PositiveIntegerField(default=0)  # Non-negative number of dependents

    # Consider a separate model for dependents with their details (age, gender)
    # This is a more scalable approach for managing complex dependent information.

    # Additional fields as needed (e.g., join date, membership status)
    join_date = models.DateTimeField(default=timezone.now)


    @property
    def full_name(self):
        """
        Returns the full name constructed from first, other (optional), and last name.
        """
        return f"{self.first_name} {self.other_name} {self.last_name}"


    
    def __str__(self):
        if self.dependent == 'DEPENDENT':
            return f" Dependent: {self.first_name} {self.last_name}-{self.membership_number}"
            # return f"{self.first_name} - Dependent of {self.member.first_name} {self.member.last_name}"
        else:
        # full_name = f"{self.first_name} {self.other_name} {self.last_name}"
        # return self.full_name
            return f"{self.first_name}-{self.last_name}-{self.membership_number}"
            # return f"Member: {self.full_name}-{self.membership_number}"


    def get_absolute_url(self):
        return reverse('member_detail', kwargs={'pk': self.membership_number})
        # return reverse('paylist')



    def clean_next_of_kin_contact(self):
        """
        Custom validator to ensure the phone_number has 10 digits and starts with 0.
        """
        phone_regex = r"^0\d{9}$"  # Regular expression for 0 followed by 9 digits
        if not re.match(phone_regex, self.next_of_kin_contact):
            raise ValidationError('Phone number must be 10 digits and start with 0.')
        return self.next_of_kin_contact

    def clean_phone_number(self):
        """
        Custom validator to ensure the phone_number has 10 digits and starts with 0.
        """
        phone_regex = r"^0\d{9}$"  # Regular expression for 0 followed by 9 digits
        if not re.match(phone_regex, self.phone_number):
            raise ValidationError('Phone number must be 10 digits and start with 0.')
        return self.phone_number

    def clean_id_number(self):
        """
        Custom validator to ensure the id_number has at least 8 digits and consists only of numbers.
        """
        id_regex = r"^\d{8}$"  # Regular expression for 8 digits
        if not re.match(id_regex, self.id_number):
            raise ValidationError('ID number must be 8 digits and contain only numbers.')
        return self.id_number

    def clean(self):
        """
        Call custom validator for id_number during model cleaning.
        """
        self.clean_id_number()
        self.clean_phone_number()
        self.clean_next_of_kin_contact()
        super().clean()
    
    def save(self, *args, **kwargs):
        # ... (your existing save logic)
        if self.dependent == 'DEPENDENT':
            self.set_contribution = 100.00 # Set contribution amount for dependents (logic here)
        else:
            self.set_contribution = 200.00 # Set contribution amount for non-dependents (logic here)

        # self.full_name = f"{self.first_name} {self.other_name} {self.last_name}"  # Set full name on save
        super().save(*args, **kwargs)


import random
from string import ascii_uppercase



from .counter import Counter
from django.utils import timezone

from django.db import models
from .counter import Counter  # Assuming counter.py is in the same app
from django.contrib.auth.models import User  # Assuming user model


class Case(models.Model):
    # deceased_name = models.CharField(max_length=255)
    # deceased_name = models.ForeignKey('membership.Member', on_delete=models.CASCADE, related_name='deceased_cases')  # Foreign key to Member
    date_of_death = models.DateField(blank=True, null=True, help_text='Enter date in YYYY-MM-DD format (e.g., 2024-03-27)')
    membership_number = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='member_cases')
    mpesa_number = models.CharField(max_length=20, blank=True, default = '0701411355')
    contribution_window_start = models.DateField(blank=False, null=False)
    contribution_window_end = models.DateField(blank=False, null=False)    
    case_number = models.CharField(max_length=50, unique=True, primary_key=True)
    set_contribution_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    run_penalties = models.CharField(max_length=20, choices=(('Run Penalties', 'run_penalties'), ('Penalties Not Run', 'penalties_not_run')), default='penalties_not_run')
    deceased_name = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='deceased_cases', limit_choices_to={'status': 'ACTIVE'})  # Filter deceased members
    status = models.CharField(max_length=20, choices=(('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('PENDING', 'Deceased')), default='ACTIVE')
    cashed_out = models.CharField(max_length=20, choices=(('Cashed Out', 'cashed_out'), ('Not Cashed Out', 'not_cashed_out')), default='not_cashed_out')

    def __str__(self):
        # full_name = f"{self.first_name} {self.other_name} {self.last_name}"
        # return self.full_name
        return f"{self.case_number}"


    def get_year(self):
        return timezone.now().year

    def save(self, *args, **kwargs):
        
        if self.deceased_name:
            self.deceased_name.status = 'DECEASED'
            self.deceased_name.save()  # Update member status after Case save

        # Get or create a counter object
        counter, created = Counter.objects.get_or_create(defaults={'current_value': 0})

        # Generate sequential case number with year and membership number
        counter.current_value += 1
        counter.save()  # Update counter value
        self.case_number = f"{self.get_year()}-{counter.current_value:0>4}-{self.membership_number}"



        # Set case status based on contribution window
        today = timezone.now().date()
        if self.contribution_window_start and self.contribution_window_end:  # Check only if contribution_window_start is defined
          if today < self.contribution_window_start:
            self.status = 'PENDING_LAUNCH'  # Set to pending if before contribution window
          else:
            # Handle cases within or after contribution window (unchanged)
            if today <= self.contribution_window_end:
                self.status = 'ACTIVE'
            else:
                self.status = 'INACTIVE'
        else:
          self.status = 'UNKNOWN'  # Maintain pending status if contribution window not defined

        # For all payments by autopayer, remove from list of payments
        super().save(*args, **kwargs)





