# IT Access Control Audit & Risk Dashboard

A portfolio project that models a Technology Risk access-governance workflow: ingest access evidence, execute repeatable control tests, prioritize exceptions, and track remediation.

## Business use case

Technology Risk and IT audit teams may review access to business-critical systems and evaluate controls around account lifecycle, privileged access, MFA, segregation of duties, and access recertification. This application turns structured evidence into reviewable findings.

## Workflow

```text
Access evidence
    ↓
Evidence validation
    ↓
Control tests
    ↓
Risk findings
    ↓
Recommendations
    ↓
Remediation status
```

## Control tests

- Inactive accounts retaining access
- Privileged access without MFA
- Potential segregation-of-duties conflicts
- Missing access-review evidence

## Technology

Python, Flask, SQLite, HTML, CSS, JavaScript, pytest, Docker, GitHub Actions.

## Local setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

## Test

```bash
pytest
```

## Docker

```bash
docker build -t it-access-audit .
docker run -p 5000:5000 it-access-audit
```

## Portfolio relevance

Demonstrates access governance, internal controls, risk assessment, audit evidence handling, security awareness, data validation, API development, automated testing, and CI/CD.

All records and scenarios are fictional and created for independent portfolio development. This project does not represent client work.
