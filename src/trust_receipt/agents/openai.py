"""LangChain/OpenAI adapter isolated from domain and deterministic verification modules."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from trust_receipt.agents.ports import StructuredArtifact


def ChatOpenAI(**kwargs):
    """Load the vendor SDK only when a live model adapter is constructed."""
    from langchain_openai import ChatOpenAI as model_class

    return model_class(**kwargs)


class OpenAIStructuredOutputAdapter:
    """Invoke one fixed model with a response schema and no application tools."""

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        timeout_seconds: float = 30,
        max_retries: int = 2,
        base_url: str | None = None,
        use_responses_api: bool | None = None,
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name must be fixed and non-empty")
        self._model = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            timeout=timeout_seconds,
            max_retries=max_retries,
            base_url=base_url,
            use_responses_api=use_responses_api,
        )

    def generate(
        self,
        *,
        schema: type[StructuredArtifact],
        system_prompt: str,
        payload: Mapping[str, Any],
    ) -> StructuredArtifact:
        structured = self._model.with_structured_output(schema, method="json_schema", strict=True)
        response = structured.invoke(
            [
                ("system", system_prompt),
                (
                    "human",
                    "INPUT_JSON:\n"
                    + json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                ),
            ]
        )
        if isinstance(response, schema):
            return response
        if isinstance(response, BaseModel):
            return schema.model_validate(response.model_dump(mode="json"))
        return schema.model_validate(response)


class DeepSeekStructuredOutputAdapter(OpenAIStructuredOutputAdapter):
    """DeepSeek adapter using its official OpenAI-compatible Responses endpoint."""

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        timeout_seconds: float = 30,
        max_retries: int = 2,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model_name=model_name,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            base_url="https://api.deepseek.com",
            use_responses_api=True,
        )
