import pytest
from pydantic import BaseModel

from app.llm.base import ChatMessage
from app.llm.errors import InvalidModelOutput
from app.llm.fake import FakeProvider

MESSAGES = [ChatMessage(role="user", content="isso faz nota fiscal?")]


class Answer(BaseModel):
    verdict: str
    reason: str


async def test_valid_json_becomes_the_schema_object() -> None:
    provider = FakeProvider(['{"verdict": "não", "reason": "não encontrei no material"}'])

    answer = await provider.generate_json("sys", MESSAGES, Answer)

    assert answer == Answer(verdict="não", reason="não encontrei no material")


@pytest.mark.parametrize("output", ['{"verdict": "sim"}', "not json", ""])
async def test_invalid_json_raises_invalid_model_output(output: str) -> None:
    provider = FakeProvider([output])

    with pytest.raises(InvalidModelOutput):
        await provider.generate_json("sys", MESSAGES, Answer)
