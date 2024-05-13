from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Payment
import decimal


def check_payment_status(sender, instance, created, **kwargs):
    from .models import Payment
    if created:
        try:
            # Attempt to convert amount to a decimal for validation
            total_paid_for_case = decimal.Decimal(instance.total_paid_for_case)

            # Access the related Case object using the foreign key
            related_case = instance.case_number  # Assuming 'case_number' is the foreign key field

            # Access set_contribution_amount from the retrieved Case object
            case_contribution_amount = related_case.set_contribution_amount

            if total_paid_for_case < 0 or total_paid_for_case == 0:
                instance.status = 'UNPAID'
            elif total_paid_for_case >= case_contribution_amount:
                instance.status = 'PAID'
            else:
                # Existing logic for valid payment amounts
                if total_paid_for_case > 0 and total_paid_for_case < case_contribution_amount:
                    instance.status = 'PARTIALLY_PAID'
                # else:
                #     instance.status = 'PAID'
            instance.save()
        except decimal.InvalidOperation:
            # Handle non-numeric input
            instance.status = 'INVALID'
            instance.save()


# @receiver(post_save, sender=Payment)
# def check_payment_status(sender, instance, created, **kwargs):
#     from .models import Payment
#     if created:
#         try:
#             # Attempt to convert amount to a decimal for validation
#             total_paid_for_case = decimal.Decimal(instance.total_paid_for_case)
#             if total_paid_for_case < 0 or total_paid_for_case == 0:
#                 instance.status = 'UNPAID'
#             elif total_paid_for_case >= case.set_contribution_amount:
#                 instance.status = 'PAID'
#             else:
#                 # Existing logic for valid payment amounts
#                 if total_paid_for_case > 0 and instance.total_paid_for_case < instance.set_contribution_amount:
                
#                     instance.status = 'PARTIALLY_PAID'
#                 # else:
#                 #     instance.status = 'PAID'
#             instance.save()
#         except decimal.InvalidOperation:
#             # Handle non-numeric input
#             instance.status = 'INVALID'
#             instance.save()























        # if instance.total_paid_for_case >= instance.set_contribution_amount:
        #   pass



# def check_payment_status(sender, instance, created, **kwargs):
#     from .models import Payment  # Import Payment inside the function
#     if created and instance.amount >= instance.set_contribution_amount:
#         instance.mark_as_paid()
#         instance.save()

# @receiver(post_save, sender=Payment)
# def check_payment_status(sender, instance, created, **kwargs):
#     from .models import Payment
#     if created:
#         try:
#             # Attempt to convert amount to a decimal for validation
#             payment_amount = decimal.Decimal(instance.amount)
#             if payment_amount < 0 or payment_amount == 0:
#                 instance.status = 'UNPAID'
#                 instance.save()
#             else:
#                 # Existing logic for valid payment amounts
#                 if payment_amount > 0 and payment_amount < instance.set_contribution_amount:
#                     instance.status = 'PARTIALLY_PAID'
#                 else:
#                     instance.status = 'PAID'
#                 instance.save()
#         except decimal.InvalidOperation:
#             # Handle non-numeric input
#             instance.status = 'INVALID'
#             instance.save()
