import os
import datetime
from django.core.management.base import BaseCommand, CommandError
from evidence.models import DocumentBatch, PlannedEvidenceDocument, GeneratedEvidenceDocument
from core.constants import GeneratedDocumentStatus, GenerationStatus

class Command(BaseCommand):
    help = 'Generate draft documents for document batches.'

    def add_arguments(self, parser):
        parser.add_argument('--batch', type=str, help='Generate documents for a specific batch code (e.g. QA, HRM).')
        parser.add_argument('--all', action='store_true', help='Generate documents for all batches.')
        parser.add_argument('--dry-run', action='store_true', help='Do not save to database or filesystem.')
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing draft documents.')
        parser.add_argument('--only', type=str, help='Only generate a specific document by code.')

    def handle(self, *args, **kwargs):
        if not kwargs['batch'] and not kwargs['all'] and not kwargs['only']:
            raise CommandError("Please specify --batch BATCH_CODE, --all, or --only DOC-CODE")

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        batches_to_process = []
        if kwargs['all']:
            batches_to_process = DocumentBatch.objects.filter(active=True)
        elif kwargs['batch']:
            try:
                batches_to_process = [DocumentBatch.objects.get(code=kwargs['batch'])]
            except DocumentBatch.DoesNotExist:
                raise CommandError(f"Batch {kwargs['batch']} not found.")
        elif kwargs['only']:
            # find batch of the single doc
            try:
                doc = PlannedEvidenceDocument.objects.get(code=kwargs['only'])
                batches_to_process = [doc.batch]
            except PlannedEvidenceDocument.DoesNotExist:
                raise CommandError(f"Document {kwargs['only']} not found.")

        total_generated = 0
        
        for batch in batches_to_process:
            self.stdout.write(self.style.SUCCESS(f"\nProcessing batch: {batch.code}"))
            
            planned_docs = PlannedEvidenceDocument.objects.filter(batch=batch)
            if kwargs['only']:
                planned_docs = planned_docs.filter(code=kwargs['only'])

            if not planned_docs.exists():
                self.stdout.write(self.style.WARNING(f"No planned documents found for {batch.code} batch."))
                continue

            output_dir = f'generated_documents/{batch.code}/{timestamp}/'
            if not kwargs['dry_run']:
                os.makedirs(output_dir, exist_ok=True)
            
            index_content = f"# {batch.code} Pack Generation Index - {timestamp}\n\n"
            index_content += "| Doc Code | Title | Status | Link |\n| --- | --- | --- | --- |\n"
            batch_generated_count = 0

            for doc in planned_docs:
                if doc.generation_status == GenerationStatus.DRAFTED and not kwargs['overwrite']:
                    self.stdout.write(f"Skipping {doc.code} (Already drafted). Use --overwrite to regenerate.")
                    continue

                content = self.get_document_content(doc)
                if not content:
                    self.stdout.write(self.style.WARNING(f"No template defined for {doc.code}. skipping."))
                    continue

                # Ensure filename is safe
                safe_title = doc.title.replace(' ', '_').replace('/', '_').replace(':', '')
                file_name = f"{doc.code}_{safe_title}.md"
                file_path = os.path.join(output_dir, file_name)

                if not kwargs['dry_run']:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Create GeneratedEvidenceDocument record
                    gen_doc, created = GeneratedEvidenceDocument.objects.get_or_create(
                        planned_document=doc,
                        batch=batch,
                        defaults={
                            'title': doc.title,
                            'document_code': doc.code,
                            'content_markdown': content,
                            'status': GeneratedDocumentStatus.DRAFT,
                        }
                    )
                    if not created and kwargs['overwrite']:
                        gen_doc.content_markdown = content
                        gen_doc.save()
                    
                    # Update Planned Document status
                    doc.generation_status = GenerationStatus.DRAFTED
                    doc.save()

                self.stdout.write(self.style.SUCCESS(f"Generated: {doc.code} - {doc.title}"))
                batch_generated_count += 1
                index_content += f"| {doc.code} | {doc.title} | DRAFT | [{file_name}]({file_name}) |\n"

            if not kwargs['dry_run'] and batch_generated_count > 0:
                with open(os.path.join(output_dir, 'INDEX.md'), 'w', encoding='utf-8') as f:
                    f.write(index_content)
                    
            total_generated += batch_generated_count
            self.stdout.write(self.style.SUCCESS(f"Batch {batch.code} generation complete. Docs: {batch_generated_count}"))

        self.stdout.write(self.style.SUCCESS(f"\nTotal documents generated across all batches: {total_generated}"))

    def get_document_header(self, title, code):
        return f"""# Laboratory Name: Al Shifa Laboratory
Address: Circular Road, Jaranwala
Document Title: {title}
Document Code: {code}
Version: 1.0
Effective Date: ___________________
Review Date: ___________________
Prepared by: Dr. Muhammad Munaim Tahir, Lab Manager / In-charge
Reviewed/Approved by: Dr. Mubasher Ahmed, Consultant Pathologist

---

"""

    def get_document_footer(self):
        return """
---

### Approval Section

**Prepared by:**
Dr. Muhammad Munaim Tahir
Lab Manager / In-charge
Signature: ___________________
Date: ___________________

**Reviewed and Approved by:**
Dr. Mubasher Ahmed
Consultant Pathologist
Signature: ___________________
Date: ___________________

Effective Date: ___________________
Review Date: ___________________
"""

    def get_document_content(self, doc):
        header = self.get_document_header(doc.title, doc.code)
        footer = self.get_document_footer()
        
        indicators = ", ".join([i.indicator_no for i in doc.indicators.all()])
        context = f"**Related PHC/MSDS Indicator(s):** {indicators}\n\n"
        
        body = ""
        
        # Determine specific template based on batch and title/code
        if doc.batch.code == 'GOV':
            body = self.get_gov_template(doc)
        elif doc.batch.code == 'QA':
            body = self.get_qa_template(doc)
        elif doc.batch.code == 'HRM':
            body = self.get_hrm_template(doc)
        elif doc.batch.code == 'FMS':
            body = self.get_fms_template(doc)
        elif doc.batch.code == 'MER':
            body = self.get_mer_template(doc)
        elif doc.batch.code == 'RRS':
            body = self.get_rrs_template(doc)
        elif doc.batch.code == 'BSBS':
            body = self.get_bsbs_template(doc)
        elif doc.batch.code == 'PATIENT':
            body = self.get_patient_template(doc)
        
        # If it's an AUTO document and no specific template matched, provide a generic one
        if not body and doc.code.startswith('DOC-AUTO'):
            body = self.get_generic_template(doc)
            
        if not body:
            return None # No template defined

        return header + context + body + footer

    def get_gov_template(self, doc):
        if doc.code == 'DOC-GOV-01' or 'Mission Statement' in doc.title:
            return """## 1. Mission Statement
Al Shifa Laboratory is dedicated to providing high-quality, reliable, and timely diagnostic services to the community of Jaranwala and surrounding areas. Our mission is to support clinical decision-making through accurate laboratory testing while ensuring patient safety, confidentiality, and professional ethics.

## 2. Core Values
- **Quality:** Commitment to excellence in every test we perform.
- **Integrity:** Maintaining the highest standards of professional conduct.
- **Patient-Centered Care:** Ensuring a comfortable and respectful experience for all patients.
- **Reliability:** Providing results that clinicians and patients can trust.

## 3. Service Scope
This laboratory provides clinical pathology, hematology, and biochemistry services as licensed by the Punjab Healthcare Commission.

## 4. Display Requirement
This mission statement must be displayed prominently at:
- Reception Desk
- Patient Waiting Area
- Staff Notice Board

## 5. Review
This statement shall be reviewed annually or whenever there is a significant change in the scope of services.
"""
        elif doc.code == 'DOC-GOV-02' or 'Organogram' in doc.title:
            return """## 1. Purpose
To define the organizational structure, reporting lines, and functional hierarchy of Al Shifa Laboratory.

## 2. Organizational Hierarchy
The laboratory operates under the following structure:

| Level | Role | Current Appointee |
| --- | --- | --- |
| 1 | Consultant Pathologist | Dr. Mubasher Ahmed |
| 2 | Lab Manager / In-charge | Dr. Muhammad Munaim Tahir |
| 3 | QA Focal Person | [To be filled] |
| 3 | Biosafety & Waste Focal Person | [To be filled] |
| 4 | Technical Staff (Technologists/Technicians) | [To be filled] |
| 4 | Reception & Data Entry | [To be filled] |
| 4 | Phlebotomy Staff | [To be filled] |
| 5 | Support Staff / Housekeeping | [To be filled] |

## 3. Reporting Lines
- Technical staff report to the Lab Manager.
- Lab Manager reports to the Consultant Pathologist.
- Focal persons coordinate directly with the Lab Manager for operational compliance.

## 4. Simple Visual Chart (ASCII)
```
       [Consultant Pathologist]
                 |
        [Lab Manager / In-charge]
        _________|_________
       |                   |
 [QA Focal Person]  [Biosafety Focal Person]
       |___________________|
                 |
      [Technical & Support Staff]
```

## 5. Display Requirement
The organogram must be available in the management file and displayed in the staff area.
"""
        elif 'Policy and SOP Master Index' in doc.title:
            return """## 1. Policy Statement
Al Shifa Laboratory maintains a standardized system for creating, reviewing, and controlling all Standard Operating Procedures (SOPs) and policies to ensure consistency in laboratory operations.

## 2. Document Control Rules
- All documents must be approved by the Consultant Pathologist.
- Documents are reviewed annually.
- Obsolete documents are removed from workstations and archived.

## 3. Master Index of Policies & SOPs
*Note: This table serves as a placeholder for the actual master file.*

| Document Code | Document Title | Current Version | Location |
| --- | --- | --- | --- |
| SOP-GEN-01 | Mission Statement | 1.0 | Reception/Staff Area |
| SOP-GEN-02 | Organogram | 1.0 | Management File |
| SOP-SAF-01 | Emergency Policy | 1.0 | Laboratory Entrance |
| ... | [To be expanded] | ... | ... |

## 4. Staff Awareness
All staff members are required to read and sign the "Staff SOP Acknowledgment Record" for all procedures relevant to their roles.
"""
        elif 'Emergency Policy' in doc.title:
            return """## 1. Purpose
To ensure the safety of patients, staff, and visitors during various laboratory emergencies.

## 2. Emergency Types
The laboratory identifies and prepares for the following:
- **Fire Emergency:** Response to smoke or flames.
- **Electrical Failure:** Safe shutdown of equipment and backup power use.
- **Chemical/Biological Spill:** Immediate containment and cleaning protocols.
- **Accident / Injury:** First aid and referral procedures.
- **Security / Violence:** Handling disruptive behavior.

## 3. General Response Protocol
1. **Safety First:** Evacuate patients and visitors if necessary.
2. **Alert:** Inform the Lab Manager immediately.
3. **Contact:** Use the "Emergency Contact List" for Fire Brigade, Ambulance, or Police.
4. **Action:** Use available safety equipment (Fire Extinguishers) only if safe to do so.

## 4. Staff Responsibility
All staff must be familiar with the location of emergency exits and fire extinguishers. Mock drills are conducted annually.

## 5. Display
This policy summary and the emergency contact list must be displayed near the laboratory entrance.
"""
        elif 'Section Head Appointment' in doc.title:
            return """## 1. Appointment Authority
Under the authority of the Management of Al Shifa Laboratory, the following internal appointment is made to ensure compliance with PHC MSDS standards.

## 2. Appointment Details
**Appointee Name:** [To be filled]
**Designation:** [Technologist / Technician / Staff Name]
**Appointed Role:** [e.g., QA Focal Person / Biosafety Focal Person / Section Head]
**Section/Area:** [To be filled]
**Effective Date:** [To be filled]

## 3. Responsibilities
- Monitor compliance within the assigned area.
- Maintain required registers and logs.
- Report any non-conformities to the Lab Manager.
- Assist in staff training for the assigned functional area.

## 4. Reporting Line
The appointee shall report to the Lab Manager for all matters related to this role.
"""
        elif 'Budget' in doc.title:
            return """## 1. Declaration
The management of Al Shifa Laboratory hereby declares that adequate financial and physical resources are allocated to maintain laboratory operations in accordance with quality and safety standards.

## 2. Resource Allocation Areas
- **Human Resources:** Qualified staff for all technical and support roles.
- **Equipment:** Procurement and maintenance of required diagnostic machines.
- **Reagents & Consumables:** Continuous supply of quality reagents.
- **Facility:** Maintenance of space, utilities, and safety infrastructure.
- **Quality Control:** Participation in EQA and provision of IQA materials.

## 3. Review
The budget and resource requirements are reviewed biannually by the Lab Manager and Consultant Pathologist to ensure no disruption in services.
"""
        elif 'Research' in doc.title:
            return """## 1. Policy Scope
Al Shifa Laboratory primarily functions as a clinical diagnostic facility. This policy defines the approach toward research and data sharing.

## 2. Data Sharing Protocol
- The laboratory may share anonymized, aggregated data regarding notifiable diseases or public health trends with authorized health authorities (e.g., PHC, Health Department).
- Patient confidentiality is strictly maintained; no personally identifiable information (PII) is shared without explicit consent.

## 3. Formal Research
If any formal research project is to be conducted using laboratory data:
- Prior ethical approval must be obtained.
- Explicit informed consent must be taken from patients if required.
- The project must be reviewed and approved by the Consultant Pathologist.

## 4. Declaration of Non-Conduct
Currently, Al Shifa Laboratory does not conduct active clinical trials or experimental research on human subjects.
"""
        elif 'Referral' in doc.title:
            return """## MEMORANDUM OF UNDERSTANDING (Referral Services)

**Between:**
**Al Shifa Laboratory** (Circular Road, Jaranwala) - *The Referring Lab*

**And:**
**[Name of Partner Laboratory]** - *The Referral Lab*

## 1. Purpose
To define the arrangement for specialized tests not performed at Al Shifa Laboratory.

## 2. Responsibilities
- **Referring Lab:** Proper sample collection, labeling, and transport under cold chain.
- **Referral Lab:** Timely testing, providing accurate reports, and maintaining quality standards.

## 3. Quality Assurance
The Referral Lab must be licensed by the PHC and preferably hold ISO 15189 accreditation or participate in valid EQA schemes.

## 4. Confidentiality
Both parties agree to maintain the strict confidentiality of all patient data shared during this process.

## 5. Duration
This MOU is valid for [1 Year / 2 Years] from the date of signing and can be renewed by mutual consent.

## 6. Signatures

For Al Shifa Laboratory: ___________________  Date: __________
For [Partner Lab]: ___________________  Date: __________
"""
        elif 'PHC Registration' in doc.title:
            return """## 1. PHC Compliance File Index
This file contains all documents related to the registration and licensing of Al Shifa Laboratory with the Punjab Healthcare Commission.

## 2. Required Documents Checklist
| S.No | Document Description | Status (Available/NA) |
| --- | --- | --- |
| 1 | PHC Registration Certificate | |
| 2 | PHC License / Provisional License | |
| 3 | Evidence of Application (if under process) | |
| 4 | List of Associated Collection Centers | |
| 5 | PMDC/PMC Registration of Consultant Pathologist | |
| 6 | PHC Inspection Reports (Latest) | |
| 7 | Corrective Action Reports (if any) | |

## 3. Display Requirement
The PHC Registration/License must be displayed at the main reception desk.
"""
        elif 'Lab Head Qualification' in doc.title:
            return """## 1. Management Qualification File
This file contains the credentials and appointment details of the Laboratory Head / Consultant Pathologist.

## 2. Credentials Checklist
| Document Type | Verification Status |
| --- | --- |
| MBBS Degree | |
| Post-Graduate Degree (e.g., M.Phil / FCPS Pathology) | |
| PMDC / PMC Registration Certificate (Valid) | |
| Appointment Order as Lab Head | |
| Job Description | |
| Annual Performance Review | |

## 3. Responsibility
The Lab Manager is responsible for ensuring these documents are updated annually upon the renewal of registrations.
"""
        return None

    def get_qa_template(self, doc):
        if doc.code == 'DOC-QA-01' or 'QA SOP' in doc.title:
            return """## 1. Purpose
To define the Quality Assurance (QA) program for Al Shifa Laboratory, covering both Internal Quality Assurance (IQA) and External Quality Assurance (EQA).

## 2. Scope
Applies to all analytical processes within the laboratory.

## 3. Internal Quality Assurance (IQA)
- Control samples shall be run daily or with each batch of tests as appropriate.
- IQA results must be documented in the IQA Control Record.
- Any out-of-range results require immediate corrective action before patient testing resumes.
- The QA Focal Person will review IQA records weekly.

## 4. External Quality Assurance (EQA)
- The laboratory participates in recognized EQA schemes for core parameters.
- EQA samples are processed blindly like normal patient samples.
- EQA reports are reviewed by the Consultant Pathologist.
- Poor EQA performance requires documented root cause analysis and corrective action.

## 5. Staff Awareness
All technical staff must be trained on this SOP and sign the awareness log.
"""
        elif doc.code == 'DOC-QA-02' or 'EQA Participation' in doc.title:
            return """## 1. Purpose
To maintain a record of participation in External Quality Assurance schemes.

## 2. EQA Scheme Details
**Provider Name:** [To be filled]
**Scheme Code:** [To be filled]
**Parameters Covered:** [To be filled]

## 3. Participation Log
| Date | Cycle / Batch | Sample Received | Result Submitted | Report Received | QA Focal Sign |
| --- | --- | --- | --- | --- | --- |
| [Date] | [Cycle] | [Yes/No] | [Yes/No] | [Yes/No] | |
| [Date] | [Cycle] | [Yes/No] | [Yes/No] | [Yes/No] | |

## 4. Review
The Consultant Pathologist must review and sign off on all received EQA reports.
"""
        elif 'IQA Control Record' in doc.title or 'Control' in doc.title:
            return """## 1. Purpose
Daily log for Internal Quality Control runs.

## 2. Log Format
**Instrument / Parameter:** [To be filled]
**Control Lot No:** [To be filled]   **Expiry Date:** [Date]

| Date | Time | Run By | Control Level (L1/L2) | Result | In Range? (Y/N) | Corrective Action (if N) | Sign |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Date] | [Time] | [Name] | [Level] | [Value] | [Y/N] | [Action] | |
| [Date] | [Time] | [Name] | [Level] | [Value] | [Y/N] | [Action] | |

## 3. Review
Lab Manager / QA Focal Person reviews this log weekly.
"""
        elif 'Process Cycle' in doc.title:
            return """## 1. Purpose
To document and monitor the complete analytical process cycle from sample collection to report dispatch.

## 2. Process Cycle Components
- **Pre-analytical:** Patient prep, sample collection, labeling, transport, accessioning.
- **Analytical:** Processing, testing, IQA, result verification.
- **Post-analytical:** Reporting, validation, dispatch, critical result notification.

## 3. Monitoring Log
| Date | Parameter Monitored | Findings/Deviations | Corrective Action | Sign |
| --- | --- | --- | --- | --- |
| [Date] | [e.g. Sample Rejection Rate] | [Details] | [Action] | |
| [Date] | [e.g. TAT Compliance] | [Details] | [Action] | |

## 4. Responsibility
QA Focal Person is responsible for maintaining and analyzing process cycle records.
"""
        elif 'Corrective Action' in doc.title or 'Gap Analysis' in doc.title or 'Recurrence' in doc.title:
            return """## 1. Corrective and Preventive Action (CAPA) Log
To document errors, deviations, or gaps identified in audits/EQA and the actions taken to resolve them.

## 2. CAPA Register
| Date | Identification Source | Description of Gap / Error | Root Cause | Corrective Action Taken | Preventive Action (to avoid recurrence) | Status (Open/Closed) | Sign |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Date] | [e.g. Internal Audit] | [Details] | [Analysis] | [Immediate fix] | [Long term fix] | [Status] | |

## 3. Review
The Consultant Pathologist reviews open CAPAs monthly.
"""
        return None

    def get_hrm_template(self, doc):
        if 'Job Description' in doc.title:
            return """## 1. Job Description Template

**Designation:** [To be filled]
**Department:** [To be filled]
**Reporting to:** [To be filled]

## 2. Primary Responsibilities
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]
- Adhere strictly to laboratory safety, quality, and PHC guidelines.

## 3. Qualifications Required
- [Degree/Diploma]
- [Registration if applicable]
- [Experience required]

## 4. Acknowledgment
I have read and understood my job responsibilities.

**Employee Name:** [To be filled]
**Signature:** ___________________ **Date:** ___________________
"""
        elif 'Eligibility Criteria' in doc.title or 'Recruitment' in doc.title:
            return """## 1. Recruitment Policy & Eligibility Criteria
Al Shifa Laboratory ensures all staff are qualified for their respective roles.

## 2. Standard Eligibility Criteria
| Designation | Minimum Qualification | Required Registration | Experience |
| --- | --- | --- | --- |
| Consultant Pathologist | MBBS, FCPS/M.Phil | PMDC / PMC | As per PMDC rules |
| Lab Manager | MBBS / Ph.D / M.Sc | PMDC (if applicable) | [Years] |
| Technologist | BS MLT / equivalent | Allied Health Council | [Years] |
| Technician | F.Sc MLT / Diploma | Allied Health Council | [Years] |
| Phlebotomist | Nursing/Lab Diploma | - | [Years] |

## 3. Recruitment Process
- Vacancies are advertised or sourced through known networks.
- Interviews evaluate technical competence and attitude.
- Original credentials must be verified before the final appointment.
"""
        elif 'Orientation' in doc.title:
            return """## 1. Staff Orientation Plan
All new employees must undergo an orientation program before assuming independent duties.

## 2. Orientation Checklist
| Topic | Completed Date | Trainer Sign | Employee Sign |
| --- | --- | --- | --- |
| Facility Layout & Emergency Exits | | | |
| Job Description Review | | | |
| Biosafety & Infection Control | | | |
| Waste Management Protocols | | | |
| Patient Rights & Confidentiality | | | |
| Incident Reporting | | | |

## 3. Records
This checklist must be maintained in the employee's personal file.
"""
        elif 'Rights' in doc.title:
            return """## 1. Staff Rights and Responsibilities
## Staff Rights
- Safe and healthy working environment.
- Fair treatment without discrimination.
- Access to required protective equipment (PPE).
- Clear job descriptions and performance expectations.

## Staff Responsibilities
- Comply with all laboratory SOPs and safety rules.
- Maintain patient confidentiality at all times.
- Treat patients and colleagues with respect.
- Participate in required training and quality assurance activities.

## 2. Acknowledgment
Staff must acknowledge receipt of this document during orientation.
"""
        elif 'Appraisal' in doc.title:
            return """## 1. Performance Appraisal Form
**Employee Name:** [To be filled]
**Designation:** [To be filled]
**Review Period:** [Date] to [Date]

## 2. Evaluation Criteria (Rate 1 to 5)
1. **Technical Competence:** [Score]
2. **Adherence to SOPs:** [Score]
3. **Punctuality & Attendance:** [Score]
4. **Behavior with Patients/Colleagues:** [Score]
5. **Participation in QA/Safety:** [Score]

## 3. Comments & Development
**Strengths:** [To be filled]
**Areas for Improvement / Training Needed:** [To be filled]

**Appraiser Name:** [To be filled]
**Signature:** ___________________
"""
        elif 'Personal File' in doc.title:
            return """## 1. Personal File Checklist
Every employee must have a standardized personal file.

## 2. Required Documents
- [ ] Resume / CV
- [ ] CNIC Copy
- [ ] Offer / Appointment Letter
- [ ] Signed Job Description
- [ ] Verified Academic Degrees
- [ ] Professional Council Registration (if applicable)
- [ ] Orientation Checklist
- [ ] Vaccination Record (Hep B, etc.)
- [ ] Performance Appraisals

## 3. Maintenance
The Lab Manager ensures all files are updated and securely stored.
"""
        elif 'Training' in doc.title:
            return """## 1. In-Service Training Plan & Register
Continuous education is provided to maintain and improve staff competence.

## 2. Annual Training Plan Topics
- Biosafety and Spill Management (Biannual)
- Quality Control and EQA (Annual)
- Patient Rights and Confidentiality (Annual)
- Fire Safety and Evacuation (Annual)
- New Equipment Operation (As needed)

## 3. Training Register
| Date | Topic | Trainer | Attendees (Names & Signatures) |
| --- | --- | --- | --- |
| [Date] | [Topic] | [Name] | [Signatures] |
"""
        elif 'Credential Verification' in doc.title:
            return """## 1. Credential Verification Record
The laboratory verifies the authenticity of academic and professional credentials.

## 2. Verification Log
| Employee Name | Document Verified (Degree/License) | Verification Method (Online Portal/University) | Verified By | Date | Signature |
| --- | --- | --- | --- | --- | --- |
| [Name] | [Document] | [Method] | [Name] | [Date] | |

## 3. Policy
No technical staff may perform independent patient testing until their primary qualification is verified.
"""
        return None

    def get_fms_template(self, doc):
        if 'Laws' in doc.title or 'Legal Update' in doc.title:
            return """## 1. Legal and Regulatory Compliance File
Al Shifa Laboratory monitors and complies with applicable laws.

## 2. Applicable Regulations
- Punjab Healthcare Commission (PHC) Act and MSDS
- Environmental Protection Agency (EPA) Hospital Waste Management Rules
- Pakistan Medical and Dental Council (PMDC) regulations for pathologists
- Local government regulations for signage and operations

## 3. Legal Update Review Register
| Date of Review | Regulation Reviewed | Updates Identified | Actions Taken | Reviewed By |
| --- | --- | --- | --- | --- |
| [Date] | [Regulation] | [Updates] | [Action] | [Name] |

## 4. Responsibility
The Lab Manager reviews regulatory updates annually or when notified by authorities.
"""
        elif 'Workflow' in doc.title or 'Access' in doc.title:
            return """## 1. Facility Workflow and Access Policy
To ensure safety and prevent cross-contamination, the laboratory maintains separated workflows.

## 2. Zonal Separation
- **Public Zone:** Reception, waiting area, patient washrooms.
- **Semi-Restricted Zone:** Phlebotomy/sample collection area.
- **Restricted Zone:** Core laboratory processing and testing areas.

## 3. Unauthorized Access Policy
- Patients and unauthorized visitors are strictly prohibited from entering the restricted analytical areas.
- "Restricted Area - Authorized Personnel Only" signs must be displayed at all entry points to the analytical area.
- Service engineers and vendors must be accompanied by staff.

## 4. Display Requirement
Signage must clearly separate public areas from restricted areas.
"""
        elif doc.code == 'DOC-FMS-01' or 'Fire and Non-Fire Emergency SOP' in doc.title or 'Emergency Policy' in doc.title:
            return """## 1. Purpose
To ensure the safety of patients, staff, and visitors during various laboratory emergencies.

## 2. Emergency Types
The laboratory identifies and prepares for the following:
- **Fire Emergency:** Response to smoke or flames.
- **Electrical Failure:** Safe shutdown of equipment and backup power use.
- **Chemical/Biological Spill:** Immediate containment and cleaning protocols.
- **Accident / Injury:** First aid and referral procedures.
- **Security / Violence:** Handling disruptive behavior.

## 3. General Response Protocol
1. **Safety First:** Evacuate patients and visitors if necessary.
2. **Alert:** Inform the Lab Manager immediately.
3. **Contact:** Use the "Emergency Contact List" for Fire Brigade, Ambulance, or Police.
4. **Action:** Use available safety equipment (Fire Extinguishers) only if safe to do so.

## 4. Staff Responsibility
All staff must be familiar with the location of emergency exits and fire extinguishers. Mock drills are conducted annually.

## 5. Display
This policy summary and the emergency contact list must be displayed near the laboratory entrance.
"""
        elif 'Emergency Exit' in doc.title or 'Emergency Contact' in doc.title:
            return """## 1. Emergency Evacuation and Contact Plan

## 2. Evacuation Plan
- In case of fire or major emergency, remain calm.
- Follow the green 'EXIT' signs.
- Do not use elevators (if applicable).
- Assemble at the designated safe point outside the building.

## 3. Emergency Contacts
| Service | Contact Number |
| --- | --- |
| Lab Manager | [To be filled] |
| Fire Brigade | 16 |
| Edhi Ambulance | 115 |
| Local Police | 15 |
| Nearest Hospital | [To be filled] |

## 4. Display
This plan and contact list must be prominently displayed near the entrance and in the staff area.
"""
        elif 'Fire Extinguisher' in doc.title or 'Physical Verification' in doc.title:
            return """## 1. Fire Safety and Extinguisher Inspection Checklist

## 2. Extinguisher Inventory
| ID | Type (e.g., DCP, CO2) | Location | Expiry Date |
| --- | --- | --- | --- |
| 1 | [Type] | [Location] | [Date] |

## 3. Monthly Inspection Log
| Date | Extinguisher ID | Pressure Gauge in Green? | Pin intact? | Sign of Damage? | Inspected By |
| --- | --- | --- | --- | --- | --- |
| [Date] | [ID] | [Y/N] | [Y/N] | [Y/N] | [Sign] |

## 4. Responsibility
The Lab Manager is responsible for monthly inspections and arranging timely refills before expiry.
"""
        elif 'Mock Drill' in doc.title or 'Emergency Training' in doc.title:
            return """## 1. Mock Drill & Emergency Training Record
Annual mock drills are conducted to ensure emergency preparedness.

## 2. Drill Report Form
**Date of Drill:** [Date]
**Type of Drill:** [Fire Evacuation / Spill Response]
**Scenario Assumed:** [Details]

## 3. Observations
- Time taken to evacuate: [Minutes]
- Were exits clear? [Yes/No]
- Did staff follow protocols? [Yes/No]

## 4. Corrective Actions
- [List any issues found during the drill and how they will be fixed]

## 5. Attendees
| Staff Name | Designation | Signature |
| --- | --- | --- |
| [Name] | [Role] | |

## 6. Review
Lab Manager signs off on the drill report.
"""
        return None

    def get_mer_template(self, doc):
        if 'Procurement' in doc.title or 'Purchase' in doc.title:
            return """## 1. Procurement SOP
Ensures quality materials are purchased from evaluated vendors.

## 2. Procedure
1. **Requisition:** Section heads identify requirements.
2. **Approval:** Lab Manager approves routine purchases; Consultant Pathologist approves capital equipment.
3. **Vendor Selection:** Purchases are made only from vendors providing quality assurance and proper cold-chain transport (for reagents).
4. **Purchase Order (PO):** A formal PO is generated for significant orders, clearly stating specifications.

## 3. Purchase Order Template
**PO Number:** [To be filled]   **Date:** [Date]
**Vendor:** [Name]

| Item Description | Specification / Cat No | Qty | Unit Price |
| --- | --- | --- | --- |
| [Item] | [Spec] | [Qty] | [Price] |

**Authorized By:** ___________________
"""
        elif 'Specification' in doc.title:
            return """## 1. Equipment & Reagent Specifications File
Maintains standardized requirements for laboratory supplies.

## 2. Specification Record
| Item Category | Minimum Required Specification | Preferred Brand/Vendor | Storage Requirement |
| --- | --- | --- | --- |
| Biochemistry Kits | CE marked / FDA approved, compatible with [Machine Name] | [Brand] | 2-8°C |
| Hematology Analyzer | 3-part / 5-part differential, closed tube sampling | [Brand] | Room Temp |
| Vacutainers | Sterile, vacuum intact, clear expiry date | [Brand] | Room Temp |

## 3. Responsibility
Consultant Pathologist reviews specifications before major changes in test methodology.
"""
        elif 'Stock' in doc.title or 'Inventory' in doc.title:
            return """## 1. Inventory & Stock Register
Tracks the receipt and consumption of reagents and consumables.

## 2. Stock Register Format
**Item Name:** [To be filled]
**Storage Condition:** [To be filled]

| Date | Received (Qty) | Lot No | Expiry Date | Consumed (Qty) | Balance | Signature |
| --- | --- | --- | --- | --- | --- | --- |
| [Date] | [Qty] | [Lot] | [Date] | [Qty] | [Qty] | |

## 3. Inventory Management
- First-In, First-Out (FIFO) principle must be followed.
- Items nearing expiry (within 30 days) must be highlighted in the Near-Expiry Alert Register.
"""
        elif 'Reagent Storage' in doc.title or 'Label' in doc.title:
            return """## 1. Reagent Storage and Use SOP
Ensures reagents maintain their efficacy.

## 2. Storage Guidelines
- Reagents must be stored strictly according to manufacturer instructions (e.g., 2-8°C, -20°C, or Room Temp).
- Refrigerators must be monitored daily (Temperature Log).
- Food items are strictly prohibited in reagent refrigerators.

## 3. Reagent Labeling Format
When reagents are prepared in-house or transferred to secondary containers, they must bear the following label:
- **Reagent Name:**
- **Concentration:**
- **Date Prepared/Opened:**
- **Expiry Date:**
- **Prepared By (Initials):**

## 4. Near-Expiry Alert
Reagents expiring within the month must be flagged visually (e.g., red sticker) and noted in the log.
"""
        elif 'Equipment Logbook' in doc.title or 'Maintenance' in doc.title or 'Calibration' in doc.title:
            return """## 1. Equipment Logbook & Maintenance Record
Tracks the usage, maintenance, and calibration of laboratory equipment.

## 2. Equipment Details
**Equipment Name:** [To be filled]   **Model:** [To be filled]
**Serial No:** [To be filled]        **Location:** [To be filled]

## 3. Daily/Weekly Maintenance Log
| Date | Task Performed (e.g., Cleaning, Prime) | Performed By | Status/Remarks |
| --- | --- | --- | --- |
| [Date] | [Task] | [Name] | [OK] |

## 4. Calibration / Breakdown Record
| Date | Event (Calibration/Breakdown/Service) | Details / Engineer Name | Next Due Date | Sign |
| --- | --- | --- | --- | --- |
| [Date] | [Event] | [Details] | [Date] | |

## 5. Display
A summarized log sheet must be displayed on or near the equipment.
"""
        return None

    def get_rrs_template(self, doc):
        if 'Patient Record' in doc.title or 'Unique Identifier' in doc.title:
            return """## 1. Patient Record & Unique Identifier Policy
Ensures traceability, security, and chronological maintenance of patient data.

## 2. Unique Identifier (MRN)
- Every patient/sample registered must be assigned a Unique Identifier (Lab ID / MRN).
- The ID must link the patient demographic details to the sample and the final report.

## 3. Record Maintenance
- Records are maintained chronologically in the Laboratory Information System (LIS) / Computerized System.
- Every entry must auto-capture or record the Date, Time, and Identity of the staff making the entry.

## 4. Data Security & Retention
- Only authorized staff have access to modify data.
- Records must be retained as per local regulations (e.g., minimum 2 years for routine reports, longer for specific biopsies).
- Regular backups of the LIS must be maintained.
"""
        elif 'Reporting' in doc.title or 'Turnaround' in doc.title:
            return """## 1. Laboratory Reporting & Turnaround Time (TAT) SOP

## 2. Reporting Protocol
- Results are verified against IQA prior to release.
- Abnormal results must be re-checked before final verification.
- Reports must clearly show Patient ID, Name, Test, Result, Units, Biological Reference Intervals, and the Pathologist's signature.

## 3. Turnaround Time (TAT) List
| Test Category | Standard TAT | Urgent/STAT TAT |
| --- | --- | --- |
| Routine Chemistry | 4 Hours | 2 Hours |
| Routine Hematology | 2 Hours | 1 Hour |
| Serology | 24 Hours | - |
| Microbiology (C&S) | 72 Hours | - |

## 4. TAT Monitoring
The QA Focal person will audit TAT compliance monthly. Delays must be documented with reasons.
"""
        elif 'Critical Result' in doc.title:
            return """## 1. Critical Result Notification SOP
Defines the procedure for handling life-threatening laboratory results.

## 2. Critical Values List
*Note: A detailed list verified by the Pathologist must be appended.*
- **Glucose:** < 40 mg/dL or > 400 mg/dL
- **Potassium:** < 2.5 mEq/L or > 6.0 mEq/L
- **Hemoglobin:** < 7.0 g/dL or > 20.0 g/dL
- **Platelets:** < 40,000 /uL

## 3. Notification Protocol
1. Re-run the test to confirm the result.
2. Immediately inform the referring physician or the patient/attendant via phone.
3. Document the notification in the Critical Result Register.

## 4. Critical Result Register Form
| Date/Time | Patient Name & ID | Test | Result | Informed To (Name/Rel) | Informed By | Remarks |
| --- | --- | --- | --- | --- | --- | --- |
| [Date/Time] | [Details] | [Test] | [Value] | [Person] | [Staff] | [Notes] |
"""
        elif 'Notifiable Disease' in doc.title:
            return """## 1. Notifiable Disease Reporting Policy
Ensures compliance with public health surveillance requirements.

## 2. List of Notifiable Diseases
As per Government of Punjab guidelines, positive results for the following must be reported:
- Polio
- Dengue
- COVID-19
- Measles
- Tuberculosis (TB)
- HIV
- Cholera

## 3. Reporting Mechanism
- The Lab Manager is responsible for reporting positive cases to the District Health Authority (DHA) / relevant portal within 24 hours.

## 4. Reporting Log
| Date | Patient Name & ID | Disease Detected | Reported To (Authority) | Reported By |
| --- | --- | --- | --- | --- |
| [Date] | [Details] | [Disease] | [Authority] | [Staff] |
"""
        elif 'Access/Code' in doc.title:
            return """## 1. Patient Report Access Policy
Ensures patient confidentiality during report retrieval.

## 2. Procedure
- Hard copy reports are handed over only upon presentation of the original laboratory receipt.
- If the receipt is lost, verifying patient identity via CNIC or phone number is required.
- **Online Access:** Patients accessing reports online must use their unique Lab ID / MRN and the specific password/PIN provided on their receipt.
- Laboratory staff shall not disclose results over the phone without verifying the patient's identity through standard security questions (e.g., exact age, referring doctor, and tests ordered).
"""
        return None

    def get_bsbs_template(self, doc):
        if 'Biosafety SOP' in doc.title or 'Spill Kit' in doc.title or 'Sample Transport' in doc.title:
            return """## 1. Biosafety and Spill Management SOP
Ensures the protection of staff and the environment from biological hazards.

## 2. General Biosafety Rules
- PPE (Gloves, Lab Coats, Masks) is mandatory in the analytical area.
- Mouth pipetting is strictly prohibited.
- Eating, drinking, and applying cosmetics in the lab are prohibited.
- Hands must be washed after handling samples and before leaving the lab.

## 3. Spill Management Protocol (Spill Kit)
- **Spill Kit Contents:** Hypochlorite solution (10%), absorbent material, forceps/scoop, biohazard bags, heavy-duty gloves, safety goggles.
- **Procedure:**
  1. Wear PPE.
  2. Cover the spill with absorbent material.
  3. Pour 10% Hypochlorite over the material and wait 20 minutes.
  4. Collect carefully using forceps and discard in a yellow biohazard bag.
  5. Mop the area with water.

## 4. Sample Transportation
- Samples transported from collection centers must be in sealed, leak-proof primary containers.
- Secondary transport boxes must be rigid, insulated, and contain cool packs to maintain cold chain.
- Transport boxes must display a Biohazard symbol.

## 5. Responsibility
The appointed Biosafety Focal Person monitors compliance and maintains the Incident Register.
"""
        elif 'Vaccination' in doc.title or 'Medical Checkup' in doc.title:
            return """## 1. Staff Health & Vaccination Record
Ensures occupational health safety for laboratory personnel.

## 2. Vaccination Policy
- All staff handling clinical specimens must be vaccinated against Hepatitis B.
- The laboratory facilitates/monitors the vaccination schedule (3 doses).

## 3. Medical Checkup Policy
- Annual physical checkups and baseline screening (e.g., CBC, LFTs, HBsAg, Anti-HCV) are recommended for technical staff.

## 4. Health Record Log
| Staff Name | Designation | Hep B Dose 1 | Hep B Dose 2 | Hep B Dose 3 | Anti-HBs Titer | Annual Checkup Date |
| --- | --- | --- | --- | --- | --- | --- |
| [Name] | [Role] | [Date] | [Date] | [Date] | [Result] | [Date] |

## 5. Confidentiality
Staff health records are kept strictly confidential in personal files.
"""
        elif 'Incident' in doc.title:
            return """## 1. Incident & Needle Stick Injury Register
To document and manage occupational exposure incidents.

## 2. Protocol for Needle Stick Injury
1. Wash the area immediately with soap and running water (do not squeeze/scrub).
2. Report to the Lab Manager immediately.
3. Draw baseline blood sample of the staff and (if possible) the source patient for HIV, HBV, HCV testing.
4. Consult a physician for Post-Exposure Prophylaxis (PEP) evaluation.

## 3. Incident Register
| Date | Name of Staff | Description of Incident (e.g. Needle stick) | Immediate Action Taken | Follow-up Required? | Manager Sign |
| --- | --- | --- | --- | --- | --- |
| [Date] | [Name] | [Details] | [Action] | [Yes/No] | |
"""
        elif 'Waste Management SOP' in doc.title or 'Segregation' in doc.title:
            return """## 1. Healthcare Waste Management SOP
Ensures safe handling and disposal of laboratory waste per EPA guidelines.

## 2. Waste Segregation Protocol
Waste must be segregated at the source using color-coded bins:
- **Yellow Bin / Bag:** Infectious waste (swabs, contaminated tissue, tubes with blood).
- **Red Bin / Sharp Container:** Sharps (needles, lancets, broken glass) - Must be puncture-proof.
- **White / Black Bin:** General municipal waste (paper, wrappers).

## 3. Temporary Storage & Disposal
- Infectious waste bags must not be filled beyond 3/4 capacity.
- Bags are sealed and stored in a designated secure area away from the public.
- Final disposal is handed over to a certified waste management contractor.

## 4. Display Requirement
A visual chart showing waste segregation color codes must be displayed near the washing/disposal sinks.
"""
        elif 'Waste Disposal' in doc.title:
            return """## 1. Waste Disposal Transport Record
Logs the handover of infectious waste to the authorized contractor.

## 2. Contractor Details
**Authorized Waste Contractor:** [To be filled]
**MOU/Contract Valid Until:** [Date]

## 3. Waste Handover Log
| Date | Weight/Bags of Infectious Waste | Weight of Sharps Containers | Handed Over By (Lab Staff) | Collected By (Contractor Staff Sign) |
| --- | --- | --- | --- | --- |
| [Date] | [Qty] | [Qty] | [Name] | [Sign] |

## 4. Responsibility
The Biosafety/Waste Focal person ensures this register is updated during every collection.
"""
        return None

    def get_patient_template(self, doc):
        if 'Complaint' in doc.title:
            return """## 1. Patient Complaint Management System
Ensures patient grievances are heard, recorded, and addressed to improve service quality.

## 2. Complaint Register
Patients can lodge complaints verbally to the reception, or in writing.

| Date | Patient Name & Contact | Description of Complaint | Received By | Action Taken | Status (Resolved/Open) | Manager Sign |
| --- | --- | --- | --- | --- | --- | --- |
| [Date] | [Details] | [Complaint] | [Staff] | [Action] | [Status] | |

## 3. Review Process
- The Lab Manager must review all complaints within 24 hours.
- If no complaints are received in a month, a "No Complaints Received" entry must be signed by the manager at the end of the month.
"""
        elif 'Confidentiality' in doc.title or 'Consent' in doc.title:
            return """## 1. Patient Confidentiality & Consent Policy

## 2. Confidentiality Rules
- All patient records, test results, and personal information are strictly confidential.
- Staff must not discuss patient details in public areas (e.g., reception).
- Results are only issued to the patient or an authorized representative holding the receipt.

## 3. Informed Consent
- **Implied Consent:** Rolling up a sleeve for phlebotomy is considered implied consent for routine tests.
- **Explicit / Written Consent:** Required for sensitive tests (e.g., HIV) or invasive procedures beyond standard phlebotomy.
- **Minors/Incapacitated:** Consent must be taken from a parent or legal guardian.

## 4. Staff Awareness
All staff must sign a confidentiality undertaking upon joining.
"""
        elif 'Accessibility' in doc.title or 'Signage' in doc.title or 'Scope' in doc.title:
            return """## 1. Facility Accessibility and Signage Checklist
Ensures the laboratory is patient-friendly and accessible.

## 2. Signage Checklist (To be physically verified)
- [ ] Main Laboratory Signboard (Legal size/format)
- [ ] Directional Arrows leading to Reception
- [ ] Phlebotomy / Sample Collection Area signage
- [ ] Washrooms (Male/Female/Disabled marked)
- [ ] Scope of Services displayed at reception
- [ ] Tariff List (Prices) clearly displayed
- [ ] Emergency Exit signs clearly marked

## 3. Accessibility Facilities
- The laboratory has arrangements for disabled/elderly patients (e.g., ramp access, wheelchair availability, or priority phlebotomy facilitation).
- Waiting area has adequate seating, ventilation, and clean drinking water.
"""
        elif 'Sentinel' in doc.title or 'First Aid' in doc.title:
            return """## 1. Sentinel Event and First Aid Policy

## 2. First Aid Protocol
- A fully stocked First Aid Box is maintained at the phlebotomy station.
- If a patient feels dizzy or faints (syncope) during phlebotomy:
  1. Stop the procedure immediately.
  2. Lay the patient flat or lower their head.
  3. Loosen tight clothing and offer water when conscious.
  4. If condition worsens, shift to nearest emergency facility.

## 3. Sentinel Events
A sentinel event is an unexpected occurrence involving death or serious physical/psychological injury (e.g., severe adverse reaction to phlebotomy, sample misidentification leading to critical harm).

## 4. Sentinel Event Register
| Date | Event Description | Root Cause Analysis | Corrective/Preventive Action | Reported to Authority | Pathologist Sign |
| --- | --- | --- | --- | --- | --- |
| [Date] | [Details] | [Analysis] | [Action] | [Yes/No] | |
"""
        return None

    def get_generic_template(self, doc):
        return f"""## 1. Purpose
This document provides evidence and guidelines regarding: {doc.title}.

## 2. Description
{doc.description}

## 3. Guidelines / Instructions
- Ensure compliance with all PHC MSDS standards linked to this document.
- Follow standard operating procedures relevant to this section.
- If this requires a physical record, maintain it in the designated file.

## 4. Review
This document is subject to periodic review by the Laboratory Management.
"""
