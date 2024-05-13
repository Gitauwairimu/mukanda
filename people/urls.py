

from django.urls import path
from people.views import (
    dashboard,
    create_case,
    create_rule,
    propose_rule,
    approve_proposal,
    edit_proposal,
    discard_proposal,
    active_members_list,
    list_rules,
    edit_rule,
    delete_rule,
    rule_detail,
    CaseListView,
    case_contribution_report,
    AddDependentView,
    RegisterMemberView,
    register_member,
    AllMemberListView,
    MemberDetailView,
    EditMemberDetailView,
    DeleteMemberView,
)

from . import views
from django.contrib.auth import views as auth_views
# from membership.views import create_case, create_rule, active_members_list, list_rules, edit_rule, delete_rule,
# rule_detail, CaseListView, AddDependentView, RegisterMemberView, AllMemberListView, MemberDetailView, EditMemberDetailView, DeleteMemberView

# MemberDetailView, RegisterMemberView, MemberListView  # Import views from the current app (membership)


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'), # Active members' List
    path('allmembers', AllMemberListView.as_view(), name='member_list'),  # List all members
    # path('', ActiveMemberListView.as_view(), name='active_members_list'),  # Active members' List
    path('', views.active_members_list, name='active_members'), # Active members' List
    # path('registration/', views.register_member, name='register_member'), # Register members
    path('member/<int:member_id>/add-dependent/', AddDependentView.as_view(), name='add_dependent'), # Add Dependent
    path('member/<int:pk>/', MemberDetailView.as_view(), name='member_detail'),
    path('member/<int:pk>/update/', EditMemberDetailView.as_view(), name='edit_member_detail'),
    path('member/<int:pk>/delete/', DeleteMemberView.as_view(), name='delete_member'),
    # path('registration/', RegisterMemberView.as_view(), name='register_member'),  # Register members
    path('registration/', views.register_member, name='register_member'),  # Register members
    path('addcase/', views.create_case, name='case_create'),
    # path('member/<int:member_pk>/dependents/<int:dependent_pk>/create-case/', views.create_dependent_case, name='create_dependent_case'),
    # path('members/dependentcase/', views.create_dependent_case, name='create_dependent_case'),
    # path('dependentcase/', views.create_dependent_case, name='create_dependent_case'),
    path('propose/', views.propose_rule, name='propose_rule'), # Add Rule Proposal
    path('approve-proposal/<int:proposal_id>/', views.approve_proposal, name='approve_proposal'), # Approve Proposal
    path('edit-proposal/<int:proposal_id>/', views.edit_proposal, name='edit_proposal'), # Edit Proposal
    path('discard-proposal/<int:proposal_id>/', views.discard_proposal, name='discard_proposal'), # Discard Proposal
    path('addrule/', views.create_rule, name='create_rule'), # Add Rules
    path('rules/', views.list_rules, name='rules'), # View Rules
    path('edit-rule/<int:rule_id>/', views.edit_rule, name='edit_rule'), # Edit Rules
    path('detail-rule/<int:rule_id>/', views.rule_detail, name='rule_detail'), # Rules Detail
    path('delete-rule/<int:rule_id>/', views.delete_rule, name='delete_rule'), # Delete Rules
    path('caselist/', CaseListView.as_view(), name='case_list'),
    path('case-report/<str:case_pk>/', views.case_contribution_report, name='case_contribution_report'),
    path('login/', auth_views.LoginView.as_view(template_name='people/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='people/logout.html'), name='logout'),


    # ... other URL patterns for your membership app (if any)
]