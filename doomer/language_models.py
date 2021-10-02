from abc import ABC, abstractmethod
from typing import Any
from os import path
import json

import openai
from transformers import GPT2LMHeadModel, GPT2TokenizerFast, GPTNeoForCausalLM
import requests

from doomer.discord_utils import hundo_to_float
from doomer.settings import SETTINGS_DIR


class LanguageModel(ABC):
    def __init__(self, model_name: str, settings: dict) -> None:
        self.model_name = model_name
        self.settings = settings
        if path.exists(SETTINGS_DIR / f"{model_name}.json"):
            with open(SETTINGS_DIR / f"{model_name}.json", "r") as infile:
                self.settings.update(json.load(infile))

    @abstractmethod
    def completion_handler(self, prompt: str, **kwargs: Any):
        raise NotImplementedError

    @abstractmethod
    def parse_completion(self, completion: Any, **kwargs: Any) -> str:
        raise NotImplementedError


class GPT3LanguageModel(LanguageModel):
    def __init__(self, model_name: str) -> None:
        settings = {
            "temperature": 100,
            "frequency_penalty": 0,
            "presence_penalty": 50,
        }
        super().__init__(model_name, settings)

    def completion_handler(self, prompt: str, max_tokens: int, stop: list = None):
        return openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=max_tokens,
            frequency_penalty=hundo_to_float(self.settings["frequency_penalty"]),
            temperature=hundo_to_float(self.settings["temperature"]),
            presence_penalty=hundo_to_float(self.settings["presence_penalty"]),
            stop=stop,
        )

    def parse_completion(self, completion: Any, **kwargs: Any) -> str:
        text = completion.choices[0].text
        return text


class GPTJLanguageModel(LanguageModel):
    def __init__(self, model_name: str, api_key: str) -> None:
        settings = {"temperature": 100, "min_tokens": 20}
        self.api_url = "https://nlp-server.exafunction.com/text_completion"
        self.api_key = api_key
        super().__init__(model_name, settings)

    def completion_handler(self, prompt: str, max_tokens: int, **kwargs: any):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "prompt": prompt,
            "max_length": max_tokens,
            "min_length": self.settings["min_tokens"],
            "temperature": hundo_to_float(self.settings["temperature"]),
            "remove_input": "true",
        }
        response = requests.post(self.api_url, json=payload, headers=headers)
        return response.json()

    def parse_completion(self, completion: Any, **kwargs: Any) -> str:
        print(completion)
        text = completion["text"]
        return text


class GPT2TransformersLanguageModel(LanguageModel):
    def __init__(self, tokenizer_name: str, model_name: str) -> None:
        self._tokenizer = self.update_tokenizer(tokenizer_name)
        self._model = self.update_model(model_name)
        settings = {"temperature": 100, "top_p": 100, "top_k": 0, "max_length": 1024}
        super().__init__(model_name, settings)

    def update_tokenizer(self, tokenizer_name: str):
        return GPT2TokenizerFast.from_pretrained(tokenizer_name)

    def update_model(self, model_name: str):
        return GPT2LMHeadModel.from_pretrained(model_name)

    def completion_handler(self, prompt: str, max_tokens: int = None, **kwargs: Any):
        if not max_tokens:
            max_tokens = self.max_length

        inputs = self._tokenizer(prompt, return_tensors="pt")
        print(inputs)
        print(type(max_tokens))
        input_len = len(inputs["input_ids"][0])
        full_completion = self._model.generate(
            **inputs,
            do_sample=True,
            max_length=input_len + max_tokens,
            top_p=hundo_to_float(self.settings["top_p"]),
            top_k=hundo_to_float(self.settings["top_k"]),
        )
        completion = full_completion[0][input_len:]
        completion.resize_(1, len(completion))
        return completion

    def parse_completion(self, completion: Any, stop: list[str], **kwargs: Any) -> str:
        text = self._tokenizer.decode(completion[0], skip_special_tokens=True)
        if stop:
            for seq in stop:
                if seq in text:
                    return text.split(seq)[0]
        return text


class GPTNeoTransformersLanguageModel(LanguageModel):
    def __init__(self, tokenizer_name: str, model_name: str) -> None:
        self._tokenizer = self.update_tokenizer(tokenizer_name)
        self._model = self.update_model(model_name)
        settings = {"temperature": 100, "top_p": 100, "top_k": 0, "max_length": 1024}
        super().__init__(model_name, settings)

    def update_tokenizer(self, tokenizer_name: str):
        return GPT2TokenizerFast.from_pretrained(tokenizer_name)

    def update_model(self, model_name: str):
        return GPTNeoForCausalLM.from_pretrained(model_name)

    def completion_handler(self, prompt: str, max_tokens: int = None, **kwargs: Any):
        if not max_tokens:
            max_tokens = self.max_length

        inputs = self._tokenizer(prompt, return_tensors="pt")
        input_len = len(inputs["input_ids"][0])
        full_completion = self._model.generate(
            **inputs,
            do_sample=True,
            max_length=input_len + max_tokens,
            top_p=hundo_to_float(self.settings["top_p"]),
            top_k=hundo_to_float(self.settings["top_k"]),
        )
        completion = full_completion[0][input_len:]
        completion.resize_(1, len(completion))
        return completion

    def parse_completion(self, completion: Any, stop: list[str], **kwargs: Any) -> str:
        text = self._tokenizer.decode(completion[0], skip_special_tokens=True)
        if stop:
            for seq in stop:
                if seq in text:
                    return text.split(seq)[0]
        return text
