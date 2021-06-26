from abc import ABC, abstractmethod
from typing import Any

import openai
from transformers import AutoTokenizer, GPT2LMHeadModel

from doomer.discord_utils import hundo_to_float


class LanguageModel(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def completion_handler(self, prompt: str, max_tokens: int, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def parse_completion(self, completion: Any) -> str:
        raise NotImplementedError


class GPT3LanguageModel(LanguageModel):
    def __init__(self) -> None:
        self.temperature = 100
        self.frequency_penalty = 0
        self.presence_penalty = 50
        super().__init__()

    def completion_handler(self, prompt: str, max_tokens: int, stop: list = None):
        return openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=max_tokens,
            frequency_penalty=hundo_to_float(self.frequency_penalty),
            temperature=hundo_to_float(self.temperature),
            presence_penalty=hundo_to_float(self.presence_penalty),
            stop=stop,
        )

    def parse_completion(self, completion: Any) -> str:
        return completion.choices[0].text


class GPT2TransformersLanguageModel(LanguageModel):
    def __init__(self, tokenizer: AutoTokenizer, model: GPT2LMHeadModel) -> None:
        self.tokenizer = tokenizer
        self.model = model
        self.temperature = 100
        super().__init__()

    def completion_handler(self, prompt: str, max_tokens: int):
        prompt = prompt + self.tokenizer.eos_token
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        return self.model.generate(
            inputs,
            max_length=max_tokens,
            pad_token_id=self.tokenizer.eos_token_id,
            temperature=self.temperature,
        )

    def parse_completion(self, completion: Any) -> str:
        return self.tokenizer.decode(completion[0], skip_special_tokens=True)
