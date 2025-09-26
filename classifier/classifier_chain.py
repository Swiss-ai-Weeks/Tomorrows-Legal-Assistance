import os

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser

from apertus import LangchainApertus


def get_classifier_chain():
    prompt_template = PromptTemplate.from_template(
"""
You are a helpful AI agent and an expert in classifying questions and statements in different fields of law.
You are provided with a user input and a chat history. Use the provided classes for your classification.
Your output should be a list of the classes and whether they are affected.
Answer in the expected JSON format and don't generate any other content.

classes:
* traffic_law
  * Definition: Minor violations of traffic rules. Usually handled administratively. No criminal record unless repeated or particularly dangerous.
  * Examples / Measures:
    * Setting the wrong arrival time on a parking disc → CHF 40 fine
    * Speeding within town up to 15 km/h over the limit → warning or fine
    * Speeding outside town up to 20 km/h over limit → fine
    * Highway speeding up to 25 km/h over limit → fine
  * Goal: Ensure compliance with traffic rules and prevention.
* civil_law
  * Definition: Liability and compensation matters related to traffic incidents. Focus is on financial/insurance consequences.
  * Examples:
    * Accidents with property or personal damage → liability insurance pays damages
    * Insurance can reclaim payments in cases of gross negligence (e.g., driving under alcohol/drugs)
    * Disputes over compensation after an accident
  * Goal: Financial restoration and compensation of damages.
* criminal_law
  * Definition: Traffic offenses with criminal relevance. Penalties can include fines, license suspension, or imprisonment.
  * Examples:
    * Speeding >16 km/h in town, >21 km/h outside town. >25km/h highway
    * Driving under significant influence of alcohol (>0.5 ‰)
    * Dangerous driving, hit-and-run accidents
    * Repeat offenders → traffic psychological assessment, immediate license suspension
  * Goal: Protect life, health, and public safety.

expected_format:
{{
    "traffic_law": bool,
    "civil_law": bool,
    "criminal_law": bool,
}}

user_input:
{user_input}

chat_history:
{chat_history}
"""
    )
    
    llm = LangchainApertus(api_key=os.environ["API_KEY"], temperature=0)

    return prompt_template | llm | JsonOutputParser()


if __name__ == "__main__":
    import sys

    chain = get_classifier_chain()

    result = chain.invoke({"user_input": sys.argv[1], "chat_history": []})

    print(result, type(result))