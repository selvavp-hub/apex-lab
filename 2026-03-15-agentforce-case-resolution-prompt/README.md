# 🤖 Agentforce Prompt Template: Case Resolution Assistant

![AI](https://img.shields.io/badge/AI-Powered-FF6B6B?style=flat&logo=openai&logoColor=white) ![Salesforce](https://img.shields.io/badge/Salesforce-00A1E0?style=flat&logo=salesforce&logoColor=white)

> **Category**: Salesforce + AI

## Overview

A production-ready Agentforce / Einstein Copilot prompt template for a Case Resolution AI Agent. Includes the system prompt, user prompt structure, and a Python script to test it via the Salesforce API.

## Files

```
2026-03-15-agentforce-case-resolution-prompt/
├── `.env.example`
├── `case_resolution_agent_prompt.md`
├── `test_prompt_api.py`
```

## Code Preview

```python
"""
Test the Agentforce Prompt Template via Salesforce REST API.

Requirements:
    pip install simple-salesforce python-dotenv requests

Environment variables (.env):
    SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN, SF_DOMAIN
"""
import os
import requests
import logging
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def get_sf_session() -> tuple[str, str]:
    """Authenticate and return (instance_url, access_token)."""
    sf = Salesforce(
        username=os.environ["SF_USERNAME"],
        password=os.environ["SF_PASSWORD"],
        security_token=os.environ["SF_SECURITY_TOKEN"],
        domain=os.environ.get("SF_DOMAIN", "login"),
    )
    return sf.sf_instance, sf.session_id


def invoke_prompt_template(
    instance_url: str,
    access_token: str,
    template_api_name: str,
    input_vars: dict
) -> dict:
    """
    Invoke an Einstein Prompt Template via the Connect API.
    API: POST /services/data/v59.0/einstein/prompt-templates/{templateApiName}/generations
// ... (see full file)
```

## About

This project is part of [apex-lab](https://github.com/selvavp-hub/apex-lab) —
a daily series of real Salesforce & AI code projects demonstrating
Apex development, LWC, integrations, and applied AI.

---
*Generated as part of the daily Salesforce coding series.*
