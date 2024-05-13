from django.db import models
from people.models import Case, Member
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver  # Import receiver here
from django.db import models
from django.db.models.signals import post_save
# from .signals import check_payment_status  # Import from signals.py

# Create your models here.
from django.contrib.auth.models import User  # Assuming user model
# from .signals import Payment  # Forward declaration
from django.db.models import F

from django.db import models

class Penalty(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='penalties')  # Foreign key to Member
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='penalties')  # Foreign key to Case
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of the penalty with decimal support
    description = models.TextField(blank=True)  # Optional description of the penalty
    date_imposed = models.DateField(auto_now_add=True)  # Date the penalty was imposed (automatically set on creation)

    def __str__(self):
        return f"Penalty for {self.member} (Case: {self.case.case_number}) - KES {self.amount}"  # Example string representation

    class Meta:
        ordering = ['-date_imposed']  # Order penalties by most recent first by default


class Account(models.Model):
  """Model for tracking contributed money."""

  name = models.CharField(max_length=255)
  collection_method = models.CharField(max_length=50, choices=(
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
        ('MPESA', 'MPesa'),
    ), default='CASH')
  description = models.TextField(blank=True)  # Optional description
  balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation
  updated_at = models.DateTimeField(auto_now=True)  # Timestamp of last update
#   case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='account_case_payment')
  # Optional: User relationship (if user authentication is needed)
  owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

  def __str__(self):
    return self.name


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    payer = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50, choices=(
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
        ('MPESA', 'MPesa'),
    ), default='CASH')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_receive', default=0)
    # member = models.ForeignKey('Member', on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments_membership')
    # members = models.ManyToManyField(Member)  # ManyToMany relationship

    case_number = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='pesa_case_title_payment', default=1)
    # case = models.ForeignKey('Case', on_delete=models.CASCADE, blank=True, null=True)
    total_paid_for_case = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=(
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('INVALID', 'Invalid'),  # Added for invalid payments
    ), default='UNPAID')
    # set_contribution_amount = models.DecimalField(max_digits=10, decimal_places=2, default=185) 
    # account = models.ForeignKey(Account, on_delete=models.CASCADE, null=False, blank=False)  # Optional: Allow null if not applicable to all payments


    class Meta:
        ordering = ['-payment_date']  # Order payments by recent first

    def __str__(self):
        case_text = f" for case {self.case_number}" if self.case_number else ""
        return f"Payment of {self.amount} on {self.payment_date} by {self.payer}{case_text}"

    def save(self, *args, **kwargs):
        from .models import Member, Case  # Assuming models are in the same app

        try:
            # Fetch existing payments using foreign key fields
            existing_payments = Payment.objects.filter(member=self.member_id, case_number=self.case_number)
            # payments = Payment.objects.filter(member=member, case_number=case)

            if existing_payments.exists():
                # Calculate total paid from existing payments
                total_paid_existing = sum(payment.amount for payment in existing_payments)
                
                
                # total_paid_existing = sum(payment.amount for payment in payments)

            else:
                total_paid_existing = 0

            # Update total_paid_for_case with the current and existing payments
            self.total_paid_for_case = total_paid_existing + self.amount

            # Save the current payment object
        


        except Exception as e:
            # Handle potential errors during update (optional)
            print(f"Error updating total_paid_for_case: {e}")
  
        super().save(*args, **kwargs)



from django.db import models
from django.utils import timezone


class Transfer(models.Model):
  from_account = models.ForeignKey(
      'Account', on_delete=models.CASCADE, related_name='from_transfers')
  to_account = models.ForeignKey(
      'Account', on_delete=models.CASCADE, related_name='to_transfers')
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  reason = models.CharField(max_length=255, blank=True)
  withdraw_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  created_at = models.DateTimeField(default=timezone.now)  # Auto-created timestamp
  transfered_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='funds_transferer')
#   transfered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='funds_transferer', default=1)

  def __str__(self):
    return f"Transfer #{self.pk} - {self.from_account} to {self.to_account} (amount: {self.amount})"

  class Meta:
    ordering = ['-created_at']  # Order transfers by creation date (descending)



class CashOut(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)  # Commented out
    # member = models.ForeignKey(Member, on_delete=models.CASCADE)  # Commented out
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Amount cashed out
    transaction_date = models.DateTimeField(auto_now_add=True)  # Date and time of the transaction
    # reason = models.CharField(max_length=255, blank=True)  # Optional reason for cash out (commented out)
    # status = models.CharField(max_length=20, choices=(('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')), default='PENDING')  # Approval status

    # Additional fields for cash out details
    case = models.ForeignKey(Case, on_delete=models.CASCADE)  # Foreign key to the Case model
    to_whom = models.CharField(max_length=255)  # Name of the recipient
    mpesa_id = models.CharField(max_length=10, blank=True)  # Optional Mpesa ID
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE)  # Foreign key to the Account model

    def __str__(self):
        return f"Cash Out: #{self.pk} - {self.case} - KES {self.amount:.2f}"

    class Meta:
        ordering = ['-transaction_date']  # Order by most recent transactions first
