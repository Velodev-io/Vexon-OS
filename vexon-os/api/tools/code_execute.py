import os
import subprocess
import tempfile
from .registry import register_tool


def execute_sandboxed(code: str, timeout: int = 10):
    try:
        import docker
    except ImportError:
        docker = None

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as handle:
        handle.write(code)
        temp_path = handle.name

    if docker is not None:
        client = None
        container = None
        try:
            client = docker.from_env()
            container = client.containers.run(
                "python:3.12-slim",
                command=["python", f"/code/{os.path.basename(temp_path)}"],
                volumes={os.path.dirname(temp_path): {"bind": "/code", "mode": "ro"}},
                mem_limit="128m",
                nano_cpus=500_000_000,
                network_disabled=True,
                working_dir="/code",
                detach=True,
                stderr=True,
                stdout=True,
            )
            result = container.wait(timeout=timeout)
            logs = container.logs().decode()
            return {
                "stdout": logs if result.get("StatusCode", 1) == 0 else "",
                "stderr": logs if result.get("StatusCode", 1) != 0 else "",
                "exit_code": result.get("StatusCode", 1),
                "engine": "docker",
            }
        except Exception as exc:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            docker_error = str(exc)
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass
    else:
        docker_error = "docker SDK is not installed"

    try:
        result = subprocess.run(
            ["python3", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "engine": "subprocess_fallback",
            "warning": f"Docker sandbox unavailable: {docker_error}",
        }
    except subprocess.TimeoutExpired:
        return {
            "error": "Execution timed out after 10 seconds",
            "engine": "subprocess_fallback",
            "warning": f"Docker sandbox unavailable: {docker_error}",
        }
    finally:
        os.unlink(temp_path)

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
        return execute_sandboxed(code)
    except Exception as exc:
        return {"error": str(exc)}
