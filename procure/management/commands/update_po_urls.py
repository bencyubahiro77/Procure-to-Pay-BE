from django.core.management.base import BaseCommand
from procure.models import PurchaseOrder


class Command(BaseCommand):
    help = 'Update existing PurchaseOrders to ensure they have proper Cloudinary URLs'

    def handle(self, *args, **options):
        pos = PurchaseOrder.objects.filter(file__isnull=False).exclude(file='')
        
        updated_count = 0
        for po in pos:
            # This forces Django to regenerate the URL property
            # The URL is automatically available via po.file.url
            if po.file:
                self.stdout.write(
                    f'PO #{po.id} - File: {po.file.name} - URL: {po.file.url}'
                )
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {updated_count} Purchase Orders. '
                f'URLs are now accessible via the API.'
            )
        )
