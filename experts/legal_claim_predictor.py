import os
from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from .tools.estimators.estimator import estimate_chance_of_winning, estimate_time, estimate_costs
from ..apertus.apertus import LangchainApertus

# --- Provided Functions ---

def estimate_chance_of_winning(claims_type: str, claims_category: str):
    """
    Estimate the chance of winning based on claims type and category.
    """
    if claims_type == "traffic_criminal_law":
        if claims_category == "Speeding 20 km/h outside built-up areas":
            chance_of_winning = "10–15% (usually hopeless unless technical errors)"
        elif claims_category == "Driving under influence – 1.8 ‰ alcohol, license withdrawal":
            chance_of_winning = "<10% (almost hopeless, mandatory withdrawal)"
        elif claims_category == "Parking lot accident CHF 2,500, no witnesses":
            chance_of_winning = "50–60% (good if insurance involved; depends on proof)"
        elif claims_category == "Parking fine expired by 5 minutes":
            chance_of_winning = "<10% (hopeless)"
        elif claims_category == "Alcohol 0.6 ‰ (penalty order)":
            chance_of_winning = "20–30% (low, slightly better if strong evidence)"
        else:
            chance_of_winning = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "Termination (poor performance)":
            chance_of_winning = "20%"
        elif claims_category == "Increase in workload":
            chance_of_winning = "0%"
        elif claims_category == "Lohn Monate ausstehend":
            chance_of_winning = "100%"
        elif claims_category == "Fristlose Kündigung":
            chance_of_winning = "80%"
        elif claims_category == "Kündigung während Krankheit/Unfall":
            chance_of_winning = "100%"
        else:
            chance_of_winning = "unknown"
    else:
        chance_of_winning = "unknown"
    return chance_of_winning

def estimate_time(claims_type: str, claims_category: str):
    """
    Estimate the time required based on claims type and category.
    """
    if claims_type == "traffic_criminal_law":
        if claims_category == "Speeding 20 km/h outside built-up areas":
            time = "Paid: 30 days; Contested: 3–6 months+"
        elif claims_category == "Driving under influence – 1.8 ‰ alcohol, license withdrawal":
            time = "6–12 months+"
        elif claims_category == "Parking lot accident CHF 2,500, no witnesses":
            time = "1–6 months"
        elif claims_category == "Parking fine expired by 5 minutes":
            time = "Paid: 30 days; Contested: 3–6 months"
        elif claims_category == "Alcohol 0.6 ‰ (penalty order)":
            time = "3–6 months"
        else:
            time = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "Termination (poor performance)":
            time = "3 Months"
        elif claims_category == "Increase in workload":
            time = "0 Months"
        elif claims_category == "Lohn Monate ausstehend":
            time = "5 Months"
        elif claims_category == "Fristlose Kündigung":
            time = "6 Months"
        elif claims_category == "Kündigung während Krankheit/Unfall":
            time = "3 Months"
        else:
            time = "unknown"
    else:
        time = "unknown"
    return time

def estimate_costs(claims_type: str, claims_category: str):
    """
    Estimate the costs involved based on claims type and category.
    """
    if claims_type == "traffic_criminal_law":
        if claims_category == "Speeding 20 km/h outside built-up areas":
            costs = "Fine: CHF 240; Admin fees: CHF 0–600; Lawyer: CHF 1,000–5,000; Court: CHF 300–3,000"
        elif claims_category == "Driving under influence – 1.8 ‰ alcohol, license withdrawal":
            costs = "Fine: CHF 500–10,000; Road Traffic fees: CHF 400–1,000; Assessment: CHF 1,500–3,000; Lawyer: CHF 2,000–8,000"
        elif claims_category == "Parking lot accident CHF 2,500, no witnesses":
            costs = "Deductible CHF 200–1,000; Lawyer usually unnecessary (insurance covers); private lawyer CHF 1,000–4,000"
        elif claims_category == "Parking fine expired by 5 minutes":
            costs = "Fine: CHF 40–80; Lawyer: CHF 500–2,000; Court: CHF 300–1,000"
        elif claims_category == "Alcohol 0.6 ‰ (penalty order)":
            costs = "Fine: CHF 500–1,000; Road Traffic fees: CHF 200–1,000; Lawyer: CHF 1,000–3,000; Court: CHF 500–3,000"
        else:
            costs = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "Termination (poor performance)":
            costs = "3500"
        elif claims_category == "Increase in workload":
            costs = "0"
        elif claims_category == "Lohn Monate ausstehend":
            costs = "5000"
        elif claims_category == "Fristlose Kündigung":
            costs = "2500"
        elif claims_category == "Kündigung während Krankheit/Unfall":
            costs = "1500"
        else:
            costs = "unknown"
    else:
        costs = "unknown"
    return costs

# --- Langchain Implementation ---

# 1. Define the structured output model using Pydantic
class ClaimDetails(BaseModel):
    """Structured data model for a legal claim."""
    claims_type: Literal["traffic_criminal_law", "employment_law"] = Field(
        description="The general type of legal claim."
    )
    claims_category: str = Field(
        description="The specific category within the legal claim type."
    )

# 2. Set up the output parser
parser = PydanticOutputParser(pydantic_object=ClaimDetails)

# 3. Create a high-quality prompt template
prompt_template = """
You are an expert legal assistant. Your task is to analyze an incoming email and extract the key details of the legal claim.

You must classify the claim into one of the following main types:
- traffic_criminal_law
- employment_law

Then, you must identify the specific category for the claim. Here are the possible categories for each type:

If the claims_type is 'traffic_criminal_law', the possible categories are:
- Speeding 20 km/h outside built-up areas
- Driving under influence – 1.8 ‰ alcohol, license withdrawal
- Parking lot accident CHF 2,500, no witnesses
- Parking fine expired by 5 minutes
- Alcohol 0.6 ‰ (penalty order)

If the claims_type is 'employment_law', the possible categories are:
- Termination (poor performance)
- Increase in workload
- Lohn Monate ausstehend
- Fristlose Kündigung
- Kündigung während Krankheit/Unfall

Please analyze the following email and provide the output in the required structured format.

{format_instructions}

Here is the email:
---
{email_text}
---
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["email_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 4. Main execution function
def process_legal_email(email_content: str):
    """
    Processes an email to extract claim details and estimate outcomes.
    
    Args:
        email_content: The text content of the email.
        api_key: Your OpenAI API key.
    """
    # Initialize the language model
    # For this example, we use OpenAI. Ensure you have the library installed:
    # pip install langchain-openai
    model = LangchainApertus(api_key=os.environ.get("API_KEY"))

    # Create the processing chain
    chain = prompt | model | parser

    try:
        # Invoke the chain with the email content
        extracted_data = chain.invoke({"email_text": email_content})

        # Use the extracted data to call the estimation functions
        claims_type = extracted_data.claims_type
        claims_category = extracted_data.claims_category

        chance = estimate_chance_of_winning(claims_type, claims_category)
        time = estimate_time(claims_type, claims_category)
        costs = estimate_costs(claims_type, claims_category)

        # Print the results
        print("--- Legal Claim Analysis ---")
        print(f"Claim Type: {claims_type}")
        print(f"Claim Category: {claims_category}")
        print("\n--- Estimates ---")
        print(f"Chance of Winning: {chance}")
        print(f"Estimated Time: {time}")
        print(f"Estimated Costs: {costs}")
        print("--------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Could not process the email. Please ensure the content is clear and the API key is valid.")

# --- Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: Replace "YOUR_OPENAI_API_KEY" with your actual OpenAI API key.
    # You can get a key from https://platform.openai.com/
    # It is recommended to set this as an environment variable for security.
    # Example Email 1: Traffic Law
    # email_1 = """
    # Hello,
    
    # I received a penalty order today. I was caught driving with a blood alcohol level of 0.6 per mille. 
    # What are my options here?
    
    # Thanks,
    # Peter
    # """
    # print("Processing Example 1: Traffic Law...")
    # process_legal_email(email_1)

    # print("\n" + "="*50 + "\n")

    # # Example Email 2: Employment Law
    # email_2 = """
    # Hi there,
    
    # I'm in a difficult situation. My boss just fired me without any notice period. 
    # He claims I stole from the company, which is not true. Can you help?
    
    # Best,
    # Maria
    # """
    # print("Processing Example 2: Employment Law...")
    # process_legal_email(email_2)

    email_3 = """Objet : Demande d'assistance juridique – Litige concernant des frais d'avocat\n\nMadame, Monsieur,\n\nJe m'appelle Sophie Dubois et je suis titulaire de la police n° 87654321 avec AXA ARAG. Je vous contacte aujourd'hui car j'ai besoin de conseils juridiques concernant une situation que je rencontre.\n\nIl y a quelque temps, j'ai été condamnée à verser des sommes à titre de frais de justice à une autre partie, suite à une affaire où j'étais impliquée. L'avocat de cette autre partie, Monsieur B.________, m'a fait signifier un commandement de payer pour le montant total de ces frais, soit 12'400 francs, plus des intérêts et des frais de procédure.\n\nJ'avais une précédente démarche concernant ces mêmes frais, mais le juge de paix avait initialement rejeté la demande de paiement. Cependant, cette décision a été annulée par la Cour des poursuites et faillites du Tribunal cantonal du canton de Vaud. Ensuite, Monsieur B.________ a fait une nouvelle demande de paiement, et là, l'opposition que"""
    
    print("Processing Example 3.")
    process_legal_email(email_3)
