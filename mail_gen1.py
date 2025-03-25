import multiprocessing
from huggingface_hub import hf_hub_download
from langchain_community.chat_models import ChatLlamaCpp

# Model configuration
model_name = "lmstudio-community/Llama-3.2-3B-Instruct-GGUF"
model_file = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
model_path = hf_hub_download(model_name, filename=model_file)

# LLM initialization with optimized parameters
llm = ChatLlamaCpp(
    temperature=0.7,
    model_path=model_path,
    n_ctx=4096,
    n_gpu_layers=6,
    n_batch=128,
    max_tokens=1024,
    n_threads=multiprocessing.cpu_count() - 1,
    repeat_penalty=1.2,
    top_p=0.9,
    verbose=True,
)

def generate_email(user_input, user_context=None):
    """
    Generate a personalized email based on minimal user input
    
    Args:
        user_input (str): The user's request, which could be as simple as "Write an email to Tom about dinner"
        user_context (dict, optional): Additional context that might be available from the conversation
                                      or user preferences (completely optional)
    
    Returns:
        str: Generated email text
    """
    # Extract available context if provided
    context = {}
    if user_context:
        context = {
            "recipient": user_context.get("recipient", None),
            "tone": user_context.get("tone", None),
            "style": user_context.get("style", None),
            "sender_name": user_context.get("sender_name", None),
            "additional_info": user_context.get("additional_info", None),
        }
    
    # Construct a system prompt that works with minimal information
    system_prompt = """You are an expert email writer who crafts perfectly tailored messages based on even minimal instructions.

Your goal is to create appropriate emails that match the context and purpose implied by the user's request.

If the user specifies a tone (formal, casual, friendly, professional, urgent) or style (concise, detailed, persuasive, enthusiastic), follow it precisely.
If not explicitly mentioned, infer an appropriate tone and style from the context.

Always include:
1. Appropriate greeting
2. Clear body with purpose of the email
3. Appropriate closing
4. Sender's name (if known)

Generate only the email content without explanations unless specifically requested.
"""

    # Create user prompt that incorporates any available context
    user_prompt = f"Write an email based on this request: {user_input}"
    
    # Add any available context as hints
    context_hints = []
    if context.get("recipient"):
        context_hints.append(f"Recipient: {context['recipient']}")
    if context.get("tone"):
        context_hints.append(f"Use a {context['tone']} tone")
    if context.get("style"):
        context_hints.append(f"Write in a {context['style']} style")
    if context.get("additional_info"):
        context_hints.append(f"Include these details: {context['additional_info']}")
    if context.get("sender_name"):
        context_hints.append(f"Sign as: {context['sender_name']}")
    
    # Add context hints if available
    if context_hints:
        user_prompt += "\n\nAdditional context:\n" + "\n".join(context_hints)
    
    # Generate the email
    messages = [
        ("system", system_prompt),
        ("human", user_prompt),
    ]
    
    response = llm.invoke(messages)
    return response.content

# Example usage in an assistant context
def ai_assistant_email(user_request):
    """
    Function to integrate with your AI assistant
    
    Args:
        user_request (str): User's email request
        
    Returns:
        str: Generated email or follow-up question if needed
    """
    # Simple parsing to extract potential context
    # In a real assistant, you might have more sophisticated NLU
    context = {}
    
    # Example of very simple extraction - your actual assistant would likely use more advanced NLP
    if "formal" in user_request.lower():
        context["tone"] = "formal"
    elif "casual" in user_request.lower():
        context["tone"] = "casual"
    
    # Generate email based on available information
    email = generate_email(user_request, context)
    return email

# Example of how this would work in your assistant
if __name__ == "__main__":
    # Minimal request example
    print("MINIMAL REQUEST:")
    print(ai_assistant_email("Invite Tom to dinner"))
    print("\n" + "="*50 + "\n")
    
    # More detailed request example
    print("DETAILED REQUEST:")
    print(ai_assistant_email("Write a formal email to the client about the project delay"))