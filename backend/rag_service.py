import os
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from backend.config import INDEX_PATH
from backend.schemas import (
    EvaluationJudgment,
    EvaluationMetrics,
    RetrievedSource,
    SchemeAnswer,
    SearchResponse,
)


class RagService:
    """Retrieval and answer generation over the existing local FAISS index."""

    def __init__(self, index_path: Path = INDEX_PATH) -> None:
        if not (index_path / "index.faiss").is_file():
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. "
                "Build the index with `python -m backend.index_builder` first."
            )
        if not (index_path / "index.pkl").is_file():
            raise FileNotFoundError(
                f"FAISS metadata not found at {index_path}."
            )
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Add it to the project .env file."
            )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.vector_db = FAISS.load_local(
            str(index_path),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        self.retriever = self.vector_db.as_retriever(
            search_kwargs={"k": 4}
        )
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.relevance_chain = self._create_relevance_chain()

        self.answer_parser = JsonOutputParser(pydantic_object=SchemeAnswer)
        answer_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                (
                    "You are an expert assistant for Tamil Nadu agriculture "
                    "schemes. Answer strictly using the provided context. "
                    "If the context does not contain the answer, say so rather "
                    "than inventing details. Return valid JSON matching this "
                    "schema:\n{format_instructions}\n"
                    "Write every answer value in {language}. When the language "
                    "is Tamil, use clear, natural Tamil in Tamil script. Keep "
                    "scheme names, official names, abbreviations, and figures "
                    "accurate; include the English term in parentheses only "
                    "when it helps identify an official name."
                ),
            ),
            (
                "user",
                "Context:\n{context}\n\nUser question: {query}\n"
                "Respond in {language}.",
            ),
        ]).partial(format_instructions=self.answer_parser.get_format_instructions())
        self.answer_chain = answer_prompt | self.llm | self.answer_parser
        self.evaluation_parser = JsonOutputParser(
            pydantic_object=EvaluationJudgment
        )
        self.evaluation_chain = self._create_evaluation_chain()

    def _create_relevance_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                (
                    "You are a strict relevance grader. Output only YES if "
                    "the retrieved document is relevant to the question, "
                    "otherwise output NO."
                ),
            ),
            (
                "user",
                "Question: {query}\n\nRetrieved document:\n{document}",
            ),
        ])
        return prompt | self.llm

    def _create_evaluation_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                (
                    "Evaluate whether the generated answer is faithful to "
                    "the context and answers the query. Score faithfulness "
                    "and answer relevance from 0 to 100, where 100 is "
                    "excellent and 0 is completely unsupported or irrelevant. "
                    "Use the requested language for the reason, but return "
                    "the requested JSON structure containing both scores "
                    "and the reason.\n"
                    "{format_instructions}"
                ),
            ),
            (
                "user",
                (
                    "Query: {query}\nContext: {context}\nGenerated response: "
                    "{response}\nEvaluation (in {language}):"
                ),
            ),
        ])
        return prompt.partial(
            format_instructions=self.evaluation_parser.get_format_instructions()
        ) | self.llm | self.evaluation_parser

    def _retrieve_relevant_documents(
        self,
        query: str,
    ) -> tuple[list[Document], int, int]:
        retrieved_documents = self.retriever.invoke(query)
        relevant_documents = [
            document
            for document in retrieved_documents
            if self.relevance_chain.invoke(
                {"query": query, "document": document.page_content}
            ).content.strip().upper() == "YES"
        ]
        return (
            relevant_documents or retrieved_documents[:2],
            len(retrieved_documents),
            len(relevant_documents),
        )

    def search(
        self,
        query: str,
        language: str = "Tamil",
    ) -> SearchResponse:
        documents, retrieved_count, relevant_count = (
            self._retrieve_relevant_documents(query)
        )
        context = "\n\n".join(
            document.page_content for document in documents
        )
        answer = SchemeAnswer.model_validate(
            self.answer_chain.invoke({
                "context": context,
                "query": query,
                "language": language,
            })
        )
        judgment = EvaluationJudgment.model_validate(
            self.evaluation_chain.invoke({
                "query": query,
                "context": context,
                "response": answer.model_dump_json(),
                "language": language,
            })
        )
        retrieval_score = (
            round(100 * relevant_count / retrieved_count, 1)
            if retrieved_count
            else 0.0
        )
        overall_score = round(
            (
                judgment.faithfulness_score
                + judgment.answer_relevance_score
                + retrieval_score
            )
            / 3,
            1,
        )
        evaluation = EvaluationMetrics(
            **judgment.model_dump(),
            retrieval_relevance_score=retrieval_score,
            overall_score=overall_score,
            verdict=(
                "PASS"
                if min(
                    judgment.faithfulness_score,
                    judgment.answer_relevance_score,
                    retrieval_score,
                ) >= 70
                else "FAIL"
            ),
            relevant_document_count=relevant_count,
            retrieved_document_count=retrieved_count,
        )

        sources = [
            RetrievedSource(
                source=str(document.metadata.get("source", "Local document")),
                content=document.page_content,
            )
            for document in documents
        ]
        return SearchResponse(
            answer=answer,
            evaluation=evaluation,
            sources=sources,
        )
