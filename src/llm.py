import yaml
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import LlamaCpp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')


def init_llm_gemini(api_key: str, model_name: str = "models/gemini-2.0-flash", **kwargs) -> ChatGoogleGenerativeAI:
    """
    Initialize and return a ChatGoogleGenerativeAI LLM with explicit default handling.

    Args:
        api_key (str): The API key for Google Generative AI.
        model_name (str): The name of the model to use. Defaults to "models/gemini-2.0-flash".
    """
    # Extract parameters with defaults
    temperature = kwargs.get("temperature", 0.9)
    max_tokens = kwargs.get("max_tokens", 8192)
    logging.info(f"Initializing Online LLM with model: {model_name}...")

    return ChatGoogleGenerativeAI(
        model=model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )

def init_llm_local(model_path: str = "models/gemma-3-12b-it-Q4_K_M.gguf", **kwargs) -> LlamaCpp:
    """
    Initialize and return a LlamaCpp LLM with explicit default handling.

    Args:
        model_path (str): The path to the LlamaCpp model file. Defaults to "models/gemma-3-12b-it-Q4_K_M.gguf".
        **kwargs: Arbitrary keyword arguments for LlamaCpp initialization,
                  including:
                    - temperature (float): Sampling temperature (defaults to 0.9).
                    - max_tokens (int): Maximum number of tokens to generate (defaults to 2048).
                    - n_ctx (int): Text context window size (defaults to 8192).
                    - n_batch (int): Batch size for prompt processing (defaults to 16).
                    - n_gpu_layers (int): Number of layers to offload to GPU (defaults to -1).
                    - verbose (bool): Whether to print verbose output (defaults to False).

    Returns:
        LlamaCpp: An initialized LlamaCpp language model instance.
    """
    # Extract parameters with defaults
    temperature = kwargs.get("temperature", 0.9)
    max_tokens = kwargs.get("max_tokens", 8192)
    n_ctx = kwargs.get("n_ctx", 32768)
    n_batch = kwargs.get("n_batch", 16)
    n_gpu_layers = kwargs.get("n_gpu_layers", -1)
    # n_threads = kwargs.get("n_threads", 8)
    verbose = kwargs.get("verbose", False)
    logging.info(f"Initializing LlamaCpp LLM with model: {model_path}...")

    return LlamaCpp(model_path=model_path, temperature=temperature, max_tokens=max_tokens,
                    n_ctx=n_ctx, n_batch=n_batch, n_gpu_layers=n_gpu_layers, verbose=verbose)


if __name__ == "__main__":
    llm = init_llm_local()
    print(llm.invoke("Please introduce agent powered by LangChain."))