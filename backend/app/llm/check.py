"""Manual check of the LLM setup. Each run of the default check uses ONE model request.

npm run llm:check    -> asks the model to answer "ok"
npm run llm:models   -> lists Gemini Flash models available to your key (no generation)
"""

import asyncio
import sys
import time

from google import genai

from app.core.config import get_settings
from app.llm.base import ChatMessage
from app.llm.errors import LLMError
from app.llm.factory import create_provider


async def check() -> int:
    settings = get_settings()
    try:
        provider = create_provider(settings)
    except LLMError as exc:
        print(f"Erro: {exc.message}")
        return 1
    print(f"Provedor: {provider.name} | modelo: {provider.model}")
    started = time.perf_counter()
    try:
        answer = await provider.generate(
            "Você é um verificador de conexão.",
            [ChatMessage(role="user", content="Responda apenas com a palavra: ok")],
        )
    except LLMError as exc:
        print(f"Erro: {exc.message}")
        return 1
    finally:
        await provider.aclose()
    print(f"Resposta: {answer.strip()} ({time.perf_counter() - started:.1f}s)")
    return 0


async def list_gemini_models() -> int:
    settings = get_settings()
    if not settings.gemini_api_key:
        print("Erro: preencha GEMINI_API_KEY no .env.")
        return 1
    client = genai.Client(api_key=settings.gemini_api_key)
    print("Modelos Flash com geração de texto disponíveis para a sua chave:")
    async for model in await client.aio.models.list():
        name = (model.name or "").removeprefix("models/")
        if "flash" in name and "generateContent" in (model.supported_actions or []):
            print(f"  {name}")
    return 0


def main() -> None:
    command = list_gemini_models if "--models" in sys.argv else check
    sys.exit(asyncio.run(command()))


if __name__ == "__main__":
    main()
