import json
from litellm import (
    completion,
    token_counter,
    completion_cost, 
    get_max_tokens,
)
from services.assets import USER_MESSAGE, MODELS_USED
from functions.api_management import get_api_key
import os


def call_llm_model(
    data,
    response_format,
    model,
    system_message,
    extra_user_instruction="",
    max_tokens=None,
    use_model_max_tokens_if_none=False,
):
    """
    Calls an LLM via LiteLLM and returns:
      - parsed_response (str or dict, depending on your response_format),
      - token_counts ({"input_tokens": int, "output_tokens": int}),
      - cost (float).

    It also checks the maximum allowable tokens for the chosen model via
    'get_max_tokens' and ensures the 'max_tokens' parameter doesn't exceed that.

    Parameters:
        data (str): Additional data to append to the user message.
        response_format: Desired response format (a dict or Pydantic model).
        model (str): Model identifier (e.g., "gpt-3.5-turbo", "gemini/gemini-1.5-pro", etc.).
        system_message (str): System prompt to prime the assistant.
        extra_user_instruction (str, optional): Extra instructions for the user message.
        max_tokens (int, optional): The maximum number of tokens to allow in the completion.
        use_model_max_tokens_if_none (bool, optional): If True and max_tokens is not provided,
            the function will automatically use the model's maximum context size.

    Returns:
        tuple: (parsed_response, token_counts, cost)
            - parsed_response: The parsed output (could be text or a structured object).
            - token_counts: A dict with "input_tokens" and "output_tokens".
            - cost: The overall cost (in USD) for the API call.
    """
    # 1) Retrieve the single API key name for this model from MODELS_USED
    env_var_name = list(MODELS_USED[model])[0]  # e.g., "GEMINI_API_KEY"
    # 2) Retrieve the actual key from session or OS
    env_value = get_api_key(model)
    print("env variable is:" + env_value)
    # 3) Set it in os.environ so that litellm / underlying client sees it
    if env_value:
        os.environ[env_var_name] = env_value

    model_max_tokens = get_max_tokens(model)
    if max_tokens is not None:
        max_tokens = min(max_tokens, model_max_tokens) - 100
    elif use_model_max_tokens_if_none:
        max_tokens = model_max_tokens - 100

    # Build the conversation messages
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{USER_MESSAGE} {extra_user_instruction} {data}"},
    ]

    # Prepare parameters for the LiteLLM completion call
    params = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
    }
    if max_tokens is not None:
        params["max_tokens"] = max_tokens

    # Call the LLM using LiteLLM
    response = completion(**params)

    # Extract the parsed response
    parsed_response = response.choices[0].message.content

    # Calculate token counts:
    #   - input_tokens: from the user/system prompt
    #   - output_tokens: from the returned content
    input_tokens = token_counter(model=model, messages=messages)

    # Make sure we convert the parsed response to a string for counting
    output_text = (
        parsed_response
        if isinstance(parsed_response, str)
        else json.dumps(parsed_response)
    )
    output_tokens = token_counter(model=model, text=output_text)

    token_counts = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }

    # Calculate the total cost for the request
    cost = completion_cost(completion_response=response)

    return parsed_response, token_counts, cost
