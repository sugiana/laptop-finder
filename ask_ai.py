import os
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import ollama
from dotenv import load_dotenv


def set_num_ctx(options: dict):
    # Maksimalkan kapasitas token
    client = ollama.Client(host=options["base_url"])
    info = client.show(options["model"])
    for key, val in info.modelinfo.items():
        if key.find("context_length") > -1:
            options["num_ctx"] = val
            break


def ollama_llm_class(options: dict) -> ChatOllama:
    url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    options["base_url"] = os.getenv("OLLAMA_LLM_URL", url)
    options["model"] = os.getenv("OLLAMA_LLM_MODEL", "gemma2")
    if os.getenv("OLLAMA_LLM_NUM_CTX"):
        options["num_ctx"] = int(os.getenv("OLLAMA_LLM_NUM_CTX"))
    else:  # Maksimalkan kapasitas token
        set_num_ctx(options)
    return ChatOllama


def openai_llm_class(options: dict) -> ChatOpenAI:
    url = os.getenv("OPENAI_URL", "https://api.openai.com/v1")
    options["base_url"] = os.getenv("OPENAI_LLM_URL", url)
    options["model"] = os.getenv("OPENAI_LLM_MODEL", "gpt-5.1")
    options["stream_usage"] = True
    return ChatOpenAI


def anthropic_llm_class(options: dict) -> ChatAnthropic:
    url = os.getenv("ANTHROPIC_URL", "https://api.anthropic.com")
    options["base_url"] = os.getenv("ANTHROPIC_LLM_URL", url)
    options["model"] = os.getenv("ANTHROPIC_LLM_MODEL", "claude-opus-4-8")
    options["stream_usage"] = True
    options["thinking"] = dict(type="disabled")
    return ChatAnthropic


def get_token(meta):
    if "token_usage" in meta:  # OpenAI invoke
        usage = meta["token_usage"]
        token_input = usage["prompt_tokens"]
        token_output = usage["completion_tokens"]
    elif "input_tokens" in meta:  # OpenAI stream
        token_input = meta["input_tokens"]
        token_output = meta["output_tokens"]
    elif "usage" in meta:  # Anthropic
        meta = meta["usage"]
        token_input = meta["input_tokens"]
        token_output = meta["output_tokens"]
    else:  # Ollama
        token_input = meta["prompt_eval_count"]
        token_output = meta["eval_count"]
    return dict(input=token_input, output=token_output)


class AIProvider:
    def __init__(self):
        load_dotenv()
        is_openai = os.getenv("OPENAI_API_KEY")
        if is_openai:
            llm_class_func = \
                os.getenv("OLLAMA_LLM_URL") and ollama_llm_class or \
                os.getenv("ANTHROPIC_LLM_URL") and anthropic_llm_class or \
                openai_llm_class
        else:
            llm_class_func = \
                os.getenv("ANTHROPIC_API_KEY") and anthropic_llm_class or \
                ollama_llm_class
        options = dict(temperature=0)
        llm_class = llm_class_func(options)
        print(f"LLM options: {options}")
        self.llm_client = llm_class(**options)

    def ask(self, prompt: str) -> str:
        messages = [HumanMessage(prompt)]
        response = self.llm_client.invoke(messages)
        answer = response.content
        meta = response.response_metadata
        token = get_token(meta)
        return dict(message=answer, token=token)
