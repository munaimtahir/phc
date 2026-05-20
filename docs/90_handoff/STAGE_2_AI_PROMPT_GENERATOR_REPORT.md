# Stage 2 AI Prompt Generator Report

## Objective
Implement a safe Stage 2 AI Prompt Generator inside the PHC Lab Compliance Tracker to produce copyable, indicator-specific prompts for compliance drafting workflows, without any live AI API integration.

## Scope Delivered
- Added indicator-specific prompt generation for 8 prompt types:
  1. SOP / Policy Draft
  2. Register Template
  3. Display Notice / Poster Text
  4. Gap Action Plan
  5. Surveyor Explanation
  6. Evidence Checklist
  7. Staff Training Material
  8. Simple Compliance Summary
- Added generator UI panel to indicator detail page.
- Added copy-to-clipboard action.
- Added optional prompt download as `.txt`.
- Kept all generation local using existing indicator/compliance data.

## No Live AI Integration
- No calls were added to OpenAI, Gemini, or any external AI API.
- The feature only prepares structured prompt text for manual copy/paste.

## Implementation Details
- Service added: `indicators/services/prompt_generator.py`
  - `build_prompt(indicator, prompt_type)`
  - `get_prompt_context(indicator)`
  - `render_prompt_template(prompt_type, context)`
- View integration: `indicators/views.py`
  - Adds prompt type selection via query parameter.
  - Generates prompt text server-side.
  - Supports `.txt` download with `download=1`.
- UI integration: `templates/indicators/indicator_detail.html`
  - New **AI Prompt Generator** panel.
  - Prompt type buttons, generated textarea, copy button, download button.
  - Safety instruction shown to user.

## Data Included In Prompts
- Fixed lab profile:
  - Al Shifa Laboratory
  - Dr. Muhammad Munaim Tahir
  - Dr. Mubasher Ahmed
- Indicator/compliance fields used when available, otherwise `Not specified in tracker.`

## Validation
- Prompt generator tests added in `indicators/tests_prompt_generator.py`.
- Covered:
  - Lab name inclusion
  - Indicator number inclusion
  - SOP approval section inclusion
  - Register frequency/register name inclusion
  - Gap summary inclusion
  - Blank optional fields safety

## Safety Notes
- Prompt output is not auto-saved as evidence.
- User review is required before uploading generated documents as evidence.
- This stage is prompt-generation only.

## Limitations
- No one-click creation of evidence draft placeholders in this sprint.
- No live model response preview inside app by design (safety stage).

## Handoff
- Feature is ready for use in indicator detail pages.
- Future stage can add controlled AI execution after policy/security review.
