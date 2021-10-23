import openai
import pytest

from doomer.language_models import (
    GPT2TransformersLanguageModel,
    GPTJLanguageModel,
    GPT3LanguageModel,
)
from doomer import settings


def test_gpt2_completion():
    model_name = "gpt2"
    model = GPT2TransformersLanguageModel(
        tokenizer_name=model_name, model_name=model_name
    )
    assert model._model is None
    assert model._tokenizer is None
    prompt = "Hello I am "
    completion = model.completion_handler(prompt, max_tokens=50)
    assert completion is not None
    assert model._model is not None
    assert model._tokenizer is not None
    response = model.parse_completion(completion)
    assert response is not None
    assert type(response) is str


@pytest.mark.gptj
def test_gptj_completion():
    model_name = "gpt2"
    api_key = settings.EXAFUNCTION_API_KEY
    assert api_key is not None
    model = GPTJLanguageModel(model_name=model_name, api_key=api_key)
    prompt = "Hello I am "
    completion = model.completion_handler(prompt, max_tokens=50)
    assert completion is not None
    response = model.parse_completion(completion)
    assert response is not None
    assert type(response) is str


@pytest.mark.gpt3
def test_gpt3_completion():
    model_name = "gpt2"
    api_key = settings.OPENAI_API_KEY
    assert api_key is not None
    openai.api_key = settings.OPENAI_API_KEY
    model = GPT3LanguageModel(model_name=model_name)
    prompt = "Hello I am "
    completion = model.completion_handler(prompt, max_tokens=50)
    assert completion is not None
    response = model.parse_completion(completion)
    assert response is not None
    assert type(response) is str
