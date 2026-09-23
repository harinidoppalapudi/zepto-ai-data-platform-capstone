import json
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END
from pydantic import ValidationError

from config import MOCK_LLM, TOP_K
from ingestion import PolicyIndexer
from prompts import PROMPT_TEMPLATE
from schemas import AskResponse
from langchain_groq import ChatGroq 


class GraphState(TypedDict, total=False):
    query: str
    intent: str
    retrieved: List[Dict[str, Any]]
    answer: str
    sources: List[str]
    confidence: float
    response: Dict[str, Any]


class SupportAssistantGraph:
    def __init__(self):
        self.indexer = PolicyIndexer()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node(
            "classify_intent",
            self.classify_intent,
        )

        workflow.add_node(
            "retrieve_and_answer",
            self.retrieve_and_answer,
        )

        workflow.add_node(
            "direct_answer",
            self.direct_answer,
        )

        workflow.add_edge(
            START,
            "classify_intent",
        )

        workflow.add_conditional_edges(
            "classify_intent",
            self.route_intent,
            {
                "policy_question": "retrieve_and_answer",
                "general_question": "direct_answer",
            },
        )

        workflow.add_edge(
            "retrieve_and_answer",
            END,
        )

        workflow.add_edge(
            "direct_answer",
            END,
        )

        return workflow.compile()

    # ---------------------------------------------------------
    # NODE 1
    # ---------------------------------------------------------

    def classify_intent(
        self,
        state: GraphState,
    ) -> GraphState:

        query = state["query"]
        lower_query = query.lower()

        policy_keywords = [
            "delivery",
            "return",
            "refund",
            "membership",
            "tracking",
            "cancel",
            "gift card",
            "support hours",
        ]

        if MOCK_LLM:
            is_policy = any(
                keyword in lower_query
                for keyword in policy_keywords
            )

            intent = (
                "policy_question"
                if is_policy
                else "general_question"
            )

        else:
            intent = self._classify_with_llm(query)

        return {
            **state,
            "intent": intent,
        }

    # ---------------------------------------------------------
    # CONDITIONAL ROUTER
    # ---------------------------------------------------------

    def route_intent(
        self,
        state: GraphState,
    ) -> str:

        return state["intent"]

    # ---------------------------------------------------------
    # NODE 2
    # ---------------------------------------------------------

    def retrieve_and_answer(
        self,
        state: GraphState,
    ) -> GraphState:

        query = state["query"]

        retrieved = self.indexer.retrieve(
            query=query,
            top_k=TOP_K,
        )

        if not retrieved:
            return {
                **state,
                "retrieved": [],
                "answer": "No relevant policy context was found.",
                "sources": [],
                "confidence": 0.0,
            }

        if MOCK_LLM:
            top_chunk_snippet = retrieved[0]["document"][:200]

            answer = (
                "Based on the retrieved context: "
                f"{top_chunk_snippet}"
            )

            sources = [
                item["id"]
                for item in retrieved
            ]

            confidence = 1.0

        else:
            answer, sources, confidence = (
                self._answer_with_llm(
                    query,
                    retrieved,
                )
            )

        return {
            **state,
            "retrieved": retrieved,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        }

    # ---------------------------------------------------------
    # NODE 3
    # ---------------------------------------------------------

    def direct_answer(
        self,
        state: GraphState,
    ) -> GraphState:

        query = state["query"]

        if MOCK_LLM:
            answer = (
                "I can only answer questions about Zepto "
                "policies right now."
            )

            sources = []
            confidence = 1.0

        else:
            answer, sources, confidence = (
                self._direct_llm_answer(query)
            )

        return {
            **state,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        }

    # ---------------------------------------------------------
    # OPTIONAL REAL LLM
    # ---------------------------------------------------------

    def _get_llm(self):
        from langchain_groq import ChatGroq

        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
        )

    def _classify_with_llm(
        self,
        query: str,
    ) -> str:

        llm = self._get_llm()

        prompt = f"""
Classify the following user query.

Return exactly one value:
policy_question
or
general_question

Query:
{query}
"""

        response = llm.invoke(prompt)

        result = response.content.strip().lower()

        if "policy_question" in result:
            return "policy_question"

        return "general_question"

    def _answer_with_llm(
        self,
        query: str,
        retrieved: List[Dict],
    ):

        context = "\n\n".join(
            [
                f"ID: {item['id']}\n{item['document']}"
                for item in retrieved
            ]
        )

        prompt = PROMPT_TEMPLATE.format(
            question=query,
            context=context,
        )

        return self._generate_valid_response(
            prompt,
            default_sources=[
                item["id"]
                for item in retrieved
            ],
        )

    def _direct_llm_answer(
        self,
        query: str,
    ):

        prompt = PROMPT_TEMPLATE.format(
            question=query,
            context="No policy context was retrieved.",
        )

        return self._generate_valid_response(
            prompt,
            default_sources=[],
        )

    def _generate_valid_response(
        self,
        prompt: str,
        default_sources: List[str],
    ):

        llm = self._get_llm()

        corrective_instruction = """
Your previous response did not match the required schema.

Return ONLY valid JSON with exactly:
{
  "answer": "string",
  "sources": ["string"],
  "confidence": 0.0
}

Do not include markdown fences.
"""

        last_error = None

        for attempt in range(3):
            try:
                current_prompt = prompt

                if attempt > 0:
                    current_prompt += (
                        "\n\n"
                        + corrective_instruction
                    )

                raw_response = llm.invoke(
                    current_prompt
                )

                content = raw_response.content.strip()

                # Remove accidental markdown fences.
                if content.startswith("```"):
                    content = content.replace(
                        "```json",
                        "",
                    ).replace(
                        "```",
                        "",
                    ).strip()

                parsed = json.loads(content)

                validated = AskResponse.model_validate(
                    parsed
                )

                return (
                    validated.answer,
                    validated.sources,
                    validated.confidence,
                )

            except (
                json.JSONDecodeError,
                ValidationError,
                Exception,
            ) as exc:

                last_error = exc

        return (
            "ERROR: Unable to produce a valid structured response.",
            default_sources,
            0.0,
        )

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def ask(
        self,
        query: str,
    ) -> AskResponse:

        state = self.graph.invoke(
            {
                "query": query,
            }
        )

        response = AskResponse(
            answer=state["answer"],
            sources=state.get("sources", []),
            confidence=state.get("confidence", 0.0),
        )

        return response