from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('indicators', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EvidenceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('evidence_type', models.CharField(choices=[('CONTROLLED_DOCUMENT', 'Controlled Document'), ('DISPLAY_NOTICE', 'Display Notice'), ('PHYSICAL_FACILITY', 'Physical Facility'), ('LICENSE_CERTIFICATE', 'License/Certificate'), ('CONTRACT_MOU', 'Contract/MOU'), ('HR_DOCUMENT', 'HR Document'), ('HR_RECORD', 'HR Record'), ('TRAINING_RECORD', 'Training Record'), ('REGISTER_LOGBOOK', 'Register/Logbook'), ('LIMS_SYSTEM_RECORD', 'LIMS System Record'), ('AUDIT_QA_REPORT', 'Audit/QA Report'), ('INVENTORY_STOCK', 'Inventory/Stock'), ('PHOTO_EVIDENCE', 'Photo Evidence'), ('SYSTEM_SCREENSHOT', 'System Screenshot'), ('MIXED_EVIDENCE', 'Mixed Evidence'), ('OTHER', 'Other')], default='OTHER', max_length=50)),
                ('document_type', models.CharField(choices=[('SOP', 'SOP'), ('POLICY', 'Policy'), ('PROTOCOL', 'Protocol'), ('MISSION_STATEMENT', 'Mission Statement'), ('ORGANOGRAM', 'Organogram'), ('APPOINTMENT_ORDER', 'Appointment Order'), ('AUTHORIZATION_LETTER', 'Authorization Letter'), ('JOB_DESCRIPTION', 'Job Description'), ('ELIGIBILITY_CRITERIA', 'Eligibility Criteria'), ('CHECKLIST', 'Checklist'), ('REGISTER', 'Register'), ('LOGBOOK', 'Logbook'), ('INVENTORY', 'Inventory'), ('AUDIT_REPORT', 'Audit Report'), ('MONITORING_REPORT', 'Monitoring Report'), ('TRAINING_ATTENDANCE', 'Training Attendance'), ('DISPLAY_NOTICE', 'Display Notice'), ('CERTIFICATE', 'Certificate'), ('LICENSE', 'License'), ('MOU', 'MOU'), ('CONTRACT', 'Contract'), ('PHOTO_EVIDENCE', 'Photo Evidence'), ('SYSTEM_SCREENSHOT', 'System Screenshot'), ('DECLARATION', 'Declaration'), ('OTHER', 'Other')], default='OTHER', max_length=50)),
                ('file', models.FileField(blank=True, null=True, upload_to='evidence_files/')),
                ('external_url', models.URLField(blank=True, max_length=500, null=True)),
                ('physical_file_location', models.CharField(blank=True, max_length=255, null=True)),
                ('display_location', models.CharField(blank=True, max_length=255, null=True)),
                ('evidence_date', models.DateField(blank=True, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('document_code', models.CharField(blank=True, max_length=100, null=True)),
                ('effective_date', models.DateField(blank=True, null=True)),
                ('review_date', models.DateField(blank=True, null=True)),
                ('approval_status', models.CharField(choices=[('DRAFT', 'Draft'), ('PENDING_REVIEW', 'Pending Review'), ('APPROVED', 'Approved'), ('DISPLAYED', 'Displayed'), ('IMPLEMENTED', 'Implemented'), ('EXPIRED', 'Expired'), ('ARCHIVED', 'Archived'), ('REJECTED', 'Rejected')], default='DRAFT', max_length=50)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('source_type', models.CharField(choices=[('UPLOADED_FILE', 'Uploaded File'), ('EXTERNAL_URL', 'External URL'), ('PHYSICAL_FILE', 'Physical File'), ('REGISTER_ENTRY', 'Register Entry'), ('SYSTEM_RECORD', 'System Record'), ('PHOTO', 'Photo'), ('SCREENSHOT', 'Screenshot')], default='UPLOADED_FILE', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_evidence', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EvidenceRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('evidence_type', models.CharField(choices=[('CONTROLLED_DOCUMENT', 'Controlled Document'), ('DISPLAY_NOTICE', 'Display Notice'), ('PHYSICAL_FACILITY', 'Physical Facility'), ('LICENSE_CERTIFICATE', 'License/Certificate'), ('CONTRACT_MOU', 'Contract/MOU'), ('HR_DOCUMENT', 'HR Document'), ('HR_RECORD', 'HR Record'), ('TRAINING_RECORD', 'Training Record'), ('REGISTER_LOGBOOK', 'Register/Logbook'), ('LIMS_SYSTEM_RECORD', 'LIMS System Record'), ('AUDIT_QA_REPORT', 'Audit/QA Report'), ('INVENTORY_STOCK', 'Inventory/Stock'), ('PHOTO_EVIDENCE', 'Photo Evidence'), ('SYSTEM_SCREENSHOT', 'System Screenshot'), ('MIXED_EVIDENCE', 'Mixed Evidence'), ('OTHER', 'Other')], default='OTHER', max_length=50)),
                ('document_type', models.CharField(choices=[('SOP', 'SOP'), ('POLICY', 'Policy'), ('PROTOCOL', 'Protocol'), ('MISSION_STATEMENT', 'Mission Statement'), ('ORGANOGRAM', 'Organogram'), ('APPOINTMENT_ORDER', 'Appointment Order'), ('AUTHORIZATION_LETTER', 'Authorization Letter'), ('JOB_DESCRIPTION', 'Job Description'), ('ELIGIBILITY_CRITERIA', 'Eligibility Criteria'), ('CHECKLIST', 'Checklist'), ('REGISTER', 'Register'), ('LOGBOOK', 'Logbook'), ('INVENTORY', 'Inventory'), ('AUDIT_REPORT', 'Audit Report'), ('MONITORING_REPORT', 'Monitoring Report'), ('TRAINING_ATTENDANCE', 'Training Attendance'), ('DISPLAY_NOTICE', 'Display Notice'), ('CERTIFICATE', 'Certificate'), ('LICENSE', 'License'), ('MOU', 'MOU'), ('CONTRACT', 'Contract'), ('PHOTO_EVIDENCE', 'Photo Evidence'), ('SYSTEM_SCREENSHOT', 'System Screenshot'), ('DECLARATION', 'Declaration'), ('OTHER', 'Other')], default='OTHER', max_length=50)),
                ('ai_generation_mode', models.CharField(choices=[('AI_DRAFTABLE', 'AI Draftable'), ('AI_TEMPLATE_ONLY', 'AI Template Only'), ('AI_ASSISTED_REVIEW', 'AI Assisted Review'), ('HUMAN_UPLOAD_REQUIRED', 'Human Upload Required'), ('PHYSICAL_IMPLEMENTATION_REQUIRED', 'Physical Implementation Required'), ('HUMAN_APPROVAL_REQUIRED', 'Human Approval Required'), ('NO_AI_NEEDED', 'No AI Needed')], default='NO_AI_NEEDED', max_length=50)),
                ('recurrence_mode', models.CharField(choices=[('STATIC_ONCE', 'Static (Once)'), ('SCHEDULED_RECURRING', 'Scheduled Recurring'), ('EVENT_DRIVEN', 'Event Driven'), ('PER_PATIENT', 'Per Patient'), ('PER_TEST', 'Per Test'), ('PER_EQUIPMENT', 'Per Equipment'), ('PER_EMPLOYEE', 'Per Employee'), ('PER_STOCK_ENTRY', 'Per Stock Entry'), ('NONE', 'None')], default='NONE', max_length=50)),
                ('recurrence_frequency', models.CharField(blank=True, max_length=100, null=True)),
                ('minimum_required_count', models.IntegerField(default=1)),
                ('display_required', models.BooleanField(default=False)),
                ('physical_verification_required', models.BooleanField(default=False)),
                ('human_approval_required', models.BooleanField(default=False)),
                ('upload_required', models.BooleanField(default=False)),
                ('template_reusable', models.BooleanField(default=False)),
                ('evidence_reuse_policy', models.CharField(blank=True, max_length=100, null=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence_requirements', to='indicators.indicator')),
            ],
        ),
        migrations.CreateModel(
            name='EvidenceRequirementFulfillment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('MISSING', 'Missing'), ('DRAFT', 'Draft'), ('PENDING_REVIEW', 'Pending Review'), ('PARTIAL', 'Partial'), ('READY', 'Ready'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected'), ('EXPIRED', 'Expired'), ('NOT_APPLICABLE', 'Not Applicable')], default='DRAFT', max_length=50)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evidence_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requirement_fulfillments', to='evidence.evidenceitem')),
                ('evidence_requirement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fulfillments', to='evidence.evidencerequirement')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='evidenceitem',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_evidence', to=settings.AUTH_USER_MODEL),
        ),
    ]
