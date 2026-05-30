# core/constants.py

from django.db import models

class Priority(models.TextChoices):
    HIGH = 'HIGH', 'High'
    MEDIUM = 'MEDIUM', 'Medium'
    LOW = 'LOW', 'Low'

class BatchType(models.TextChoices):
    GOVERNANCE = 'GOVERNANCE', 'Governance'
    SAFETY_EMERGENCY = 'SAFETY_EMERGENCY', 'Safety & Emergency'
    HUMAN_RESOURCE = 'HUMAN_RESOURCE', 'Human Resource'
    EQUIPMENT_REAGENT = 'EQUIPMENT_REAGENT', 'Equipment & Reagent'
    RECORDING_REPORTING = 'RECORDING_REPORTING', 'Recording & Reporting'
    QUALITY_ASSURANCE = 'QUALITY_ASSURANCE', 'Quality Assurance'
    BIOSAFETY_WASTE = 'BIOSAFETY_WASTE', 'Biosafety & Waste'
    PATIENT_RIGHTS_ACCESS = 'PATIENT_RIGHTS_ACCESS', 'Patient Rights & Access'
    MIXED = 'MIXED', 'Mixed'

class DocumentKind(models.TextChoices):
    SOP = 'SOP', 'SOP'
    POLICY = 'POLICY', 'Policy'
    PROTOCOL = 'PROTOCOL', 'Protocol'
    REGISTER = 'REGISTER', 'Register'
    LOGBOOK = 'LOGBOOK', 'Logbook'
    FORM = 'FORM', 'Form'
    CHECKLIST = 'CHECKLIST', 'Checklist'
    DISPLAY_NOTICE = 'DISPLAY_NOTICE', 'Display Notice'
    APPOINTMENT_ORDER = 'APPOINTMENT_ORDER', 'Appointment Order'
    AUTHORIZATION_LETTER = 'AUTHORIZATION_LETTER', 'Authorization Letter'
    MOU = 'MOU', 'MOU'
    CERTIFICATE_LICENSE = 'CERTIFICATE_LICENSE', 'Certificate / License'
    REPORT = 'REPORT', 'Report'
    AUDIT = 'AUDIT', 'Audit'
    LIST_ROSTER = 'LIST_ROSTER', 'List / Roster'
    PHYSICAL_PROOF = 'PHYSICAL_PROOF', 'Physical Proof'
    PHOTO_PROOF = 'PHOTO_PROOF', 'Photo Proof'
    TRAINING_RECORD = 'TRAINING_RECORD', 'Training Record'
    DIGITAL_SCREENSHOT = 'DIGITAL_SCREENSHOT', 'Digital Screenshot'
    OTHER = 'OTHER', 'Other'

class GenerationStatus(models.TextChoices):
    PLANNED = 'PLANNED', 'Planned'
    DRAFT_NEEDED = 'DRAFT_NEEDED', 'Draft Needed'
    DRAFTED = 'DRAFTED', 'Drafted'
    APPROVED = 'APPROVED', 'Approved'
    UPLOADED = 'UPLOADED', 'Uploaded'
    NOT_APPLICABLE = 'NOT_APPLICABLE', 'Not Applicable'

class EvidenceNature(models.TextChoices):
    ONE_TIME = 'ONE_TIME', 'One-time'
    RECURRING = 'RECURRING', 'Recurring'
    AS_NEEDED = 'AS_NEEDED', 'As Needed'

class PrimaryEvidenceType(models.TextChoices):
    SOP_POLICY = 'SOP_POLICY', 'SOP / Policy'
    FORM_TEMPLATE = 'FORM_TEMPLATE', 'Form / Template'
    REGISTER_LOGBOOK = 'REGISTER_LOGBOOK', 'Register / Logbook'
    DISPLAY_NOTICE = 'DISPLAY_NOTICE', 'Display Notice'
    APPOINTMENT_ORDER = 'APPOINTMENT_ORDER', 'Appointment Order'
    AUTHORIZATION_LETTER = 'AUTHORIZATION_LETTER', 'Authorization Letter'
    TRAINING_RECORD = 'TRAINING_RECORD', 'Training Record'
    PHYSICAL_PROOF = 'PHYSICAL_PROOF', 'Physical Proof'
    PHOTO_EVIDENCE = 'PHOTO_EVIDENCE', 'Photo Evidence'
    LICENSE_CERTIFICATE = 'LICENSE_CERTIFICATE', 'License / Certificate'
    MOU_AGREEMENT = 'MOU_AGREEMENT', 'MOU / Agreement'
    LIST_ROSTER = 'LIST_ROSTER', 'List / Roster'
    REPORT_AUDIT = 'REPORT_AUDIT', 'Report / Audit'
    DIGITAL_SYSTEM = 'DIGITAL_SYSTEM', 'Digital System'
    OTHER = 'OTHER', 'Other'

class RecurrenceFrequency(models.TextChoices):
    NONE = 'NONE', 'None'
    DAILY = 'DAILY', 'Daily'
    WEEKLY = 'WEEKLY', 'Weekly'
    MONTHLY = 'MONTHLY', 'Monthly'
    QUARTERLY = 'QUARTERLY', 'Quarterly'
    BIANNUAL = 'BIANNUAL', 'Biannual'
    ANNUAL = 'ANNUAL', 'Annual'
    AS_NEEDED = 'AS_NEEDED', 'As Needed'
    
class ProfileConfidence(models.TextChoices):
    HIGH = 'HIGH', 'High'
    MEDIUM = 'MEDIUM', 'Medium'
    LOW = 'LOW', 'Low'

class ProfileSource(models.TextChoices):
    SEEDED_FROM_RULES = 'SEEDED_FROM_RULES', 'Seeded from Rules'
    AI_ASSISTED = 'AI_ASSISTED', 'AI Assisted'
    MANUAL_REVIEWED = 'MANUAL_REVIEWED', 'Manual Reviewed'
    IMPORTED = 'IMPORTED', 'Imported'
    

class EvidenceType(models.TextChoices):
    CONTROLLED_DOCUMENT = 'CONTROLLED_DOCUMENT', 'Controlled Document'
    DISPLAY_NOTICE = 'DISPLAY_NOTICE', 'Display Notice'
    PHYSICAL_FACILITY = 'PHYSICAL_FACILITY', 'Physical Facility'
    LICENSE_CERTIFICATE = 'LICENSE_CERTIFICATE', 'License/Certificate'
    CONTRACT_MOU = 'CONTRACT_MOU', 'Contract/MOU'
    HR_DOCUMENT = 'HR_DOCUMENT', 'HR Document'
    HR_RECORD = 'HR_RECORD', 'HR Record'
    TRAINING_RECORD = 'TRAINING_RECORD', 'Training Record'
    REGISTER_LOGBOOK = 'REGISTER_LOGBOOK', 'Register/Logbook'
    LIMS_SYSTEM_RECORD = 'LIMS_SYSTEM_RECORD', 'LIMS System Record'
    AUDIT_QA_REPORT = 'AUDIT_QA_REPORT', 'Audit/QA Report'
    INVENTORY_STOCK = 'INVENTORY_STOCK', 'Inventory/Stock'
    PHOTO_EVIDENCE = 'PHOTO_EVIDENCE', 'Photo Evidence'
    SYSTEM_SCREENSHOT = 'SYSTEM_SCREENSHOT', 'System Screenshot'
    MIXED_EVIDENCE = 'MIXED_EVIDENCE', 'Mixed Evidence'
    OTHER = 'OTHER', 'Other'

class DocumentType(models.TextChoices):
    SOP = 'SOP', 'SOP'
    POLICY = 'POLICY', 'Policy'
    PROTOCOL = 'PROTOCOL', 'Protocol'
    MISSION_STATEMENT = 'MISSION_STATEMENT', 'Mission Statement'
    ORGANOGRAM = 'ORGANOGRAM', 'Organogram'
    APPOINTMENT_ORDER = 'APPOINTMENT_ORDER', 'Appointment Order'
    AUTHORIZATION_LETTER = 'AUTHORIZATION_LETTER', 'Authorization Letter'
    JOB_DESCRIPTION = 'JOB_DESCRIPTION', 'Job Description'
    ELIGIBILITY_CRITERIA = 'ELIGIBILITY_CRITERIA', 'Eligibility Criteria'
    CHECKLIST = 'CHECKLIST', 'Checklist'
    REGISTER = 'REGISTER', 'Register'
    LOGBOOK = 'LOGBOOK', 'Logbook'
    INVENTORY = 'INVENTORY', 'Inventory'
    AUDIT_REPORT = 'AUDIT_REPORT', 'Audit Report'
    MONITORING_REPORT = 'MONITORING_REPORT', 'Monitoring Report'
    TRAINING_ATTENDANCE = 'TRAINING_ATTENDANCE', 'Training Attendance'
    DISPLAY_NOTICE = 'DISPLAY_NOTICE', 'Display Notice'
    CERTIFICATE = 'CERTIFICATE', 'Certificate'
    LICENSE = 'LICENSE', 'License'
    MOU = 'MOU', 'MOU'
    CONTRACT = 'CONTRACT', 'Contract'
    PHOTO_EVIDENCE = 'PHOTO_EVIDENCE', 'Photo Evidence'
    SYSTEM_SCREENSHOT = 'SYSTEM_SCREENSHOT', 'System Screenshot'
    DECLARATION = 'DECLARATION', 'Declaration'
    OTHER = 'OTHER', 'Other'

class AIGenerationMode(models.TextChoices):
    AI_DRAFTABLE = 'AI_DRAFTABLE', 'AI Draftable'
    AI_TEMPLATE_ONLY = 'AI_TEMPLATE_ONLY', 'AI Template Only'
    AI_ASSISTED_REVIEW = 'AI_ASSISTED_REVIEW', 'AI Assisted Review'
    HUMAN_UPLOAD_REQUIRED = 'HUMAN_UPLOAD_REQUIRED', 'Human Upload Required'
    PHYSICAL_IMPLEMENTATION_REQUIRED = 'PHYSICAL_IMPLEMENTATION_REQUIRED', 'Physical Implementation Required'
    HUMAN_APPROVAL_REQUIRED = 'HUMAN_APPROVAL_REQUIRED', 'Human Approval Required'
    NO_AI_NEEDED = 'NO_AI_NEEDED', 'No AI Needed'

class RecurrenceMode(models.TextChoices):
    STATIC_ONCE = 'STATIC_ONCE', 'Static (Once)'
    SCHEDULED_RECURRING = 'SCHEDULED_RECURRING', 'Scheduled Recurring'
    EVENT_DRIVEN = 'EVENT_DRIVEN', 'Event Driven'
    PER_PATIENT = 'PER_PATIENT', 'Per Patient'
    PER_TEST = 'PER_TEST', 'Per Test'
    PER_EQUIPMENT = 'PER_EQUIPMENT', 'Per Equipment'
    PER_EMPLOYEE = 'PER_EMPLOYEE', 'Per Employee'
    PER_STOCK_ENTRY = 'PER_STOCK_ENTRY', 'Per Stock Entry'
    NONE = 'NONE', 'None'

class ApprovalStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING_REVIEW = 'PENDING_REVIEW', 'Pending Review'
    APPROVED = 'APPROVED', 'Approved'
    DISPLAYED = 'DISPLAYED', 'Displayed'
    IMPLEMENTED = 'IMPLEMENTED', 'Implemented'
    EXPIRED = 'EXPIRED', 'Expired'
    ARCHIVED = 'ARCHIVED', 'Archived'
    REJECTED = 'REJECTED', 'Rejected'

class SourceType(models.TextChoices):
    UPLOADED_FILE = 'UPLOADED_FILE', 'Uploaded File'
    EXTERNAL_URL = 'EXTERNAL_URL', 'External URL'
    PHYSICAL_FILE = 'PHYSICAL_FILE', 'Physical File'
    REGISTER_ENTRY = 'REGISTER_ENTRY', 'Register Entry'
    SYSTEM_RECORD = 'SYSTEM_RECORD', 'System Record'
    PHOTO = 'PHOTO', 'Photo'
    SCREENSHOT = 'SCREENSHOT', 'Screenshot'

class GeneratedDocumentStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    NEEDS_REVIEW = 'NEEDS_REVIEW', 'Needs Review'
    APPROVED_FOR_PRINT = 'APPROVED_FOR_PRINT', 'Approved for Print'
    SIGNED_UPLOADED = 'SIGNED_UPLOADED', 'Signed & Uploaded'
    ARCHIVED = 'ARCHIVED', 'Archived'

class DOCXStatus(models.TextChoices):
    NOT_GENERATED = 'NOT_GENERATED', 'Not Generated'
    GENERATED_WAITING_APPROVAL = 'GENERATED_WAITING_APPROVAL', 'Generated, Waiting for Approval'
    SIGNED_UPLOADED = 'SIGNED_UPLOADED', 'Signed & Uploaded'
    NEEDS_REGENERATION = 'NEEDS_REGENERATION', 'Needs Regeneration'

class FulfillmentStatus(models.TextChoices):
    MISSING = 'MISSING', 'Missing'
    DRAFT = 'DRAFT', 'Draft'
    PENDING_REVIEW = 'PENDING_REVIEW', 'Pending Review'
    PARTIAL = 'PARTIAL', 'Partial'
    READY = 'READY', 'Ready'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'
    EXPIRED = 'EXPIRED', 'Expired'
    NOT_APPLICABLE = 'NOT_APPLICABLE', 'Not Applicable'
    PLANNED = 'PLANNED', 'Planned'
    OVERDUE = 'OVERDUE', 'Overdue'
