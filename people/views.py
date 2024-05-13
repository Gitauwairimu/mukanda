from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, View  # Correct import for ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User  # Optional for authentication
from .forms import MembershipForm, MemberUpdateForm, CaseForm
from django import forms
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import UpdateView
from django.shortcuts import render, redirect
from .models import Case, Member
from django.urls import reverse_lazy

# # Create your views here.
# from .models import Member  # Import your Member model

from django.views.generic import CreateView
from people.models import Member, RuleProposal
from pesa.models import Payment, Account, Penalty
from .forms import DependentForm, RuleForm, ProposalRuleForm  # Assuming you have a DependentForm

from datetime import date

from django.db.models import Count, Q  # Import required modules

from decimal import Decimal


from django.contrib.auth import logout
from django.db.models import Q, Sum  # Import for complex filtering

# def logout_view(request):
#   logout(request)
#   # Redirect to logout success page


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
      (0, 49, 0.00),
      (50, 100, 0.00),
      (101, 500, 33.00),
      (501, 1000, 43.00),
      (1001, 1500, 54.00),
      (1501, 2500, 70.00),
      (2501, 3500, 88.00),
      (3501, 5000, 107.00),
      (5001, 7501, 126.00),
      (7501, 10000, 126.00),
      (10001, 15000, 126.00),
      (15001, 20000, 105.00),
      (20001, 35000, 108.00),
      (35001, 50000, 108.00),
      (50001, 250000, 108.00),

  ]

  # Find the appropriate tier for the given amount
  for lower_bound, upper_bound, charge in tiers:
    # if lower_bound <= amount <= upper_bound:
    if (lower_bound is None or amount >= lower_bound) and (upper_bound is None or amount <= upper_bound):
      return Decimal(str(charge))


    # if (lower_bound is None or amount >= lower_bound) and (upper_bound is None or amount <= upper_bound):


def generate_case_contribution_report(case):
  """
  Generates a report for a specific case and its contributions.

  Args:
      case: A Case object representing the case for which the report is generated.

  Returns:
      A dictionary containing the report data.
  """
  # contributions = Payment.objects.all()  # Get all contributions for the case
  contributions = Payment.objects.filter(case_number=case)
#   contributions_total = Payment.objects.filter(case_number=case).aggregate(total_amount=Sum('amount'))['total_amount']
#   contributions_total = Payment.objects.filter(case_number=case).aggregate(total_amount=Sum('amount')).get_or_default(0)


  contributions_total = Payment.objects.filter(case_number=case).aggregate(total_amount=Sum('amount'))['total_amount']

  if contributions_total is None:
    contributions_total = 0
  else:
    contributions_total = int(contributions_total)

  confirmation_fee = int(0.1 * contributions_total)
  # charged = (contributions_total + confirmation_fee + 2000)
  amount_to_send = contributions_total - confirmation_fee - 2000

  if amount_to_send < 0:
    mpesa_charge = 0
  else:
    mpesa_charge = calculate_mpesa_charge(amount_to_send)

  # mpesa_charge = calculate_mpesa_charge(amount_to_send)

  net_amount_sent = contributions_total - 2000 - mpesa_charge - confirmation_fee
  net_amount_sent = int(net_amount_sent)
#   print(f"Mpesa charge for KES {amount_to_send:.2f} is KES {mpesa_charge:.2f}")

#   accounts = Account.objects.all()
  
  # Count contributions based on payment status (implement logic for full, partial, and no payment
  full_payment_count = contributions.filter(status='PAID').count()
  partial_payment_count = contributions.filter(status='PARTIALLY_PAID').count()
  
  eligible_members = Member.objects.filter(
    Q(join_date__lt=case.contribution_window_start) &
    ~Q(status='DECEASED') &
    Q(dependent='NOT DEPENDENT')).count()
  
  no_payment_count = eligible_members - full_payment_count - partial_payment_count

#   no_payment_count = contributions.filter(Q(status='UNPAID') | Q(status='INVALID')).count()



  # Get information about accounts receiving payments (logic depends on your model)
#   payment_accounts = set(contribution.payment_account for contribution in contributions if contribution.payment_account)  # Remove duplicates
#   payment_accounts = set(accounts.name for contribution in contributions if accounts.name)  # Remove duplicates
#   payment_accounts = accounts  # Remove duplicates


  # payment_accounts = accounts
#   accounts_balances = accounts_balances

  # Get membership details of the deceased
  deceased_member = case.deceased_name
  deceased_details = {
      'first_name': deceased_member.first_name,  # Replace with your member model's full_name method
      'other_name': deceased_member.other_name,
      'last_name': deceased_member.last_name,
      'next_of_kin': deceased_member.next_of_kin,
      'next_of_kin_contact': deceased_member.next_of_kin_contact,
      'address': deceased_member.address,
      'id_number': deceased_member.id_number,
      'membership_number': deceased_member.membership_number,
      'date_of_death': case.date_of_death,
      
  }

  # accounts = Account.objects.all().values('name', 'balance')  # Retrieve account details (name and balance)
  # accounts = Account.objects.all().values('name', 'balance')
  # Combine data into report dictionary

  # print(accounts) 
  report_data = {
      'case_number': case.case_number,
      'deceased_details': deceased_details,
      'full_payment_count': full_payment_count,
      'partial_payment_count': partial_payment_count,
      'no_payment_count': no_payment_count,
      'mpesa_charge': mpesa_charge,
      'net_amount_sent': net_amount_sent,
      'confirmation_fee': confirmation_fee,

      # 'payment_accounts': list(accounts),  # Convert to list for report output
      # 'accounts_balances': [account['balance'] for account in accounts],  # Extract balances from accounts data
      # 'accounts': accounts,  # Extract balances from accounts data
  }
  return report_data



def penalty_apply(case):
    # if date.today() > case.contribution_window_end and case.run_penalties == 'penalties_not_run':
    if date.today() > case.contribution_window_end and case.run_penalties == 'penalties_not_run':
        # Retrieve all payments for the case
        # payments = Payment.objects.filter(case_number=case)
        payments = Payment.objects.filter(case_number=case, status='PAID')

        # if contribution.total_paid_for_case >= contributions.set_contribution_amount:
        #   pass

        # Get a list of member IDs who have made payments
        # paid_member_ids = payments.values_list('member__id', flat=True)
        paid_member_ids = payments.values_list('member_id', flat=True)

        # Filter members who haven't paid (excluding those with payments)
        unpaid_members = Member.objects.filter(~Q(membership_number__in=paid_member_ids),~Q(status='DECEASED'))

        # Update status of unpaid members
        unpaid_members.update(penalized='PENALIZED')

        # Update run_penalties field directly on the queryset (if applicable)
        Case.objects.filter(pk=case.pk).update(run_penalties='run_penalties')

        return unpaid_members
    else:
      print("Case doesn't meet requirements")


      

def penalty_create(case):
# def penalty_create():
    # case = Case.objects.get(pk=case_pk)
    # case = Case.objects.last()
    if date.today() > case.contribution_window_end and case.run_penalties == 'penalties_not_run':
        
        alive_members = Member.objects.filter(
            Q(join_date__lt=case.contribution_window_start) &
            ~Q(status='DECEASED') &
            Q(dependent='NOT DEPENDENT')  # Filter for non-dependent members
        )

        for member in alive_members:
            total_expected_contribution = case.set_contribution_amount  # Assuming a field in Case
            
            # Calculate total paid by the member for this case (replace with appropriate logic)
            # total_paid = Payment.objects.filter(case=case, member=member).aggregate(sum_=Sum('amount'))['sum_'] or 0
            total_paid = Payment.objects.filter(member=member, case_number=case).aggregate(total_contributed=Sum('amount'))
            # total_paid = Payment.objects.filter(member=member, case_number=case, status='PAID').aggregate(total_contributed=Sum('amount'))
            total_amount_paid = total_paid['total_contributed']
            # total_paid = Payment.objects.filter(case=case, member=membership_number).aggregate(sum_=Sum('amount'))['sum_'] or 0

            if total_amount_paid is not None:
              if total_amount_paid < total_expected_contribution:
                penalty_amount = total_expected_contribution - total_amount_paid
                Penalty.objects.create(member=member, case=case, amount=penalty_amount, description="Late contribution fee")
                member.total_penalties += penalty_amount
                member.save()
                print('Full Calculated Penalties')
                # penalty_apply(case)  # Call the penalty_apply function if needed
              elif total_amount_paid >= total_expected_contribution:
                print('No penalties created')
              # else total_amount_paid >= total_expected_contribution: # Overpayment shouldn't be allowed
            else:
              penalty_amount = total_expected_contribution
              Penalty.objects.create(member=member, case=case, amount=penalty_amount, description="Late contribution fee")
              member.total_penalties += penalty_amount
              member.save()
              print('Full penalties')
            #           # Handle the case where total_amount_paid is None (e.g., log a message, create a placeholder penalty, etc.)


            # if total_expected_contribution > total_amount_paid:
            #     penalty_amount = total_expected_contribution - total_amount_paid
            #     penalty = Penalty.objects.create(member=member, case=case, amount=penalty_amount, description="Late contribution fee")
            #     # penalty_apply(case)  # Call the penalty_apply function if needed
            #     print('Success')
        Case.objects.filter(pk=case.pk).update(run_penalties='run_penalties', status='INACTIVE')
        # Case.objects.filter(pk=case.pk).update(status='INACTIVE')
        # Update case status to INACTIVE after penalties are applied

        print('Run Penalties Done. Case marked as INACTIVE.')
    else:
      print('Unsuccessful')

        # ... (consider redirect or other actions after processing all members) ...


# from django.db.models import F
# penalized_members = Member.objects.filter(status='PENALIZED').select_related('member_cases')  # Retrieve cases in one query

# Alternatively, if you need more data from the Case model:
# penalized_members = Member.objects.filter(status='PENALIZED')
# cases = Case.objects.filter(membership_number__in=penalized_members)


# penalized_members = Member.objects.filter(penalized='PENALIZED')
# cases = Case.objects.filter(membership_number__in=penalized_members)
# for member in penalized_members:
#     case = member.member_cases  # Assuming each member has only one relevant case
    
#     # Assuming a 'set_contribution_amount' field in the Case model:
#     penalty_amount = case.set_contribution_amount - member.total_contributions  # Replace 'total_contributions' with the appropriate field for contributed amount

#     # Set the penalty amount
#     case.penalty_amount = penalty_amount
#     case.save()


        # {% for penalty in penalized_member.penalties.all %}
def cash_out(case):
  """
  This function handles the cash out process for a given case.

  Args:
      case: The Case object representing the case to be cashed out.
  """

  # Retrieve case data
  contributions_total = Payment.objects.filter(case_number=case).aggregate(total_amount=Sum('amount'))['total_amount']

  # Calculate net amount to send
  # cash_account = Account.objects.filter(name__startswith='Cash')[0]
  # cash_account.balance - cash_total
  # cash_account.save()

  mpesa_account = Account.objects.filter(name__startswith='Mpesa')[0]
  mpesa_account.balance - mpesa_total
  mpesa_account.save() 

  # cheque_account = Account.objects.filter(name__startswith='Cheque')[0]
  # cheque_account.balance - cheque_total
  # cheque_account.save()

  # contributions_total - contributions_total

  # Update case status
  case.cashed_out = 'cashed_out'  # Or another value indicating cashed out
  case.save()

  # Process cash out logic
  # subtract_from_accounts(case.id, contributions_total, mpesa_charge)  # Example function call
  # ... (Optional) Additional cash out processing (money transfer, transaction recording)


# if case.cashed_out == 'not_cashed_out':
#     cash_out(case)

from django.db.models import Prefetch
from pesa.views import get_or_create_account_for_payment_method
def case_contribution_report(request, case_pk):
  case = Case.objects.get(pk=case_pk)
  # member = Member.objects.all()
#   # Retrieve all payments for the case
  payments = Payment.objects.filter(case_number=case, status='PAID') # For payments matching or over set contribution
#   # Get a list of member IDs who have made payments
  paid_member_ids = payments.values_list('member_id', flat=True)
  

#   # Filter members who haven't paid (excluding those with payments)
  # Prefetch penalties for the case
  penalty_prefetch = Prefetch(
      'penalties', queryset=Penalty.objects.filter(case=case)
  )
#   unpaid_members = Member.objects.filter(~Q(membership_number__in=paid_member_ids), ~Q(status='DECEASED')).prefetch_related(penalty_prefetch)
  unpaid_members = Member.objects.filter(
    ~Q(membership_number__in=paid_member_ids),
    ~Q(status='DECEASED'),
    dependent__in=('NOT DEPENDENT',)  # Assuming 'NOT DEPENDENT' is the desired value
).prefetch_related(penalty_prefetch)


  # unpaid_members = Member.objects.filter(~Q(membership_number__in=paid_member_ids), ~Q(status='DECEASED')).prefetch_related('penalties')  # Prefetch penalties for efficiency

  # unpaid_members = penalty_apply(case)

  # penalties = Penalty.objects.filter(case=case) # Get all penalties for the case

  # Retrieve total amounts for each payment method
  # cash_account = get_or_create_account_for_payment_method(payment_method='CASH')
  cash_payments = Payment.objects.filter(case_number=case, payment_method='CASH')
  cash_total = sum(payment.amount for payment in cash_payments)

  # mpesa_account = get_or_create_account_for_payment_method(payment_method='MPESA')
  mpesa_payments = Payment.objects.filter(case_number=case, payment_method='MPESA')
  mpesa_total = sum(payment.amount for payment in mpesa_payments)

  # cheque_account = get_or_create_account_for_payment_method(payment_method='CHEQUE')
  cheque_payments = Payment.objects.filter(case_number=case, payment_method='CHEQUE')
  cheque_total = sum(payment.amount for payment in cheque_payments)


  accounts = Account.objects.all().values('name', 'balance')
  # account_ids = payments.values_list('account_id', flat=True)  # Get account IDs from payments
  # accounts = Account.objects.filter(id__in=account_ids).values('name', 'balance')
  contributions_total = Payment.objects.filter(case_number=case).aggregate(total_amount=Sum('amount'))['total_amount']


  date_of_death = case.date_of_death
#   eligible_members = Member.objects.filter(join_date__gt=date_of_death, status='ACTIVE') # Add logic for members who are still alive at contribution_window_end
  total_members = Member.objects.filter(
    Q(join_date__lt=case.contribution_window_start) &
    ~Q(status='DECEASED') &
    Q(dependent='NOT DEPENDENT')).count()

#   total_members = eligible_members.count() # define eligible members as those whose join_date is earlier than date of start of contributions, and they dont die during the period between opening of case and closing of the case
  report_data = generate_case_contribution_report(case)
  context = {'report_data': report_data, 'accounts': accounts, 'cheque_total': cheque_total, 'mpesa_total': mpesa_total, 'cash_total': cash_total, 'contributions_total': contributions_total, 'case':case, 'total_members': total_members, 'unpaid_members': unpaid_members}
  # penalty_apply(case)
  penalty_create(case)
  # penalty_create()
#   get_last_created_case()
#   case.update(run_penalties='run_penalties')
#   case.run_penalties = 'run_penalties'
#   case.save()
  # member = Member.objects.filter(pk=membership_number)
  # penalty_create(case, member)
  return render(request, 'people/case_contribution_report.html', context)


def propose_rule(request):
    if request.method == 'POST':
        form = ProposalRuleForm(request.POST)  # Assuming you have a ProposalRuleForm
        if form.is_valid():
            rule = form.save()
            return redirect('rules')  # Redirect on success
    else:
        form = ProposalRuleForm()
    return render(request, 'people/rule_proposal_create.html', {'form': form})

def discard_proposal(request, proposal_id):
  """
  Function-based view to handle rule deletion.

  Args:
      request: HttpRequest object containing request information.
      rule_id: Integer representing the primary key of the rule.

  Returns:
      HttpResponse redirecting to the rule list view after deletion or displaying an error message.
  """
  try:
      proposal = RuleProposal.objects.get(pk=proposal_id)
  except RuleProposal.DoesNotExist:
      messages.error(request, 'Proposal not found.')
      return redirect('rules')  # Redirect to list view on error

  if request.method == 'POST':
      proposal.delete()
      messages.success(request, 'Proposal discarded successfully.')
      return redirect('rules')  # Redirect to list view on success

  # Not a POST request, display confirmation prompt (optional)
  context = {'proposal': proposal}
  return render(request, 'people/proposal_confirm_delete.html', context)  # Confirmation template (optional)

def edit_proposal(request, proposal_id):
  """
  Function-based view to handle rule editing.

  Args:
      request: HttpRequest object containing request information.
      rule_id: Integer representing the primary key of the rule.

  Returns:
      HttpResponse rendered with the rule edit form or redirecting after update.
  """
  try:
      proposal = RuleProposal.objects.get(pk=proposal_id)
  except RuleProposal.DoesNotExist:
      messages.error(request, 'Proposal not found.')
      return redirect('rules')  # Redirect to list view on error

  if request.method == 'POST':
      form = ProposalRuleForm(request.POST, instance=proposal)  # Pre-populate form with proposal data
      if form.is_valid():
          form.save()
          messages.success(request, 'Proposal updated successfully.')
          return redirect('rules')  # Redirect to detail view on success
  else:
      form = ProposalRuleForm(instance=proposal)  # Create form with initial rule data

  context = {'form': form}
  return render(request, 'people/proposal_edit.html', context)  # Use the same form template


from django.contrib.auth.decorators import login_required  # Restrict access
from django.db.models import Max

# @login_required
def approve_proposal(request, proposal_id):
  """
  View function for approving a rule proposal and creating a new rule.

  Args:
      request: HttpRequest object containing request information.
      proposal_id: Integer representing the primary key of the rule proposal.

  Returns:
      HttpResponse redirecting to the rule list view after approval.
  """
  try:
      proposal = RuleProposal.objects.get(pk=proposal_id)
    #   if proposal.status == 'proposed' and request.user.has_perm('people.approve_rule'):  # Check permission
      if proposal.status == 'proposed':
          proposal.status = 'approved'
          proposal.save()
          

        #   Create a new Rule object with approved proposal content (excluding proposer)
          highest_order_value = Rule.objects.aggregate(max_order=Max('order'))
        # Access the actual maximum value from the dictionary
          if highest_order_value:  # Check if any rules exist (optional)
            order_value = highest_order_value['max_order'] + 1
          else:
            # Handle scenario with no existing rules (optional)
            order_value = 0  # Or set a default starting order

          Rule.objects.create(
              title=proposal.title,
              content=proposal.content,
              order=order_value,
          )
          messages.success(request, 'Rule proposal approved and rule created.')
      else:
          messages.error(request, 'Invalid proposal or insufficient permissions.')
  except RuleProposal.DoesNotExist:
      messages.error(request, 'Rule proposal not found.')
  return redirect('rules')  # Redirect to rule list view


def calculate_age(born):
  today = date.today()
  age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
  return age

from .models import Rule  # Assuming the model is in the same app

def create_rule(request):
    if request.method == 'POST':
        form = RuleForm(request.POST)  # Assuming you have a RuleForm
        if form.is_valid():
            rule = form.save()
            return redirect('rule_detail', rule.id)  # Redirect on success
    else:
        form = RuleForm()
    return render(request, 'people/rule_create.html', {'form': form})



from .models import Rule

def list_rules(request):
  """
  Function-based view to display a list of all rules.

  Args:
      request: HttpRequest object containing request information.

  Returns:
      HttpResponse rendered with the rule list template.
  """

  rules = Rule.objects.all().order_by('order')  # Rule.orders by order field (optional)
  # rules = Rule.objects.all().order_by('-order') # Flips the order of listing
  # proposed_rules = Rule.objects.all().order_by('order')
  proposals = RuleProposal.objects.filter(status='proposed')
#   proposals = RuleProposal.objects.all()

  context = {'rules': rules, 'proposals': proposals}
  return render(request, 'people/rule_list.html', context)

def rule_detail(request, rule_id):
  """
  Function-based view to display details for a single rule.

  Args:
      request: HttpRequest object containing request information.
      rule_id: Integer representing the primary key of the rule.

  Returns:
      HttpResponse rendered with the rule detail template.
  """
  try:
      rule = Rule.objects.get(pk=rule_id)
  except Rule.DoesNotExist:
      context = {'error': 'Rule not found.'}
      return render(request, 'people/errors/error.html', context)  # Error template

  context = {'rule': rule}
  return render(request, 'people/rule_detail.html', context)

from django.shortcuts import redirect
from django.contrib import messages  # for displaying messages

from .models import Rule


def delete_rule(request, rule_id):
  """
  Function-based view to handle rule deletion.

  Args:
      request: HttpRequest object containing request information.
      rule_id: Integer representing the primary key of the rule.

  Returns:
      HttpResponse redirecting to the rule list view after deletion or displaying an error message.
  """
  try:
      rule = Rule.objects.get(pk=rule_id)
  except Rule.DoesNotExist:
      messages.error(request, 'Rule not found.')
      return redirect('rules')  # Redirect to list view on error

  if request.method == 'POST':
      rule.delete()
      messages.success(request, 'Rule deleted successfully.')
      return redirect('rules')  # Redirect to list view on success

  # Not a POST request, display confirmation prompt (optional)
  context = {'rule': rule}
  return render(request, 'people/rule_confirm_delete.html', context)  # Confirmation template (optional)

from django.shortcuts import render, redirect
from django.contrib import messages  # for displaying messages
from .models import Rule
from .forms import RuleForm  # Assuming you have a RuleForm class

def edit_rule(request, rule_id):
  """
  Function-based view to handle rule editing.

  Args:
      request: HttpRequest object containing request information.
      rule_id: Integer representing the primary key of the rule.

  Returns:
      HttpResponse rendered with the rule edit form or redirecting after update.
  """
  try:
      rule = Rule.objects.get(pk=rule_id)
  except Rule.DoesNotExist:
      messages.error(request, 'Rule not found.')
      return redirect('rules')  # Redirect to list view on error

  if request.method == 'POST':
      form = RuleForm(request.POST, instance=rule)  # Pre-populate form with rule data
      if form.is_valid():
          form.save()
          messages.success(request, 'Rule updated successfully.')
          return redirect('rule_detail', rule.id)  # Redirect to detail view on success
  else:
      form = RuleForm(instance=rule)  # Create form with initial rule data

  context = {'form': form}
  return render(request, 'people/rule_edit.html', context)  # Use the same form template


from django.views.generic import CreateView
from .forms import DependentForm  # Assuming DependentForm is in the same directory
from .models import Member  # Assuming models in the same directory

class AddDependentView(CreateView):
    model = Member
    form_class = DependentForm
    template_name = 'people/add_dependent.html'

    # def get_success_url(self):
    #     # Redirect to member detail page after successful creation
    #     member_id = self.kwargs['member_id']
    #     return reverse('member_detail', kwargs={'pk': member_id})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.kwargs['member_id']
        membership_number = self.request.POST.get('membership_number')

        # Prioritize member_id from URL for robustness (optional)
        if member_id:
            try:
                member = Member.objects.get(pk=member_id)
            except Member.DoesNotExist:
                member = None  # Handle case where member_id is not found

        elif membership_number:
            try:
                member = Member.objects.get(membership_number=membership_number)
            except Member.DoesNotExist:
                member = None  # Handle case where membership_number is not found

        else:
            member = None  # Handle case where neither is available

        context['member'] = member  # Add member object to context (if retrieved)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)  # Don't save yet
        # member = context['member']
        context = self.get_context_data()
        member = context.get('member')
        # Inherit address, next of kin, and next of kin contact from member
        self.object.address = member.address
        self.object.next_of_kin = f"{member}"
        # self.object.next_of_kin = member.membership_number
        self.object.phone_number = member.phone_number
        self.object.next_of_kin_contact = member.phone_number
        # self.object.email = 'dependent@member.com'
        # self.object.email = member.email
        self.object.dependent = 'DEPENDENT'  # Set dependent to 'DEPENDENT'

        self.object.save()  # Save the object with inherited and dependent set
        return super().form_valid(form)



class AllMemberListView(ListView):
  model = Member  # Specify the model to retrieve data from
  template_name = 'member_list.html'  # Template to render the list

  def get_queryset(self):
    """
    Override the default queryset to potentially filter or order members.
    """
    return Member.objects.all()  # Retrieve all members by default

from django.shortcuts import render, get_object_or_404
from .models import Member

# Import for messages (optional)

# def active_members_list(request):
#   search_query = request.GET.get('search_query', '')
#   if search_query:
#     filters = Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
#     try:
#       membership_number = int(search_query)
#       filters |= Q(membership_number=membership_number)
#       print(f"Searching for membership number: {membership_number}")  # Debugging print
#     except ValueError:
#       filters |= Q(id_number__icontains=search_query)
#       print(f"Searching by ID number (case-insensitive): {search_query}")  # Debugging print
#     active_members = Member.objects.filter(filters)
#     print(f"Filtered members: {active_members.query}")  # Print the actual query used
#   else:
#     active_members = Member.objects.filter(status='ACTIVE')  # Filter for active members

#   context = {
#       'active_members': active_members,
#       'search_query': search_query,  # Optional: Pass search_query to template for display
#   }

#   # Add a message if using the message framework (optional)
#   if search_query and not active_members.exists():
#     messages.info(request, 'No search results found.')

#   return render(request, 'people/active_member_list.html', context)



def active_members_list(request):
  search_query = request.GET.get('search_query', '')
  if search_query:
    try:
      # Convert search_query to an integer (assuming it represents a number)
      if len(search_query) < 5: 
        membership_number = int(search_query)
        active_members = Member.objects.filter(membership_number=membership_number)  # Exact match
      else:
        filters = Q(id_number__icontains=search_query)  # Search by ID number (case-insensitive)
        print(f"Searching by ID number (case-insensitive): {search_query}")  # Debugging print
        active_members = Member.objects.filter(filters)
        print(f"Filtered members: {active_members.query}")
    except ValueError:
      # Handle cases where search_query is not a valid integer
      active_members = Member.objects.filter(
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(id_number__icontains=search_query)   # Add membership_number search
    )  # Empty queryset (no results)
      messages.warning(request, 'Invalid membership number format. Please enter a number.')  # Add a message (optional)
  else:
    active_members = Member.objects.filter(status='ACTIVE')  # Filter for active members

  context = {
      'active_members': active_members,
  }
  return render(request, 'people/active_member_list.html', context)



# def active_members_list(request):
#   search_query = request.GET.get('search_query', '')  # Get search query from GET parameters
#   if search_query:
#     active_members = Member.objects.filter(
#         Q(first_name__icontains=search_query) |
#         Q(last_name__icontains=search_query) |
#         Q(id_number__icontains=search_query) |
#         Q(membership_number__icontains=search_query)  # Add membership_number search
#     )
#   else:
#     active_members = Member.objects.filter(status='ACTIVE')  # Filter for active members

#   context = {
#       'active_members': active_members,
#   }

  # Ensure the return statement is indented here
  return render(request, 'people/active_member_list.html', context)


class MemberDetailView(DetailView):
    model = Member
    template_name = 'people/member_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = self.get_object()  # Access the retrieved member object

        # Add or modify context data as needed
        context['full_name'] = f"{member.first_name} {member.other_name} {member.last_name}"
        # context['date_of_birth'] = member.dob  # Assuming date_of_birth field exists
        context['address'] = member.address
        context['gender'] = member.gender
        context['next_of_kin'] = member.next_of_kin
        context['next_of_kin_contact'] = member.next_of_kin_contact
        context['phone_number'] = member.phone_number
        context['passport_photo'] = member.passport_photo.url
        context['num_dependents_listed_as_next_of_kin'] = Member.objects.filter(next_of_kin=member).count()
        context['dependents'] = Member.objects.filter(next_of_kin=member)
        context['today'] = today = date.today()

        return context




from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .forms import MemberUpdateForm
from .models import Member

class EditMemberDetailView(UpdateView):
    model = Member
    form_class = MemberUpdateForm
    template_name = 'people/edit_member_details.html'

    def get_success_url(self):
        member = self.object  # Access the updated member object
        return member.get_absolute_url()  # Redirect to member's detail page

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')  # Get member ID from URL argument
        return get_object_or_404(Member, pk=pk)  # Retrieve member object

    def form_valid(self, form):
        """
        Handle successful form submission (member details update).
        """
        response = super().form_valid(form)
        messages.success(self.request, f"Member details for {form.cleaned_data['first_name']} {form.cleaned_data['last_name']} updated successfully!")
        return response

    def form_invalid(self, form):
        """
        Handle unsuccessful form submission (member details update failure).
        """
        messages.error(self.request, "Failed to update member details. Please check the form and try again.")
        return super().form_invalid(form)

from django.views.generic import CreateView
from .forms import MembershipForm

class RegisterMemberView(CreateView):
  model = Member
  form_class = MembershipForm
  template_name = 'people/registration_form.html'
  success_url = reverse_lazy('active_members')  # Replace with actual URL for success page

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    return context


# def register_member(request):
#   if request.method == 'POST':
#     form = MembershipForm(request.POST, request.FILES)
#     if form.is_valid():
#       member = form.save(commit=False)  # Don't save yet
#       user = User.objects.create_user(
#           username=form.cleaned_data['username'],
#           password=form.cleaned_data['password1']
#       )
#       member.user = user
#       member.save()
#       messages.success(request, 'Member registration successful!')
#       # Consider redirecting to a success page (optional)
#       return redirect('active_members')  # Replace with actual URL
#     else:
#       messages.error(request, 'Please correct the errors below.')
#   else:
#     form = MembershipForm()

#   # Add Bootstrap classes to form fields (same as before)
#   # ...

#   context = {'form': form}
#   return render(request, 'people/registration_form.html', context)

from django.utils import timezone

def register_member(request):
  if request.method == 'POST':
    form = MembershipForm(request.POST, request.FILES)
    if form.is_valid():
      member = form.save(commit=False)  # Don't save yet
      user = User.objects.create_user(
          username=form.cleaned_data['username'],
          password=form.cleaned_data['password1']
      )
      member.user = user
      member.join_date = timezone.now()
      member.save()
      messages.success(request, 'Member registration successful!')
      # Consider redirecting to a success page (optional)
      return redirect('active_members')  # Replace with actual URL
    else:
      messages.error(request, 'Please correct the errors below.')
  else:
    form = MembershipForm()

  # Add Bootstrap classes to form fields (same as before)
  # ...

  context = {'form': form}
  return render(request, 'people/registration_form.html', context)



# def register_member(request):
#   if request.method == 'POST':
#     form = MembershipForm(request.POST, request.FILES)
#     if form.is_valid():
#       form.save()
#       messages.success(request, 'Member registration successful!')
#       # Consider redirecting to a success page (optional)
#       return redirect('active_members')  # Replace with actual URL
#     else:
#       messages.error(request, 'Please correct the errors below.')
#   else:
#     form = MembershipForm()

#   # Add Bootstrap classes to form fields
#   for field in form.visible_fields():
#     field.field.widget.attrs['class'] = 'form-control'

#   context = {'form': form}
#   return render(request, 'people/registration_form.html', context)

 

class DeleteMemberView(View):
    def post(self, request, pk):  # Handle POST requests for deletion
        member = get_object_or_404(Member, pk=pk)
        member.delete()
        return redirect('member_list')  # Replace with appropriate URL




# Send sms to list notifying them of case open and window


from django.db.models import Q  # Import for complex filtering

def get_non_deceased_member_phone_numbers():
    """
    Retrieves a list of phone numbers from non-deceased members.

    This function assumes the following:
        - The `Member` model has a `phone_number` field and a boolean field
          like `is_deceased` to indicate deceased status.

    Returns:
        A list of phone numbers (strings) from non-deceased members.
    """

    # Filter members who are not deceased (is_deceased=False)
    non_deceased_members = Member.objects.exclude(status='DECEASED')

    # Extract phone numbers from the filtered queryset
    phone_numbers = [member.phone_number for member in non_deceased_members]

    return phone_numbers

# Example usage (assuming you have a way to execute Python code in your Django environment)
phone_numbers = get_non_deceased_member_phone_numbers()


# def clean_phone_numbers(phone_numbers):
#     """
#     Cleans a list of phone numbers by removing "+254" or "254" prefix and replacing with "0".

#     Args:
#         phone_numbers: A list of phone number strings.

#     Returns:
#         A new list with cleaned phone numbers.
#     """
#     cleaned_numbers = []
#     for number in phone_numbers:
#         # Remove leading "+" sign (if present)
#         number = number.lstrip('+')
#         # Remove leading "254" (if present)
#         number = number.replace('254', '', 1)
#         # Prepend "0" if the number doesn't already start with it
#         if not number.startswith('0'):
#             number = '0' + number
#         cleaned_numbers.append(number)
        
#     return cleaned_numbers


def clean_phone_numbers(phone_numbers):
  """
  This function cleans a list of phone numbers to ensure they are in the format:
  +254XXXXXXXXX or XXXXXXXXX (without country code)

  Args:
      phone_numbers: A list of phone numbers (strings)

  Returns:
      A list of cleaned phone numbers (strings)
  """
  cleaned_numbers = []
  for number in phone_numbers:
    # Remove all non-numeric characters
    number = ''.join(char for char in number if char.isdigit())

    # If number starts with 0, remove it and add +254
    if number.startswith('0'):
      number = '+254' + number[1:]  # Remove leading 0 and prepend +254
    # If number starts with 254, add + at the beginning (assuming it's already the full number)
    elif number.startswith('254'):
      number = '+' + number  # Add + if it's the full number starting with 254
    
    # Add the cleaned number to the list
    cleaned_numbers.append(number)
  return cleaned_numbers


from django.shortcuts import render
def dashboard(request):
    context = {}
    return render(request, 'people/dashboard.html', context)

from decouple import config

import os
import africastalking as at
username = config('africastalking_username')
api_key = config('africastalking_api_key')
at.initialize(username, api_key)
sms = at.SMS


# Define your list of phone numbers (including country code)
# phone_numbers = ["+254735669452", "+254720051528",]
phone_numbers = clean_phone_numbers(phone_numbers)

def send_messages(request, case):
    # phone_numbers = clean_phone_numbers(phone_numbers)
    print(phone_numbers)
    for number in phone_numbers:
        name = "Member"  # You can personalize names if available
        lesson = "Sample Lesson"
        lesson_date = "Friday 12 March at 8.00 am "
        # message = f"hey {name}  Kindly note {lesson} lecture is scheduled on {lesson_date}"
        message = f"New Ananas Welfare member #{case.membership_number}  lost a dependant. Pls send Case #{case} contribution of KES {case.set_contribution_amount} to {case.mpesa_number} by {case.contribution_window_end}."
        # use if conditional to customise msg for members and dependents
        try:
            response = sms.send(message, [number])
            print(response)
        except Exception as e:
            print(f"Uh oh we have a problem: {e}")


# send_messages()

def create_case(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        
        if form.is_valid():
            # user = request.user  # Assuming you have access to the current user
            # Get the membership number from the cleaned form data
            membership_number = form.cleaned_data['membership_number']
            # membership_number = form.cleaned_data['membership_number']
            member = Member.objects.get(membership_number=membership_number.membership_number)
            print(f"Retrieved membership number: {membership_number}")


            # Check for existing case associated with the user's membership number
            existing_case = Case.objects.filter(membership_number=form.cleaned_data['membership_number']).exists()
            
            if existing_case:
                messages.error(request, "A case already exists for the provided membership number.")
                return redirect('case_list')  # Redirect to case list

            case = form.save(commit=False)
            if member.dependent == 'DEPENDENT':
                case.set_contribution_amount = 100 # Set contribution amount for dependents (logic here)
            else:
                case.set_contribution_amount = 200 # Set contribution amount for non-dependents (logic here)
            # Proceed with saving the new case if no existing case found
            case.save()

            # Send SMS notification (replace with your actual SMS function)
            # send_messages(request, case)
            messages.success(request, "Case successfully created.")
                
            return redirect('case_list')  # Redirect to case list
    else:
        form = CaseForm()

    context = {
        'form': form,
        # ... other context data ...
    }

    return render(request, 'people/case_create.html', context)



class CaseListView(ListView):
  model = Case  # Specify the model to retrieve data from
  template_name = 'people/case_list.html'  # Template to render the list

  def get_queryset(self):
    """
    Override the default queryset to potentially filter or order members.
    """
    return Case.objects.all()  # Retrieve all members by default



