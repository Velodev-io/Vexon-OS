import json
import logging
import asyncio
import redis
import os

from .base_agent import BaseAgent, AgentStatus
from llm.sdk import call_with_fallback
from prompts.researcher import RESEARCHER_SYSTEM_PROMPT, QUERY_OPTIMIZER_PROMPT, RESULT_EVALUATOR_PROMPT

import tools.web_search  # Ensure web_search is registered
from tools.registry import get_tool

logger = logging.getLogger(__name__)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0").replace("CERT_NONE", "none")


class ResearcherAgent(BaseAgent):
    """
    Specialized agent for web research tasks.
    Uses a focused ReAct loop: optimize query → search → evaluate → re-search if needed → synthesize.
    """

    def __init__(self, session_id: str, user_id: str, goal: str):
        super().__init__(session_id, user_id, goal)
        self.agent_type = "RESEARCHER"
        self.queries_used = []
        self.all_sources = []
        self.search_results = []

    async def _optimize_query(self, goal: str) -> str:
        """Use Groq to turn a verbose goal into a clean search query."""
        prompt = QUERY_OPTIMIZER_PROMPT.format(goal=goal)
        messages = [{"role": "user", "content": prompt}]
        try:
            result = await call_with_fallback(messages, stream=False)
            return result.strip().strip('"')
        except Exception:
            return goal  # Fallback to raw goal

    async def _evaluate_results(self, goal: str, query: str, results: str) -> tuple[bool, str]:
        """LLM judges whether search results are sufficient. Returns (sufficient, refined_query)."""
        prompt = RESULT_EVALUATOR_PROMPT.format(goal=goal, query=query, results=results[:2000])
        messages = [{"role": "user", "content": prompt}]
        try:
            verdict = await call_with_fallback(messages, stream=False)
            verdict = verdict.strip()
            if verdict.startswith("SUFFICIENT"):
                return True, ""
            elif verdict.startswith("INSUFFICIENT:"):
                refined = verdict.replace("INSUFFICIENT:", "").strip()
                return False, refined
            return True, ""
        except Exception:
            return True, ""  # Default to sufficient on error

    async def execute(self, intent: dict):
        goal = intent.get("description", self.goal)
        await self.load_memory()

        # ── AGENT_START ──────────────────────────────────────────────
        self.publish_event("AGENT_START", {"agent_type": self.agent_type, "goal": goal})
        self.set_status(AgentStatus.THINKING)

        # ── Step 1: Optimize the search query ────────────────────────
        self.publish_event("THINKING", {"message": "Generating optimized search query..."})
        query = await self._optimize_query(goal)
        logger.info(f"Researcher optimized query: '{query}'")

        web_search_tool = get_tool("web_search")
        if not web_search_tool:
            raise Exception("web_search tool is not registered. Please restart the Celery worker.")
            
        max_searches = 3
        search_count = 0

        while search_count < max_searches:
            search_count += 1
            self.queries_used.append(query)

            # ── TOOL_CALL ─────────────────────────────────────────────
            self.publish_event("TOOL_CALL", {"tool": "web_search", "input": {"query": query}})
            self.set_status(AgentStatus.TOOL_CALLING)

            # Execute the web search
            result = web_search_tool["func"](query=query)
            content = result.get("content", "")
            sources = result.get("sources", [])
            self.all_sources.extend(sources)
            self.search_results.append({"query": query, "content": content, "sources": sources})

            # ── TOOL_RESULT ───────────────────────────────────────────
            self.publish_event("TOOL_RESULT", {
                "tool": "web_search",
                "result": content[:500],  # Truncate for UI display
                "sources": sources
            })
            await self.save_memory(
                f"Search query: {query}\nSources: {', '.join(sources[:5])}\nContent: {content[:1000]}",
                "observation",
            )

            # ── Step 2: Evaluate quality ──────────────────────────────
            if search_count < max_searches:
                self.publish_event("THINKING", {"message": "Evaluating search results quality..."})
                sufficient, refined_query = await self._evaluate_results(goal, query, content)

                if sufficient:
                    logger.info("Researcher: results sufficient, proceeding to synthesis.")
                    break
                else:
                    logger.info(f"Researcher: results insufficient, refining query: '{refined_query}'")
                    query = refined_query if refined_query else f"{query} detailed explanation"
                    self.publish_event("THINKING", {"message": f"Refining search: {query}"})
            else:
                # Max searches reached
                break

        # ── Step 3: Synthesize with all gathered results ──────────────
        self.publish_event("THINKING", {"message": "Synthesizing answer from search results..."})
        self.set_status(AgentStatus.THINKING)

        # Build context from all searches
        context_parts = []
        for sr in self.search_results:
            context_parts.append(f"Search: {sr['query']}\nResults:\n{sr['content']}")
        full_context = "\n\n---\n\n".join(context_parts)

        synthesis_messages = [
            {
                "role": "user",
                "content": (
                    f"Original goal: {goal}\n\n"
                    f"Search Results:\n{full_context}\n\n"
                    f"Now write your structured final answer using the ## Summary, ## Key Findings, and ## Sources format."
                )
            }
        ]

        # ── STREAMING ─────────────────────────────────────────────────
        self.set_status(AgentStatus.STREAMING)
        tokens_used = 0

        try:
            stream = await call_with_fallback(
                synthesis_messages,
                system=RESEARCHER_SYSTEM_PROMPT,
                stream=True
            )
            final_text = ""
            async for token in stream:
                self.publish_event("stream_token", {"token": token})
                tokens_used += 1
                final_text += token
            await self.save_memory(final_text.strip(), "summary")
        except Exception as e:
            logger.error(f"ResearcherAgent synthesis failed: {e}")
            self.set_status(AgentStatus.ERROR)
            self.publish_event("error", {"message": str(e)})
            raise e

        # ── DONE ──────────────────────────────────────────────────────
        self.set_status(AgentStatus.DONE)
        self.publish_event("DONE", {
            "sources": list(dict.fromkeys(self.all_sources)),  # Deduplicated
            "queries_used": self.queries_used,
            "tokens_used": tokens_used
        })

        return {
            "result": "success",
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "sources": self.all_sources,
            "queries_used": self.queries_used
        }
