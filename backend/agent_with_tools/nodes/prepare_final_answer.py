from backend.agent_with_tools.schemas import AgentState
from backend.apertus import get_apertus_model
from langchain_core.prompts import ChatPromptTemplate
from textwrap import dedent
import os

GEMINI_LLM = os.getenv("GEMINI_LLM", "FALSE") == "TRUE"

if not GEMINI_LLM:
    prepare_final_answer_prompt = dedent("""
    Use all of the following information about an AXA-ARAG legal case estimation and provide 
    a final, user-friendly customer-facing answer/estimation.
                                        
    Rules:
    - Make sure your answer is AS short as possible concise and contains all relevant information according to the findings.
    - Make sure your answer is actionable and gives clear guidance on whether the case is worth pursuing or not.
    - If you're missing any information, state this clearly is in the answer provided.
    - Your answer must be formulated in a customer-friendly, but non-polite way.
    - In you answer you must mention similar cases to give a good overview to our customer.
                                        
    Information:
    - Determined Case Category: {case_category}
    - Likelihood to win the case: {likelihood}
    - Estimated time: {estimated_time}
    - Estimated cost: {estimated_cost}
    - Explanation: {explanation}

    Start your super short ENGLISH output :                             
    """)
else:
    prepare_final_answer_prompt = dedent("""
    Use all of the following information about an AXA-ARAG legal case estimation and provide 
    a final, user-friendly customer-facing answer/estimation.
                                        
    Rules:
    - Make sure your answer is  concise and contains all relevant information according to the findings.
    - Make sure your answer is actionable and gives clear guidance on whether the case is worth pursuing or not.
    - If you're missing any information, state this clearly is in the answer provided.
    - Your answer must be formulated in a customer-friendly, but non-polite way.
    - In you answer you must mention similar cases to give a good overview to our customer.
                                        
    Information:
    - Determined Case Category: {case_category}
    - Likelihood to win the case: {likelihood}
    - Estimated time: {estimated_time}
    - Estimated cost: {estimated_cost}
    - Explanation: {explanation}

    """)


def prepare_final_answer_node(state: AgentState) -> AgentState:
    """
    Formulate the final information in a helpful + user-friendly way.

    Args:
        state: Current agent state with all analysis results

    Returns:
        Updated state with the final answer
    """
    model = get_apertus_model()
    runnable = ChatPromptTemplate.from_template(prepare_final_answer_prompt) | model
    # print("\n".join([part for part in state.explanation_parts]))
    response = runnable.invoke(
        {
            "case_category": state.category,
            "likelihood": state.likelihood_win,
            "estimated_time": state.time_estimate,
            "estimated_cost": state.cost_estimate,
            "explanation": "\n".join([part for part in state.explanation_parts])
            if state.explanation_parts
            else "",
        }
    )
    state.result.final_answer = response.content
    return state
