from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Tries to import models from all apps to diagnose discovery issues.'

    def handle(self, *args, **options):
        self.stdout.write("Starting model import check...")

        try:
            from compare.models import SavedComparison
            self.stdout.write(self.style.SUCCESS("  Successfully imported 'compare' models."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED to import from 'compare': {e}"))

        try:
            from kit.models import Kit
            self.stdout.write(self.style.SUCCESS("  Successfully imported 'kit' models."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED to import from 'kit': {e}"))

        try:
            from advice.models import SavedAdvice
            self.stdout.write(self.style.SUCCESS("  Successfully imported 'advice' models."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED to import from 'advice': {e}"))

        self.stdout.write("\nDiagnostic check complete.")
