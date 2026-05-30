from django.core.management.base import BaseCommand
from django.db.models import Count
from indicators.models import Indicator
from evidence.models import DocumentBatch, PlannedEvidenceDocument

class Command(BaseCommand):
    help = 'Audit document batch coverage for all 118 indicators.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Document Batch Coverage Audit ---'))

        total_indicators = Indicator.objects.count()
        covered_indicators = Indicator.objects.filter(planned_documents__isnull=False).distinct().count()
        
        self.stdout.write(f"Total Indicators: {total_indicators}")
        self.stdout.write(f"Indicators covered by at least one Planned Document: {covered_indicators}")
        
        if covered_indicators < total_indicators:
            self.stdout.write(self.style.WARNING(f"MISSING COVERAGE: {total_indicators - covered_indicators} indicators have no planned document."))
            missing = Indicator.objects.filter(planned_documents__isnull=True).order_by('indicator_no')
            for m in missing:
                self.stdout.write(f"  - {m.indicator_no}: {m.indicator_text[:50]}...")
        else:
            self.stdout.write(self.style.SUCCESS("FULL COVERAGE: All indicators are mapped to at least one planned document."))

        self.stdout.write("\n--- Batch Summary ---")
        batches = DocumentBatch.objects.all().order_by('sequence_order')
        for b in batches:
            doc_count = b.planned_documents.count()
            ind_count = Indicator.objects.filter(planned_documents__batch=b).distinct().count()
            self.stdout.write(f"{b.code}: {doc_count} docs, covering {ind_count} indicators")

        self.stdout.write("\n--- Multi-Indicator Documents ---")
        multi_docs = PlannedEvidenceDocument.objects.annotate(ind_count=Count('indicators')).filter(ind_count__gt=1).order_by('-ind_count')
        for md in multi_docs:
            self.stdout.write(f"{md.code}: satisfies {md.ind_count} indicators")

        self.stdout.write(self.style.SUCCESS('\n--- Audit Complete ---'))
