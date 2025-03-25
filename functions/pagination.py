# pagination.py

import json
from typing import List, Dict
from services.assets import PROMPT_PAGINATION
from functions.markdown import read_raw_data
from functions.api_management import get_supabase_client
from pydantic import BaseModel, Field
from typing import List
from pydantic import create_model
from functions.llm_calls import (call_llm_model)

supabase = get_supabase_client()


class PaginationModel(BaseModel):
    page_urls: List[str]


def get_pagination_response_format():
    return PaginationModel


def create_dynamic_listing_model(field_names: List[str]):
    field_definitions = {field: (str, ...) for field in field_names}
    return create_model('DynamicListingModel', **field_definitions) 

def build_pagination_prompt(indications: str, url: str) -> str:
    # Base prompt
    prompt = PROMPT_PAGINATION + f"\nThe page being analyzed is: {url}\n"

    if indications.strip():
        prompt += (
            "These are the user's indications. Pay attention:\n"
            f"{indications}\n\n"
        )
    else:
        prompt += (
            "No special user indications. Just apply the pagination logic.\n\n"
        )
    # Finally append the actual markdown data
    return prompt


def save_pagination_data(unique_name: str, pagination_data):
       # if it's a pydantic object, convert to dict
    if hasattr(pagination_data, "dict"):
        pagination_data = pagination_data.dict()
    
    # parse if string
    if isinstance(pagination_data, str):
        try:
            pagination_data = json.loads(pagination_data)
        except json.JSONDecodeError:
            pagination_data = {"raw_text": pagination_data}

    supabase.table("scraped_data").update({
        "pagination_data": pagination_data
    }).eq("unique_name", unique_name).execute()
    MAGENTA = "\033[35m"
    RESET = "\033[0m" 
    print(f"{MAGENTA}INFO:Pagination data saved for {unique_name}{RESET}")

def paginate_urls(unique_names: List[str], selected_model: str, indication: str, urls:List[str]):
    """
    For each unique_name, read raw_data, detect pagination, save results,
    accumulate cost usage, and return a final summary.
    """
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0
    pagination_results = []

    for uniq,current_url in zip(unique_names, urls):
        raw_data = read_raw_data(uniq)
        if not raw_data:
            print(f"No raw_data found for {uniq}, skipping pagination.")
            continue
        response_schema=get_pagination_response_format()
        full_indication=build_pagination_prompt(indication,current_url)
        pag_data, token_counts, cost = call_llm_model(raw_data, response_schema,selected_model, full_indication)

        # store
        save_pagination_data(uniq, pag_data)

        # accumulate cost
        
        total_input_tokens += token_counts["input_tokens"]
        total_output_tokens += token_counts["output_tokens"]
        total_cost += cost

        pagination_results.append({"unique_name": uniq,"pagination_data": pag_data})

    return total_input_tokens, total_output_tokens, total_cost, pagination_results
