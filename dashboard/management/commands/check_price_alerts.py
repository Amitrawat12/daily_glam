from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from dashboard.models import PriceAlert
from django.db.models import Min

class Command(BaseCommand):
    help = 'Checks for price drops and sends email notifications to users.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Checking for price drops...')

        active_alerts = PriceAlert.objects.filter(is_active=True).select_related('user', 'product')
        alerts_to_deactivate = []

        for alert in active_alerts:
            # Get the current lowest price directly from the product's offers
            lowest_price = alert.product.offers.aggregate(min_price=Min('price'))['min_price']

            # Check if a price exists and if it meets the user's desired price
            if lowest_price is not None and lowest_price <= alert.desired_price:
                self.stdout.write(self.style.SUCCESS(
                    f"Price drop for {alert.product.name} for {alert.user.username}! "
                    f"(Desired: {alert.desired_price}, Current: {lowest_price})"
                ))

                # Send email notification
                send_mail(
                    'Price Alert! Your product is now available at a lower price!',
                    f"Hi {alert.user.username},\n\nThe price for {alert.product.name} has dropped to ₹{lowest_price}!",
                    settings.DEFAULT_FROM_EMAIL,
                    [alert.user.email],
                    fail_silently=False,
                )

                # Mark the alert for deactivation
                alerts_to_deactivate.append(alert.pk)

        # Bulk deactivate alerts that have been sent
        if alerts_to_deactivate:
            PriceAlert.objects.filter(pk__in=alerts_to_deactivate).update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f'Sent and deactivated {len(alerts_to_deactivate)} alerts.'))

        self.stdout.write('Price drop check complete.')
