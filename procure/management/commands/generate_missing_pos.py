from django.core.management.base import BaseCommand
from procure.models import PurchaseRequest
from procure.document_processing import generate_po_for_request

class Command(BaseCommand):
    help = 'Generates missing Purchase Orders for approved requests'

    def handle(self, *args, **options):
        # Find approved requests that don't have a related PO
        # Note: We use 'po_obj' related name check. 
        # Django reverse relation filter for OneToOne is 'po_obj__isnull=True'
        missing_pos = PurchaseRequest.objects.filter(
            status=PurchaseRequest.STATUS_APPROVED,
            po_obj__isnull=True
        )
        
        count = missing_pos.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No approved requests found missing POs.'))
            return

        self.stdout.write(f'Found {count} approved requests missing POs. Generating...')

        for pr in missing_pos:
            try:
                # We pass the last approver as the generator if available, else None
                generator = pr.last_approved_by
                generate_po_for_request(pr, generated_by=generator)
                self.stdout.write(self.style.SUCCESS(f'Generated PO for Request #{pr.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to generate PO for Request #{pr.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Completed.'))
