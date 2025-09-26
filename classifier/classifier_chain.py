import os

from langchain_core.prompts import PromptTemplate

from apertus import LangchainApertus


def get_classifier_chain():
    prompt_template = PromptTemplate.from_template(
        """
        You are a helpful AI agent and an expert in classifying questions and statements in different fields of law.
        You are provided with a user input and a chat history. Use the provided classes for your classification.
        Your output should be a list of the classes and whether they are affected.
        Answer in the expected JSON format.

        classes:
            * traffic_law: This field of law is concerned with minor traffic infractions like speeding, parking tickets and running red lights.
            * civil_law: This field of law is concerned with liability when operating a vehicle like accidents and insurance.
            * criminal_law: This field of law is concerned with penal sanctions associated with operating a vehicle like suspended licences, fines and jail time.

        expected_format: {{
            'traffic_law': bool,
            'civil_law': bool,
            'criminal_law': bool,
        }}

        user_input: {user_input}

        chat_history: {chat_history}
        """
    )
    
    llm = LangchainApertus(api_key=os.environ.get("API_KEY"))

    return prompt_template | llm


if __name__ == "__main__":
    chain = get_classifier_chain()

    result = chain.invoke({"user_input": "Hello", "chat_history": []}).content

    print(result)