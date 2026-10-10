from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    language: Literal["Tamil", "English"] = "Tamil"

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question cannot be blank.")
        return value


class SchemeAnswer(BaseModel):
    scheme_name: str = Field(description="Name of the agriculture scheme")
    funding_pattern: str = Field(
        description="Subsidy details, funding pattern, or financial assistance"
    )
    eligibility: str = Field(
        description="Eligibility criteria for farmers"
    )
    how_to_apply: str = Field(
        description="Steps or official to contact to avail the scheme"
    )


class RetrievedSource(BaseModel):
    source: str
    content: str


class EvaluationJudgment(BaseModel):
    faithfulness_score: float = Field(ge=0, le=100)
    answer_relevance_score: float = Field(ge=0, le=100)
    reason: str


class EvaluationMetrics(EvaluationJudgment):
    retrieval_relevance_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)
    verdict: Literal["PASS", "FAIL"]
    relevant_document_count: int = Field(ge=0)
    retrieved_document_count: int = Field(ge=0)


class SearchResponse(BaseModel):
    answer: SchemeAnswer
    evaluation: EvaluationMetrics
    sources: list[RetrievedSource]
