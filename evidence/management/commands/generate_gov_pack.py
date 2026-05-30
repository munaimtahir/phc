from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Backward compatible alias for generating GOV pack.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not save to database or filesystem.')
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing draft documents.')
        parser.add_argument('--only', type=str, help='Only generate a specific document by code.')

    def handle(self, *args, **kwargs):
        call_args = ['generate_document_pack', '--batch', 'GOV']
        if kwargs['dry_run']:
            call_args.append('--dry-run')
        if kwargs['overwrite']:
            call_args.append('--overwrite')
        if kwargs['only']:
            call_args.extend(['--only', kwargs['only']])
        
        call_command(*call_args)
