from openai import OpenAI
from langchain_openai import ChatOpenAI
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import concurrent, logging

APERTUS_MODEL_NAME = "swiss-ai/Apertus-70B"
APERTUS_BASE_URL = "https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"


class OpenaiApertus(OpenAI):
    """OpenAI based integration"""
    model = APERTUS_MODEL_NAME

    def __init__(self, api_key: str, **kwargs):
        super().__init__(
            api_key=api_key,
            base_url=APERTUS_BASE_URL,
            **kwargs,
        )


GEMINI_LLM = os.getenv("GEMINI_LLM", "FALSE") == "TRUE"
if GEMINI_LLM:
    print("STARTING WITH GEMINI")
    class LangchainApertus(ChatGoogleGenerativeAI):
        def __init__(self, api_key: str, **kwargs):
            super().__init__(
                model="gemini-2.5-flash-lite",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # other params...
            )
else:
    print("STARTING WITH APERTUS")
    class LangchainApertus(ChatOpenAI):
        """Langchain based integration"""
        def __init__(self, api_key: str, **kwargs):
            
            super().__init__(
                openai_api_key=api_key,
                model=APERTUS_MODEL_NAME,
                base_url=APERTUS_BASE_URL,
                **kwargs,
            )

        def _run_super_invoke(self, inputs, config):
            """
            Private wrapper function to call the actual method on the superclass.
            This function is submitted to the executor.
            """
            # Call the base class's invoke method
            return super().invoke(inputs, config)

        def invoke(self, inputs, config=None):
            """
            Runs the super().invoke function 5 times in parallel threads and 
            returns the result of the first one that arrives.
            The remaining threads are allowed to finish but their results are ignored.
            """            
            # We will run 5 concurrent tasks
            NUM_INVOCATIONS = 5
            
            # 1. Initialize ThreadPoolExecutor
            # max_workers=None uses the default, usually based on core count, but 5 is enough
            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_INVOCATIONS) as executor:
                
                # 2. Submit the task 5 times
                futures = [
                    executor.submit(self._run_super_invoke, inputs, config) 
                    for _ in range(NUM_INVOCATIONS)
                ]
                
                logging.info(f"Submitted {NUM_INVOCATIONS} tasks. Waiting for first completion...")
                
                # 3. Wait for the FIRST_COMPLETED future
                # This is the core logic for the "first result wins" pattern.
                done, not_done = concurrent.futures.wait(
                    futures, 
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                # 4. Handle the result
                if not done:
                    # Should not happen if timeout is not used, but good practice
                    raise TimeoutError("No invocation completed successfully.")
                
                # Get the single completed future (there will be exactly one in 'done')
                first_completed_future = done.pop()
                
                try:
                    # Retrieve the result, which raises any exception encountered in the thread
                    result = first_completed_future.result()
                    
                    logging.info(f"FIRST RESULT RECEIVED! Returning this result.")
                    
                    # 5. Clean up other pending futures
                    # Cancel the pending futures (note: this only prevents them from STARTING, 
                    # running threads cannot be stopped in Python, but we will return immediately).
                    for future in not_done:
                        future.cancel()
                        
                    # Return the fastest result
                    return result
                
                except Exception as e:
                    # Handle exceptions from the first completed thread
                    logging.error(f"Error in first completed thread: {e}")
                    # Re-raise the exception or handle fallback logic here
                    raise






if __name__ == "__main__":
    import os
    llm = LangchainApertus(api_key=os.environ.get("API_KEY"))
    print(llm.invoke("Hello world!"))