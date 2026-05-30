from django.core.management.base import BaseCommand, CommandError
from evidence.models import GeneratedEvidenceDocument
from evidence.services.docx_generator import generate_docx_for_generated_document

class Command(BaseCommand):
    help = 'Generate DOCX versions for generated evidence documents.'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Process all generated documents.')
        parser.add_argument('--batch', type=str, help='Process a specific batch code.')
        parser.add_argument('--only', type=str, help='Process a specific document ID or code.')
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing DOCX files.')
        parser.add_argument('--dry-run', action='store_true', help='Log actions without generating files.')

    def handle(self, *args, **kwargs):
        docs = GeneratedEvidenceDocument.objects.all()

        if kwargs['batch']:
            docs = docs.filter(batch__code=kwargs['batch'])
        elif kwargs['only']:
            if kwargs['only'].isdigit():
                docs = docs.filter(id=kwargs['only'])
            else:
                docs = docs.filter(document_code=kwargs['only'])
        elif not kwargs['all']:
            raise CommandError("Specify --all, --batch, or --only.")

        total = docs.count()
        self.stdout.write(f"Found {total} documents to process.")

        stats = {
            'generated': 0,
            'skipped': 0,
            'failed': 0,
        }

        for doc in docs:
            if not doc.content_markdown:
                self.stdout.write(self.style.WARNING(f"Skipping {doc.document_code}: No content."))
                stats['failed'] += 1
                continue

            if doc.docx_file and not kwargs['overwrite']:
                self.stdout.write(f"Skipping {doc.document_code}: Already exists.")
                stats['skipped'] += 1
                continue

            if kwargs['dry_run']:
                self.stdout.write(f"[Dry-run] Would generate DOCX for {doc.document_code}")
                continue

            try:
                generate_docx_for_generated_document(doc, overwrite=kwargs['overwrite'])
                self.stdout.write(self.style.SUCCESS(f"Generated DOCX for {doc.document_code}"))
                stats['generated'] += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed {doc.document_code}: {str(e)}"))
                stats['failed'] += 1

        self.stdout.write(self.style.SUCCESS(f"Summary: Generated: {stats['generated']}, Skipped: {stats['skipped']}, Failed: {stats['failed']}"))
