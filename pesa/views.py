from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, View  # Correct import for ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User  # Optional for authentication
from .models import Payment, Case, Transfer, CashOut  # Import your Member model
from django import forms
from django.urls import reverse
from .forms import PaymentForm
from django.contrib import messages




from django.contrib.auth.decorators import login_required  # Assuming user authentication
from .forms import CashOutForm  # Replace with your cash out form class

from django.shortcuts import redirect, render
from django.contrib import messages  # To display flash messages
from .models import Case, CashOut  # Assuming models in the same app

from datetime import date
from django.db.models import Q, Sum


from decimal import Decimal

def calculate_mpesa_charge(amount):
  """
  This function calculates the Mpesa charge based on the provided amount.

  **Args:**
      amount (float): The amount of money being sent through Mpesa.

  **Returns:**
      float: The Mpesa charge for the given amount.

  **Note:** This function is based on the information available on the Safaricom website as of 2024-04-29.
          The actual charges might change, so it's recommended to refer to the official Safaricom website for the latest information.
  """

  # Define charge tiers based on the website information
  tiers = [
      (0, 49, 0.00, 0.00),
      (50, 100, 0.00, 11),
      (101, 500, 7.00, 29),
      (501, 1000, 13.00, 29),
      (1001, 1500, 23.00, 29),
      (1501, 2500, 33.00, 29),
      (2501, 3500, 53.00, 52),
      (3501, 5000, 57.00, 69),
      (5001, 7501, 78.00, 87),
      (7501, 10000, 90.00, 115),
      (10001, 15000, 100.00, 167),
      (15001, 20000, 105.00, 185),
      (20001, 35000, 108.00, 197),
      (35001, 50000, 108.00, 278),
      (50001, 250000, 108.00, 309),

  ]

  # Find the appropriate tier for the given amount
  for lower_bound, upper_bound, charge, withdraw_fee in tiers:
    # if lower_bound <= amount <= upper_bound:
    if (lower_bound is None or amount >= lower_bound) and (upper_bound is None or amount <= upper_bound):
      # return Decimal(str(withdraw_fee))
      return Decimal(str(charge)), Decimal(str(withdraw_fee))



today = date.today()

@login_required  # Restrict access to logged-in users (adjust if needed)
def cash_out_request(request):
    if request.method == 'POST':
        form = CashOutForm(request.POST)
        # case = request.POST['case_number']  # Assuming you get case number from the form
        case = request.POST['case']
        try:
            # case = Case.objects.get(case_number=case)
            case = Case.objects.get(case_number=case)
            # if Case.objects.filter(contribution_window_end__lt=today, cashed_out='not_cashed_out').update(cashed_out='cashed_out')

            if date.today() > case.contribution_window_end and case.cashed_out == 'not_cashed_out':
            # if date.today() > case.contribution_window_end and case.cashed_out == 'cashed_out':
                # Process cash out logic here (create CashOut object, calculate payout, etc.)

              if form.is_valid():
                unsavedform = form.save(commit=False)
              # Save the cash out request (assuming form is valid)
                # form.save()
                 # ... cash out processing logic ...
                # Case.objects.filter(case_number=case).update(cashed_out = 'not_cashed_out')
                
                contributions_total = Payment.objects.filter(case_number=case).aggregate(total_amount=Sum('amount'))['total_amount']
                mpesa_account = Account.objects.filter(name__startswith='Mpesa')[0]
                
                # confirmation_fee = int(0.1 * contributions_total)
                confirmation_fee = int((10 * contributions_total) / 100)
                contributions_minus_confirmation_fee = contributions_total - confirmation_fee - 2000
                mpesa_charge = calculate_mpesa_charge(contributions_minus_confirmation_fee)[0]
                deductables = contributions_total - (mpesa_charge + confirmation_fee + 2000)
                # deductables = contributions_total

                if mpesa_account.balance >= contributions_total:
                  
                  # deductables = contributions_total + mpesa_charge + confirmation_fee + 2000
                  # mpesa_account.balance - deductables
                  mpesa_account.balance -= contributions_total
                  mpesa_account.save()
                else:
                  messages.warning(request, f"Account Balance is less than Case contribution for {case.case_number}")
                  return redirect('accounts')  # Redirect to accounts page to see balances
                Case.objects.filter(case_number=case).update(cashed_out = 'cashed_out')
                # Case.objects.filter(case_number=case).update(cashed_out = 'not_cashed_out')
                # Case.objects.filter(contribution_window_end__lt=today, cashed_out='not_cashed_out').update(cashed_out='cashed_out')
                case.save()  # Update cashed_out field
                # amount = contributions_total - mpesa_charge - confirmation_fee - 2000
                unsavedform.amount = deductables
                unsavedform.save()
                messages.success(request, f"Cash Out request submitted for case {case.case_number}")
                return redirect('cashoutlist')  # Redirect to cash out list after success
            else:
                messages.error(request, f"Case {case.case_number} is already cashed out.")
                return redirect('cashoutlist')  # Redirect to cash out list if already cashed out
        except Case.DoesNotExist:
            messages.error(request, f"Invalid Case Number: {case_number}")
            return redirect('cashoutlist')  # Redirect to cash out list after success
    else:
      form = CashOutForm()

      return render(request, 'pesa/cash_out_form.html', {'form': form})  # Render cash out form

# @login_required  # Restrict access to logged-in users (adjust if needed)
# def cash_out_request(request):
#     if request.method == 'POST':
#         form = CashOutForm(request.POST)
#         if form.is_valid():
#             # Save the cash out request (assuming form is valid)
#             form.save()
#             return redirect('cashoutlist')  # Redirect to cash out list after successful creation
#     else:
#         form = CashOutForm()

#     context = {'form': form}
#     return render(request, 'pesa/cash_out_form.html', context)


from django.shortcuts import render
from .models import CashOut

def cashout_list(request):
  # Get all cashout objects (consider filtering based on user or other criteria)
  cashouts = CashOut.objects.all()
  context = {'cashouts': cashouts}
  return render(request, 'pesa/cashout_list.html', context)




# # Create your views here.
# from .models import Member  # Import your Member model
class PaymentDetailsView(DetailView):
    model = Payment
    template_name = 'pesa/payments_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here if needed
        return context

class TransactionsListView(ListView):
  model = Payment  # Specify the model to retrieve data from
  # template_name = 'pesa/payments_list.html'  # Template to render the list
  template_name = 'pesa/transactions.html'  # Template to render the list

  def get_queryset(self):
    """
    Override the default queryset to potentially filter or order members.
    """
    return Payment.objects.all()  # Retrieve all members by default



from django.db.models import Q
# from django.db.models import Q, OuterRef, Subquery
def payments_list(request, case_number):
  """
  Function-based view to list payments for a specific case, iterating through members.
  """
  case = Case.objects.get(pk=case_number)
  # members = Member.objects.all()  # Retrieve all members
  # members = Member.objects.filter(Q(join_date__gt=case.contribution_window_start) & ~Q(status='DECEASED'))
  members = Member.objects.filter(Q(join_date__gt=case.contribution_window_start) & ~Q(status='DECEASED'))
  case_payments = {}  # Dictionary to store total_paid_for_case per member

  for member in members:
    payments = Payment.objects.filter(member=member, case_number=case_number)
    total_paid = sum(payment.amount for payment in payments)
    case_payments[member] = total_paid

  context = {'case_payments': case_payments, 'case': case}  # Pass data to template
  return render(request, 'pesa/payments_list.html', context)


# class PaymentsListView(ListView):
#   model = Payment  # Specify the model to retrieve data from
#   template_name = 'pesa/payments_list.html'  # Template to render the list

#   def get_queryset(self):
#     """
#     Override the default queryset to potentially filter or order members.
#     """
#     return Payment.objects.all()  # Retrieve all members by default

from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .models import Case, Payment, Account  # Include Account model
from people.models import Member
from .forms import PaymentForm
import decimal  # Import the decimal module

def payment_history(request, membership_number):
  """
  Function-based view to display payment history for a member.

  Args:
      request: HttpRequest object containing request information.
      member_id: Integer representing the member's primary key.

  Returns:
      HttpResponse rendered with the payment history template.
  """

  try:
      member = Member.objects.get(pk=membership_number)
  except Member.DoesNotExist:
      # Handle case where member doesn't exist (e.g., display error message)
      context = {'error': 'Member not found.'}
      return render(request, 'pesa/payment_history_error.html', context)

  # payments = member.payment_set.all().order_by('-payment_date')  # Order by recent first
  payments = Payment.objects.filter(member=member)

  context = {'member': member, 'payments': payments}
  return render(request, 'pesa/payment_history.html', context)


# class PaymentHistoryView(ListView):
#     model = Member
#     template_name = 'pesa/payment_history.html'
#     paginate_by = 10

#     def get_queryset(self):
#         member_id = self.kwargs['member_id']  # Access member ID from URL parameters
#         queryset = Payment.objects.filter(member__pk=member_id)
#         # ... (rest of your queryset logic)
#         return queryset

#     def get_context_data(self, **kwargs):
#       context = super().get_context_data(**kwargs)
#       # No need to access self.object (use the queryset instead)
#       return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     member = self.object  # Access the member object
    #     payments = member.payment_set.all().order_by('-payment_date')  # Order by recent first
    #     context['payments'] = payments
    #     return context

# unpaid_members = Member.objects.filter(Q(payment_set__status='UNPAID')).distinct()


def make_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            case_number = request.POST['case_number']
            case = Case.objects.get(case_number=case_number)
            payment = form.save(commit=False)  # Don't commit save yet
            member = payment.member
            payment.receiver = request.user

            # Get total penalties for the member
            total_penalties = member.total_penalties

            payments = Payment.objects.filter(case_number=case, member=member)
            has_payments = payments.exists()

            # has_payments = payments.filter(case_number=case, member=member).exists()

            if total_penalties == 0.00:
                print('total penalties greater than zero')
                # Deduct penalties from payment amount
                payment.amount = payment.amount
                member.total_penalties = case.set_contribution_amount - payment.amount  # Reset total penalties
                # payments = Payment.objects.filter(member=member, status='PARTIALLY_PAID')
                # for payment in payments:
                #   payment.status='PAID'
                #   payment.save()
                payment.save()

            elif total_penalties <= payment.amount:
                if has_payments:
                  print('total penalties lesser than paid amount')
                  print('Case payments exist')
                # Deduct penalties from payment amount
                  total_penalties = max(total_penalties - payment.amount, 0)
                  payment.amount = payment.amount - total_penalties
                  member.total_penalties = total_penalties  # Reset total penalties
                else:
                   print('total penalties lesser than paid amount')
                   print('Case payments dont exist')
                   penalties = case.set_contribution_amount + total_penalties
                   if payment.amount >= penalties:
                      print('paid amount more than total penalties plus set case contribution')
                      total_penalties = (case.set_contribution_amount + total_penalties) - payment.amount
                      payment.amount = payment.amount - penalties
                      member.total_penalties = total_penalties
                      member.penalized = 'NOT_PENALIZED'
                      payments = Payment.objects.filter(member=member, status='PARTIALLY_PAID')
                      for payment in payments:
                        payment.status='PAID'
                        payment.save()
                   elif payment.amount < penalties:
                      print('paid amount lesser than total penalties plus set case contribution')
                      total_penalties = penalties - payment.amount
                      payment.amount = payment.amount - case.set_contribution_amount
                      member.total_penalties = total_penalties


            elif total_penalties >= payment.amount:
                print('total penalties more or equal to paid amount')
                # Deduct penalties from payment amount
                total_penalties = max(total_penalties - payment.amount, 0)
                payment.amount = 0
                member.total_penalties = total_penalties  # Reset total penalties

            # elif total_penalties < payment.amount:
            #     # Deduct penalties from payment amount
            #     payment.amount = max(payment.amount - total_penalties, 0)
            #     member.total_penalties = 0  # Reset total penalties
            #     # Payment.objects.filter(payer=member.membership_number).update(status='PAID')
            #     member.penalized = 'NOT_PENALIZED'
            #     # Update status of all member payments to 'PAID'
            #     # member.payment_set.update(status='PAID')
            #     payments = Payment.objects.filter(member=member, status='PARTIALLY_PAID')
            #     for payment in payments:
            #       payment.status='PAID'
            #       payment.save()

            # update total_paid_for_case

            # Update member record (optional, could update in save method)
            member.save()

            # Save payment (now with potential penalty deduction)
            payment.save()
            # Update account balance based on payment method
            payment_method = payment.payment_method
            account = get_or_create_account_for_payment_method(payment_method)

            update_account_balance(account, payment.amount)
            

            # Update account balance based on payment method (if applicable)
            # ... (your existing logic for account balance update)

            messages.success(request, f'Payment Successful')
            return redirect('payments_list', case_number=payment.case_number)
        else:
            messages.error(request, f'Payment form invalid: {form.errors}')
    else:
        # Handle GET request (same as before)
        # ...
        form = PaymentForm()
    return render(request, 'pesa/make_payment.html', {'form': form})



# def make_payment(request):
#     if request.method == 'POST':
#         print(request.user)
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             case = Case.objects.get(case_number=case)
#             payment = form.save(commit=False)  # Don't commit save yet
#             member = payment.member
#             payment.receiver = request.user

#             # Get total penalties for the member
#             total_penalties = member.total_penalties

#             print(case)

#             if total_penalties == 0.00:
#                 # Deduct penalties from payment amount
#                 payment.amount = payment.amount
#                 member.total_penalties = case.set_contribution_amount - payment.amount  # Reset total penalties
#                 # payments = Payment.objects.filter(member=member, status='PARTIALLY_PAID')
#                 # for payment in payments:
#                 #   payment.status='PAID'
#                 #   payment.save()
#                 payment.save()

#             elif total_penalties >= payment.amount:
#                 # Deduct penalties from payment amount
#                 total_penalties = max(total_penalties - payment.amount, 0)
#                 # payment.amount = 0
#                 member.total_penalties = total_penalties  # Reset total penalties

#             elif total_penalties < payment.amount:
#                 # Deduct penalties from payment amount
#                 payment.amount = max(payment.amount - total_penalties, 0)
#                 member.total_penalties = 0  # Reset total penalties
#                 # Payment.objects.filter(payer=member.membership_number).update(status='PAID')
#                 member.penalized = 'NOT_PENALIZED'
#                 # Update status of all member payments to 'PAID'
#                 # member.payment_set.update(status='PAID')
#                 payments = Payment.objects.filter(member=member, status='PARTIALLY_PAID')
#                 for payment in payments:
#                   payment.status='PAID'
#                   payment.save()

#             # update total_paid_for_case

#             # Update member record (optional, could update in save method)
#             member.save()

#             # Save payment (now with potential penalty deduction)
#             payment.save()
#             # Update account balance based on payment method
#             payment_method = payment.payment_method
#             account = get_or_create_account_for_payment_method(payment_method)

#             update_account_balance(account, payment.amount)
            

#             # Update account balance based on payment method (if applicable)
#             # ... (your existing logic for account balance update)

#             messages.success(request, f'Payment Successful')
#             return redirect('payments_list', case_number=payment.case_number)
#         else:
#             messages.error(request, f'Payment form invalid: {form.errors}')
#     else:
#         # Handle GET request (same as before)
#         # ...
#         form = PaymentForm()
#     return render(request, 'pesa/make_payment.html', {'form': form})



def get_or_create_account_for_payment_method(payment_method):
  # Implement logic to get or create an account based on payment_method
  if payment_method == 'CASH':
    # Retrieve or create account for cash payments (e.g., by querying)
    return Account.objects.get_or_create(name='Cash Collection Account')[0]  # Replace with your logic
  elif payment_method == 'CHEQUE':
    # Retrieve or create account for Mpesa payments (e.g., by querying)
    return Account.objects.get_or_create(name='Cheque Collection Account')[0]  # Replace with your logic
  elif payment_method == 'MPESA':
    # Retrieve or create account for Mpesa payments (e.g., by querying)
    return Account.objects.get_or_create(name='Mpesa Collection Account')[0]  # Replace with your logic
  else:
    # Handle unexpected payment methods (optional)
    raise ValueError(f"Invalid payment method: {payment_method}")

def update_account_balance(account, amount):
  # account.balance += decimal.Decimal(amount)  # Convert amount to Decimal
  account.balance = decimal.Decimal(account.balance) + decimal.Decimal(amount)  # Convert both to Decimal
  account.save()  # Update the account balance


class AccountsListView(ListView):
  model = Account  # Specify the model to display
  template_name = 'pesa/accounts.html'  # Customize the template name
  context_object_name = 'accounts'  # Customize the context variable name (optional)

  def get_queryset(self):
    # Optional: Filter or modify the queryset here
    return super().get_queryset()

from decimal import Decimal

def calculate_mpesa_charge(amount):
  """
  This function calculates the Mpesa charge based on the provided amount.

  **Args:**
      amount (float): The amount of money being sent through Mpesa.

  **Returns:**
      float: The Mpesa charge for the given amount.

  **Note:** This function is based on the information available on the Safaricom website as of 2024-04-29.
          The actual charges might change, so it's recommended to refer to the official Safaricom website for the latest information.
  """

  # Define charge tiers based on the website information
  tiers = [
      (0, 49, 0.00, 0.00),
      (50, 100, 0.00, 11),
      (101, 500, 7.00, 29),
      (501, 1000, 13.00, 29),
      (1001, 1500, 23.00, 29),
      (1501, 2500, 33.00, 29),
      (2501, 3500, 53.00, 52),
      (3501, 5000, 57.00, 69),
      (5001, 7501, 78.00, 87),
      (7501, 10000, 90.00, 115),
      (10001, 15000, 100.00, 167),
      (15001, 20000, 105.00, 185),
      (20001, 35000, 108.00, 197),
      (35001, 50000, 108.00, 278),
      (50001, 250000, 108.00, 309),

  ]

  # Find the appropriate tier for the given amount
  for lower_bound, upper_bound, charge, withdraw_fee in tiers:
    # if lower_bound <= amount <= upper_bound:
    if (lower_bound is None or amount >= lower_bound) and (upper_bound is None or amount <= upper_bound):
      # return Decimal(str(withdraw_fee))
      return Decimal(str(charge)), Decimal(str(withdraw_fee))





from django.db import transaction

def transfer_between_accounts(request, from_account_id, to_account_id, amount, reason):
  """
  Transfers the specified amount from one account to another.

  Args:
      from_account_id (int): ID of the account transferring money.
      to_account_id (int): ID of the account receiving money.
      amount (Decimal): Amount to transfer.

  Raises:
      ValueError: If the transfer amount is negative or exceeds the from_account balance.
  """

  with transaction.atomic():
    # transfer_cost = 100
    # transfer_cost = calculate_mpesa_charge(amount)

    from_account = Account.objects.get(pk=from_account_id)
    to_account = Account.objects.get(pk=to_account_id)
    

    if amount <= 0:
      messages.error(request, "Transfer amount must be positive.")
      return redirect('pesa/accounts_transfers.html')
      # raise ValueError("Transfer amount must be positive.")

    if from_account.name.startswith('Mpesa'):
      withdraw_fee = calculate_mpesa_charge(amount)[1]
    else:
      withdraw_fee = 0

    # if amount <= 0:
    #   messages.error(request, "Transfer amount must be positive.")


    # if from_account.balance < amount:
    if from_account.balance < (amount - withdraw_fee):
      messages.warning(request, "Insufficient funds in the from account.")
      return redirect('pesa/accounts_transfers.html')
      # raise ValueError("Insufficient funds in the from account.")
    else:
      from_account.balance -= amount
    # if from_account.name.startswith('Mpesa'):
      # from_account.balance -= (amount - withdraw_fee)
    # else:
    #   from_account.balance -= amount
      from_account.save()

      to_account.balance += (amount - withdraw_fee)
      to_account.save()

      # Create transfer record


      Transfer.objects.create(
          from_account=from_account,
          to_account=to_account,
          amount=amount,
          reason = reason,
          withdraw_fee = withdraw_fee,
          transfered_by=request.user
        )

      messages.success(request, "Transfer successful!")
      return redirect('pesa/transfers.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required  # Optional: Restrict access if necessary
from .models import Account  # Assuming your model is in a file named models.py
from .forms import TransferForm  # Assuming you have a TransferForm defined

@login_required  # Optional: Add if user authentication is involved
def transfer(request):
  accounts = Account.objects.all()
  if request.method == 'POST':
    form = TransferForm(request.POST)
    if form.is_valid():
      # Extract form data
      from_account_id = form.cleaned_data['from_account'].id
      to_account_id = form.cleaned_data['to_account'].id
      amount = form.cleaned_data['amount']
      reason = form.cleaned_data['reason']

      try:
        # Perform transfer logic (consider transactions)
        transfer_result = transfer_between_accounts(request, from_account_id, to_account_id, amount, reason)
        if transfer_result:
          message = "Transfer successful!"
      except ValueError as e:
        message = f"Transfer failed: {e}"

      return render(request, 'pesa/accounts.html', {'form': form, 'message': message})
  else:
    form = TransferForm()
    accounts = Account.objects.all()  # Replace with appropriate logic to retrieve accounts

  return render(request, 'pesa/accounts_transfers.html', {'form': form, 'accounts': accounts})
  # return render(request, 'pesa/accounts_transfers.html', {'form': form, 'accounts': accounts})

















# def make_payment(request):
#   if request.method == 'POST':
#     # Handle form submission
#     form = PaymentForm(request.POST)
#     if form.is_valid():
#       form.save()  # Save the payment data to the database
#       messages.success(request, f'Payment Successful')
#       return redirect('payment_success_url')  # Replace with your success URL name
#   else:
#     # Handle GET request (display the registration form)
#     active_cases = Case.objects.filter(status='ACTIVE')  # Filter active cases
#     form = PaymentForm(queryset=active_cases)  # Initialize form with filtered queryset
#   return render(request, 'pesa/make_payment.html', {'form': form})



# class MakePaymentView(CreateView):
#     # ... your form fields here
#   model = Payment  # Your people model
#   fields = ['amount', 'payer', 'payment_method', 'receiver', 'member', 'case_number']  # Adjust as needed
#   # form_class = MembershipForm  # Your people registration form
#   template_name = 'pesa/make_payment.html'  # Template for the registration form

# def get_form_kwargs(self):
#     kwargs = super().get_form_kwargs()
#     active_cases = Case.objects.filter(status='ACTIVE')
#     print(f"Active Cases Query: {active_cases.query}")  # Inspect the generated SQL
#     kwargs['queryset'] = active_cases
#     return kwargs

# def register_payment(request):
#   if request.method == 'POST':
#     # Handle form submission
#     form = PaymentForm(request.POST)
#     if form.is_valid():

#       form.save()  # Save the member data to the database
      
#       # Handle successful registration (e.g., redirect to success page)
#       messages.success(request, f'Payment Successful')
#       return url
#       # return redirect('pesa/payment_list')  # Replace 'success_url' with actual URL
#   else:
#     # Handle GET request (display the registration form)
#     form = PaymentForm()
#   return render(request, 'pesa/payment.html', {'form':form})
