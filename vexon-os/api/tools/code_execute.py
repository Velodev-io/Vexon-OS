import subprocess
from .registry import register_tool

@register_tool(
    name="code_execute",
    description="Execute Python code in a sandboxed environment",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "The python code to execute"}
        },
        "required": ["code"]
    }
)
def code_execute(code: str):
    try:
        # Note: This is a basic subprocess run. For real production, use a secure sandbox like gVisor or Docker.
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out after 10 seconds"}
    except Exception as e:
        return {"error": str(e)}
