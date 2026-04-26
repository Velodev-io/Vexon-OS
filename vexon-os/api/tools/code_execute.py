import os
import tempfile
from .registry import register_tool


def execute_sandboxed(code: str, timeout: int = 10):
    docker_error = "docker SDK is not installed"
    try:
        import docker
    except ImportError:
        docker = None

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as handle:
        handle.write(code)
        temp_path = handle.name

    try:
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
                    read_only=True,
                    user="65534:65534",
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
                if container is not None:
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass
                if client is not None:
                    try:
                        client.close()
                    except Exception:
                        pass

        return {
            "error": (
                "Code execution is unavailable because the Docker sandbox is not ready. "
                f"Details: {docker_error}"
            ),
            "engine": "unavailable",
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
