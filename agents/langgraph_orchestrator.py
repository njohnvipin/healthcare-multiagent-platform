"""
langgraph_orchestrator.py

LangGraph orchestration layer for the Healthcare Multi-Agent platform.

Flow:
    START
      ↓
    route_request
      ↓
    Selected specialist agents run
      ↓
    combine_results
      ↓
    END
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from agents.authorization_agent import AuthorizationAgent
from agents.billing_agent import BillingAgent
from agents.claims_agent import ClaimsAgent
from agents.policy_agent import PolicyAgent
from services.llm_service import safe_llm_response


class HealthcareState(TypedDict):
    """
    Shared state passed between LangGraph nodes.

    Annotated with operator.add means agent_results and sources
    produced by multiple agents are combined instead of overwritten.
    """

    question: str
    routed_to: list[str]

    agent_results: Annotated[list[dict], operator.add]
    sources: Annotated[list[dict], operator.add]

    answer: str


class LangGraphHealthcareOrchestrator:
    """
    Coordinates the specialist healthcare agents through LangGraph.
    """

    def __init__(self) -> None:
        self.policy_agent = PolicyAgent()
        self.claims_agent = ClaimsAgent()
        self.authorization_agent = AuthorizationAgent()
        self.billing_agent = BillingAgent()

        self.graph = self._build_graph()

    # -----------------------------------------------------------------
    # Intent detection
    # -----------------------------------------------------------------

    @staticmethod
    def detect_intents(question: str) -> list[str]:
        """
        Detect which specialist agents are needed.

        This first LangGraph version preserves the existing keyword
        routing logic so students can focus on graph orchestration.

        Later, this can be replaced with LLM-based structured routing.
        """
        normalized_question = question.lower()
        intents: list[str] = []

        policy_terms = [
            "covered",
            "coverage",
            "policy",
            "benefit",
            "deductible",
            "coinsurance",
            "excluded",
            "mri",
        ]

        claims_terms = [
            "claim",
            "denied",
            "denial",
            "eob",
            "status",
            "paid",
            "appeal",
        ]

        authorization_terms = [
            "prior authorization",
            "authorization",
            "approval",
            "medical necessity",
            "preauth",
            "pa",
        ]

        billing_terms = [
            "pay",
            "cost",
            "owe",
            "responsibility",
            "premium",
            "out-of-pocket",
            "out of pocket",
            "deductible",
            "coinsurance",
        ]

        if any(term in normalized_question for term in policy_terms):
            intents.append("policy")

        if any(term in normalized_question for term in claims_terms):
            intents.append("claims")

        if any(
            term in normalized_question
            for term in authorization_terms
        ):
            intents.append("authorization")

        if any(term in normalized_question for term in billing_terms):
            intents.append("billing")

        # Safe fallback for general insurance questions.
        if not intents:
            intents.append("policy")

        # Remove duplicates while preserving order.
        return list(dict.fromkeys(intents))

    # -----------------------------------------------------------------
    # LangGraph nodes
    # -----------------------------------------------------------------

    def route_request_node(
        self,
        state: HealthcareState,
    ) -> dict:
        """
        Analyze the question and update the graph state with intents.
        """
        intents = self.detect_intents(state["question"])

        print(
            "[LangGraph Router] "
            f"Question routed to: {intents}"
        )

        return {
            "routed_to": intents,
        }

    @staticmethod
    def select_agent_nodes(
        state: HealthcareState,
    ) -> list[str]:
        """
        Conditional-edge function.

        Returns the names of all specialist nodes that should run.
        """
        node_map = {
            "policy": "policy_agent",
            "claims": "claims_agent",
            "authorization": "authorization_agent",
            "billing": "billing_agent",
        }

        selected_nodes = [
            node_map[intent]
            for intent in state["routed_to"]
            if intent in node_map
        ]

        return selected_nodes or ["policy_agent"]

    def policy_agent_node(
        self,
        state: HealthcareState,
    ) -> dict:
        """Run the existing PolicyAgent."""
        result = self.policy_agent.run(state["question"])

        print("[LangGraph] Policy Agent completed")

        return {
            "agent_results": [result],
            "sources": result.get("sources", []),
        }

    def claims_agent_node(
        self,
        state: HealthcareState,
    ) -> dict:
        """Run the existing ClaimsAgent."""
        result = self.claims_agent.run(state["question"])

        print("[LangGraph] Claims Agent completed")

        return {
            "agent_results": [result],
            "sources": result.get("sources", []),
        }

    def authorization_agent_node(
        self,
        state: HealthcareState,
    ) -> dict:
        """Run the existing AuthorizationAgent."""
        result = self.authorization_agent.run(
            state["question"]
        )

        print("[LangGraph] Authorization Agent completed")

        return {
            "agent_results": [result],
            "sources": result.get("sources", []),
        }

    def billing_agent_node(
        self,
        state: HealthcareState,
    ) -> dict:
        """Run the existing BillingAgent."""
        result = self.billing_agent.run(state["question"])

        print("[LangGraph] Billing Agent completed")

        return {
            "agent_results": [result],
            "sources": result.get("sources", []),
        }

    def combine_results_node(
        self,
        state: HealthcareState,
    ) -> dict:
        """
        Combine specialist outputs into one user-facing answer.
        """
        agent_results = state.get("agent_results", [])

        if not agent_results:
            return {
                "answer": (
                    "No specialist agent produced a response."
                )
            }

        combined_outputs = "\n\n".join(
            (
                f"{result.get('agent', 'Specialist Agent')}:\n"
                f"{result.get('answer', '')}"
            )
            for result in agent_results
        )

        fallback = combined_outputs

        prompt = f"""
You are the final response formatter for a healthcare insurance
multi-agent platform.

Combine the specialist agent outputs into one clear and accurate
answer for the user.

Rules:
1. Do not add facts not present in the specialist outputs.
2. Do not invent policy, claim, authorization, or billing details.
3. Keep the response easy to understand.
4. Use only the relevant headings:
   - Coverage
   - Prior Authorization
   - Claims
   - Cost Estimate
   - Next Steps
5. Avoid repeating the same information.
6. Clearly state when information is unavailable.

User Question:
{state["question"]}

Agents Invoked:
{state["routed_to"]}

Specialist Agent Outputs:
{combined_outputs}

Final Combined Answer:
"""

        answer = safe_llm_response(
            prompt=prompt,
            fallback=fallback,
        )

        print("[LangGraph] Final response generated")

        return {
            "answer": answer,
        }

    # -----------------------------------------------------------------
    # Graph construction
    # -----------------------------------------------------------------

    def _build_graph(self):
        """
        Construct and compile the LangGraph workflow.
        """
        workflow = StateGraph(HealthcareState)

        workflow.add_node(
            "route_request",
            self.route_request_node,
        )

        workflow.add_node(
            "policy_agent",
            self.policy_agent_node,
        )

        workflow.add_node(
            "claims_agent",
            self.claims_agent_node,
        )

        workflow.add_node(
            "authorization_agent",
            self.authorization_agent_node,
        )

        workflow.add_node(
            "billing_agent",
            self.billing_agent_node,
        )

        workflow.add_node(
            "combine_results",
            self.combine_results_node,
        )

        # Start with the router.
        workflow.add_edge(
            START,
            "route_request",
        )

        # Dynamically select one or more specialist agents.
        workflow.add_conditional_edges(
            "route_request",
            self.select_agent_nodes,
            {
                "policy_agent": "policy_agent",
                "claims_agent": "claims_agent",
                "authorization_agent": (
                    "authorization_agent"
                ),
                "billing_agent": "billing_agent",
            },
        )

        # Every selected specialist feeds the final combiner.
        workflow.add_edge(
            "policy_agent",
            "combine_results",
        )

        workflow.add_edge(
            "claims_agent",
            "combine_results",
        )

        workflow.add_edge(
            "authorization_agent",
            "combine_results",
        )

        workflow.add_edge(
            "billing_agent",
            "combine_results",
        )

        workflow.add_edge(
            "combine_results",
            END,
        )

        return workflow.compile()

    # -----------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------

    def run(self, question: str) -> dict:
        """
        Invoke the compiled LangGraph workflow.
        """
        cleaned_question = question.strip()

        if not cleaned_question:
            raise ValueError("Question cannot be empty.")

        initial_state: HealthcareState = {
            "question": cleaned_question,
            "routed_to": [],
            "agent_results": [],
            "sources": [],
            "answer": "",
        }

        result = self.graph.invoke(initial_state)

        return {
            "question": result["question"],
            "routed_to": result["routed_to"],
            "agent_results": result["agent_results"],
            "answer": result["answer"],
            "sources": result["sources"],
            "orchestration": "LangGraph StateGraph",
        }