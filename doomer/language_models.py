from abc import ABC, abstractmethod
from typing import Any

import openai
from transformers import (
    GPT2LMHeadModel,
    GPT2TokenizerFast,
)

from doomer.discord_utils import hundo_to_float


class LanguageModel(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def completion_handler(self, prompt: str, max_tokens: int, stop: list, **kwargs):
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
    def __init__(self, tokenizer_name: str, model_name: str, stop: list = None) -> None:
        self._tokenizer = self.update_tokenizer(tokenizer_name)
        self._model = self.update_model(model_name)
        self.max_length = 1024
        self.temperature = 100
        self.top_p = 100
        self.top_k = 0
        super().__init__()

    def update_tokenizer(self, tokenizer_name: str):
        return GPT2TokenizerFast.from_pretrained(tokenizer_name)

    def update_model(self, model_name: str):
        return GPT2LMHeadModel.from_pretrained(model_name)

    def completion_handler(self, prompt: str, max_tokens: int, stop: list = None):

        inputs = self._tokenizer(prompt, return_tensors="pt")
        input_len = len(inputs["input_ids"][0])
        full_completion = self._model.generate(
            **inputs,
            do_sample=True,
            max_length=max_tokens,
            top_p=hundo_to_float(self.top_p),
            top_k=hundo_to_float(self.top_k)
        )
        completion = full_completion[0][input_len:]
        completion.resize_(1, len(completion))
        return completion

    def parse_completion(self, completion: Any) -> str:
        return self._tokenizer.decode(completion[0], skip_special_tokens=True)
