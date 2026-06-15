"""Resolve Modal vLLM serve URLs from LLM profiles."""

from __future__ import annotations

import asyncio

import modal

from llm_profiles import LlmProfile


async def get_serve_url(profile: LlmProfile) -> str:
    serve = modal.Function.from_name(profile.modal_app, "serve")
    return await serve.get_web_url.aio()


def get_serve_url_sync(profile: LlmProfile) -> str:
    return asyncio.run(get_serve_url(profile))
