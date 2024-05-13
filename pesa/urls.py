# finances/urls.py
from django.urls import path
from . import views  # Import views from the finances app

# from finances.views import PaymentsListView, MakePaymentView, PaymentDetailsView
from pesa.views import payment_history, cashout_list, cash_out_request, payments_list, transfer, TransactionsListView, PaymentDetailsView, AccountsListView, make_payment
# PaymentHistoryView, , PaymentsListView

urlpatterns = [
    path('cashout/', views.cash_out_request, name='cash_out_request'),
    path('cashoutlist/', views.cashout_list, name='cashoutlist'),  
    path('transactions/', TransactionsListView.as_view(), name='transactions_list'),  # List all Transactions
    # path('', PaymentsListView.as_view(), name='payments_list'),  # List all Payments
    path('transfer', views.transfer, name='accounts_transfer'),  # Transfter money from account to another
    path('contributions/<str:case_number>/', views.payments_list, name='payments_list'),  # List all Payments
    path('accounts/', AccountsListView.as_view(), name='accounts'),  # List all Accounts and balances
    path('pay/', views.make_payment, name='pay'),  # Make Payment
    path('payments/<int:pk>/', PaymentDetailsView.as_view(), name='payment_details'),  # Payment details
    path('member/<int:membership_number>/payments/', views.payment_history, name='payments_history'), # Payment History
    # path('member/<int:member_id>/payments/', PaymentHistoryView.as_view(), name='payments_history'), # Payment History
    # path('pay/<int:pk>/membership_id', MakePaymentView.as_view(), name='pay'),  # Make Payment
    # path('member/<int:pk>/', MemberDetailView.as_view(), name='member_detail'),
    # path('member/<int:pk>/update/', EditMemberDetailView.as_view(), name='edit_member_detail'),
    # path('member/<int:pk>/delete/', DeleteMemberView.as_view(), name='delete_member'),
    # path('registration/', RegisterMemberView.as_view(), name='register_member'),  # Register members
    # ... other URL patterns for your membership app (if any)
]