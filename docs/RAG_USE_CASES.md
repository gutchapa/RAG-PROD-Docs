# RAG System - Use Cases

This document outlines the primary use cases for the Retrieval-Augmented Generation (RAG) system developed for `RAG-PROD-Docs`.

## 1. Policy Q&A (Core)
**Goal:** Enable employees to ask natural language questions about company policies and receive accurate, cited answers.
- **Source:** Policy documents (PDF/Text) in `downloads/`.
- **Example:** "What is the daily limit for food expenses?"
- **Success Criteria:** 95% Faithfulness (matches document text).

## 2. Expense Analysis (Data RAG)
**Goal:** Analyze structured financial data (CSV/Excel) to identify trends, anomalies, and compliance issues.
- **Source:** Expense reports (e.g., `petty_cash.csv`).
- **Example:** "Show me the variance in petty cash spending for Q1."
- **Success Criteria:** Accurate calculation of totals and averages (0% hallucination on numbers).

## 3. Onboarding Assistant
**Goal:** Guide new hires through standard operating procedures (SOPs).
- **Source:** Employee handbooks and onboarding checklists.
- **Example:** "How do I request access to the VPN?"

## 4. Compliance Auditing
**Goal:** Automatically cross-reference expense claims against policy limits.
- **Source:** Expense data + Policy documents.
- **Example:** "Flag any travel expenses exceeding the $50 daily allowance."

## 5. Document Version Comparison
**Goal:** Highlight changes between policy versions.
- **Source:** Multiple versions of the same policy document.
- **Example:** "What changed in the remote work policy between 2024 and 2025?"
