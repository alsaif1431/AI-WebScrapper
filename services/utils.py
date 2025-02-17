from datetime import datetime
import re
# =============================================================================
# 6) GENERATE UNIQUE FOLDER NAME
# =============================================================================
def generate_unique_name(url: str) -> str:
    """
    Generate a unique name for the folder based on the URL.
    """
    timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S_%f')
    domain = re.sub(r'\W+', '_', url.split('//')[-1].split('/')[0])
    return f"{domain}_{timestamp}"

# def calculate_price(token_counts, model):
#     """
#     Calculate the cost based on input/output tokens and model pricing.
#     """
#     input_token_count = token_counts.get("input_tokens", 0)
#     output_token_count = token_counts.get("output_tokens", 0)

#     input_cost = input_token_count * PRICING[model]["input"]
#     output_cost = output_token_count * PRICING[model]["output"]
#     total_cost = input_cost + output_cost

#     return input_token_count, output_token_count, total_cost