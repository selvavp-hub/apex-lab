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
    """
    url = (
        f"https://{instance_url}/services/data/v59.0/"
        f"einstein/prompt-templates/{template_api_name}/generations"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
    }
    payload = {
        "isPreview": True,
        "inputParams": {
            "valueMap": {
                key: {"value": val} for key, val in input_vars.items()
            }
        }
    }
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    log.info("Authenticating with Salesforce...")
    instance_url, access_token = get_sf_session()

    log.info("Invoking Case Resolution prompt template...")
    result = invoke_prompt_template(
        instance_url=instance_url,
        access_token=access_token,
        template_api_name="Case_Resolution_Assistant",   # your template API name
        input_vars={
            "case_subject":      "Cannot login to Salesforce Community",
            "case_description":  "Customer reports error: INVALID_SESSION_ID when accessing partner portal",
            "case_priority":     "High",
            "account_name":      "Acme Corp",
        }
    )

    print("\n" + "="*60)
    print("PROMPT TEMPLATE RESPONSE")
    print("="*60)
    generations = result.get("generations", [])
    for gen in generations:
        print(gen.get("text", "No text returned"))
    print("="*60)


if __name__ == "__main__":
    main()
