# Client Submission Inbox — File Drop Folder

This folder is where clients, family members, staff, and advisors drop binary files (PDFs and Excel spreadsheets) for automatic processing and filing into the archive.

## How to use

### For PDFs
1. Drop the PDF file into `pdfs/`
2. In Notion, create a new entry in **📥 Client Submission Inbox**:
   - Set **Type** to `PDF`
   - Enter the exact filename in **File Name** (e.g. `Q1-2026-tax-return.pdf`)
   - Set **Status** to `Pending`
   - Add any context in **Notes for Claude**

### For Excel files
1. Drop the Excel file into `excel/`
2. In Notion, create a new entry in **📥 Client Submission Inbox**:
   - Set **Type** to `Excel`
   - Enter the exact filename in **File Name** (e.g. `portfolio-summary-2026.xlsx`)
   - Set **Status** to `Pending`
   - Add any context in **Notes for Claude**

### For Parallel research or typed notes
No file needed — paste the content directly into the **Content / Notes** field in the Notion inbox entry.

## What happens next

A scheduled Claude task runs automatically and processes all `Pending` entries:
- Extracts text from PDFs
- Reads data from Excel files
- Classifies and files each submission to the correct archive domain
- Updates the Notion entry Status to `Filed` and adds a link to the archive record
- Moves processed files to `processed/`

## Folder structure

```
_inbox/
  pdfs/        ← drop PDF files here
  excel/        ← drop Excel files here
  processed/    ← Claude moves files here after filing
```

## Notion Inbox
https://app.notion.com/p/2edd3c17c6b04c2dab405e1f0036cffd
