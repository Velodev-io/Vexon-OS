import uuid
import json
import logging
from enum import Enum
import redis
import os

logger = logging.getLogger(__name__)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0").replace("CERT_NONE", "none")

from llm.sdk import call_with_fallback

class AgentStatus(str, Enum):
    SPAWNED = "spawned"
    MEMORY_LOADED = "memory_loaded"
    THINKING = "thinking"
    TOOL_CALLING = "tool_calling"
    STREAMING = "streaming"
    DONE = "done"
    ERROR = "error"

class BaseAgent:
    def __init__(self, session_id: str, user_id: str, goal: str):
        self.agent_id = str(uuid.uuid4())
        self.session_id = session_id
        self.user_id = user_id
        self.goal = goal
        self.status = AgentStatus.SPAWNED
        self.trace = []
        self.redis_client = redis.from_url(redis_url)

    def set_status(self, new_status: AgentStatus):
        self.status = new_status
        self.publish_event("status_update", {"status": new_status.value})

    def load_memory(self):
        self.set_status(AgentStatus.MEMORY_LOADED)
        return []

    async def execute(self, intent: dict):
        import tools.web_search
        import tools.code_execute
        import tools.memory_tool
        from tools.registry import list_tools, get_tool
        
        self.set_status(AgentStatus.THINKING)
        self.trace.append({"step": "thinking", "content": f"Analyzing goal: {self.goal}"})
        
        available_tools = list_tools()
        tools_str = json.dumps(available_tools, indent=2)
        
        system_prompt = f"""You are a kernel agent in Vexon OS.
Your current goal is: {self.goal}

You have access to the following tools:
{tools_str}

To use a tool, your response MUST start exactly with the <tool> tag, followed by a JSON object, and end with </tool>.
Example:
<tool>
{{"name": "web_search", "input": {{"query": "latest AI news"}}}}
</tool>

If you use a tool, you will receive the result in the next message, and you can then decide to use another tool or provide the final answer.
If you do not need a tool, simply write your final response directly (do not use the <tool> tag).
Provide a helpful, concise, and technical final response.
"""
        
        messages = [
            {"role": "user", "content": intent.get("description", self.goal)}
        ]
        
        max_iterations = 5
        for i in range(max_iterations):
            self.set_status(AgentStatus.THINKING)
            
            try:
                stream = await call_with_fallback(messages, system=system_prompt, stream=True)
                
                buffer = ""
                is_tool = False
                tool_json_str = ""
                has_started_streaming = False
                
                async for token in stream:
                    if not is_tool and len(buffer) < 6:
                        buffer += token
                        if len(buffer) >= 6:
                            if buffer.startswith("<tool>"):
                                is_tool = True
                                tool_json_str = buffer[6:]
                            else:
                                if not has_started_streaming:
                                    self.set_status(AgentStatus.STREAMING)
                                    has_started_streaming = True
                                self.publish_event("stream_token", {"token": buffer})
                    elif is_tool:
                        tool_json_str += token
                    else:
                        if not has_started_streaming:
                            self.set_status(AgentStatus.STREAMING)
                            has_started_streaming = True
                        self.publish_event("stream_token", {"token": token})
                
                if is_tool:
                    # Parse tool call
                    tool_json_str = tool_json_str.replace("</tool>", "").strip()
                    try:
                        tool_call = json.loads(tool_json_str)
                        tool_name = tool_call.get("name")
                        tool_input = tool_call.get("input", {})
                        
                        self.publish_event("TOOL_CALL", {"tool": tool_name, "input": tool_input})
                        
                        # Execute tool
                        self.set_status(AgentStatus.TOOL_CALLING)
                        tool_def = get_tool(tool_name)
                        if tool_def:
                            result = tool_def["func"](**tool_input)
                        else:
                            result = f"Error: Tool '{tool_name}' not found."
                            
                        self.publish_event("TOOL_RESULT", {"tool": tool_name, "result": result})
                        
                        # Append to messages for next iteration
                        messages.append({"role": "assistant", "content": f"<tool>\n{tool_json_str}\n</tool>"})
                        messages.append({"role": "user", "content": f"Tool Result:\n{result}"})
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse tool JSON: {tool_json_str}")
                        messages.append({"role": "assistant", "content": buffer})
                        messages.append({"role": "user", "content": "Error: Invalid JSON tool call format. Please try again."})
                else:
                    # Final answer completed
                    messages.append({"role": "assistant", "content": buffer})
                    break
                    
            except Exception as e:
                logger.error(f"Agent execution failed: {e}")
                self.set_status(AgentStatus.ERROR)
                self.publish_event("error", {"message": str(e)})
                raise e
            
        self.set_status(AgentStatus.DONE)
        return {"result": "success", "agent_id": self.agent_id}

    def save_memory(self):
        pass

    def publish_event(self, event_type: str, data: dict):
        channel = f"vexon:stream:{self.session_id}"
        payload = {
            "type": event_type,
            "agent_id": self.agent_id,
            "data": data
        }
        self.redis_client.publish(channel, json.dumps(payload))
