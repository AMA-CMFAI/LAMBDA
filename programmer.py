import openai
from prompt_engineering.prompts import PROGRAMMER_PROMPT
from knw_in import retrieval_knowledge
import os
import traceback
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class Programmer:

    def __init__(self, api_key, model="gpt-4o-mini", base_url=None):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.messages = []
        self.function_repository = {}
        self.last_snaps = None

    def add_functions(self, function_lib: dict) -> None:
        self.function_repository = function_lib

    def _call_chat_model(self, functions=None, include_functions=False, retrieval=False):
        if retrieval:
            snaps = retrieval_knowledge(self.messages[-1]["content"])
            if snaps:
                self.last_snaps = snaps
                self.messages[-1]["content"] += snaps
            else:
                self.last_snaps = None

        params = {
            "model": self.model,
            "messages": self.messages,
        }

        if include_functions:
            params['functions'] = functions
            params['function_call'] = "auto"

        try:
            response = self.client.chat.completions.create(**params)
            usage = response.usage
            print(f"======Prompt Tokens: {usage.prompt_tokens}======Completion Tokens: {usage.completion_tokens}=======Total Tokens: {usage.total_tokens}")
            return response
        except Exception as e:
            print(f"Error calling chat model: {e}")
            return None

    def _call_chat_model_streaming(self, functions=None, include_functions=False, retrieval=False, kernel=None):
        temp = self.messages[-1]["content"]
        if retrieval:
            snaps = retrieval_knowledge(self.messages[-1]["content"], kernel=kernel)
            if snaps:
                for chunk in snaps:
                    yield chunk
                self.last_snaps = snaps
                self.messages[-1]["content"] += snaps
            else:
                self.last_snaps = None

        params = {
            "model": self.model,
            "messages": self.messages,
            "stream": True
        }

        if include_functions:
            params['functions'] = functions
            params['function_call'] = "auto"

        try:
            stream = self.client.chat.completions.create(**params)
            self.messages[-1]["content"] = temp
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices[0].delta.content is not None:
                    chunk_message = chunk.choices[0].delta.content
                    yield chunk_message
        except Exception as e:
            print(f"Error calling chat model: {e}")
            traceback.print_exc()
            return None
    def clear(self):
        self.messages = [
            {
                "role": "system",
                "content": PROGRAMMER_PROMPT
            }
        ]
        self.function_repository = {}




