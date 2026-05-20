# PHC Lab Compliance Tracker

Single-purpose PHC/MSDS Clinical/Pathology Laboratory compliance tracker for a fixed 118-indicator checklist.

## Stage 2: AI Prompt Generator (Safe, Local)
The indicator detail page now includes an **AI Prompt Generator** panel that prepares structured prompts for manual use in ChatGPT/Gemini.

### What it does
- Generates indicator-specific prompt text for:
  - SOP / Policy
  - Register Template
  - Display Notice
  - Gap Action Plan
  - Surveyor Explanation
  - Evidence Checklist
  - Training Material
  - Compliance Summary
- Supports copy-to-clipboard.
- Supports prompt download as `.txt`.

### What it does NOT do
- No OpenAI/Gemini/live AI API call is made.
- No auto-generation of final evidence files inside the app.

### User flow
1. Open any indicator detail page.
2. In **AI Prompt Generator**, choose prompt type.
3. Copy prompt (or download `.txt`).
4. Paste into ChatGPT/Gemini externally.
5. Review output carefully before uploading as evidence.

### Prompt context includes
- Lab details:
  - Al Shifa Laboratory
  - Dr. Muhammad Munaim Tahir (Lab Manager / In-charge)
  - Dr. Mubasher Ahmed (Consultant Pathologist)
- Indicator + compliance data from tracker.
- Missing optional values are rendered as `Not specified in tracker.`.
