"""The worker manifest: which framework builds which game, how to launch it, and
the colour it flies on the live board.

Discovery is just "is the file there". A student who skipped a day has no worker
file for that framework, so its game is quietly left out and the team is smaller.
The launch paths are the only place the cross-folder layout is written down, so a
folder rename is a one-line fix here.
"""

from __future__ import annotations

import shutil
from pathlib import Path
import docker
from logger import logger
from docker.models.containers import Container
from requests.exceptions import ConnectionError, ReadTimeout

HERE = Path(__file__).resolve().parent
client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
# One record per framework, in the order they were taught. key is also the slug,
# the folder its game is built into; file is relative to this folder; colour is a
# rich colour for the live board; runner picks the launcher (uv run vs npx tsx).
WORKERS = [
    #{"key": "strands", "name": "AWS Strands", "colour": "cyan", "file": "workers/strands_worker.py", "runner": "python"},
    {"key": "pydantic", "name": "Pydantic AI", "colour": "green", "file": "workers/pydantic_worker.py", "runner": "python"},
    #{"key": "maf", "name": "Microsoft Agent Framework", "colour": "magenta", "file": "workers/maf_worker.py", "runner": "python"},
    #{"key": "agno", "name": "Agno", "colour": "yellow", "file": "workers/agno_worker.py", "runner": "python"}
]


def discover(skip: tuple[str, ...] = ()) -> list[dict]:
    """The workers whose files exist on disk, minus any skipped by key. Each result
    is its manifest record with slug set to its key (the folder its game builds into);
    the game itself is invented at runtime, so nothing about it is fixed here."""
    found = []
    for worker in WORKERS:
        if worker["key"] in skip:
            continue
        if (HERE/worker["file"]).exists():
            found.append({**worker, "slug": worker["key"]})
    return found


def launch_argv(worker: dict, task_id: int, board_path: Path) -> list[str]:
    """The subprocess argv that runs a worker against the shared board.

    The launcher (uv or npx) is resolved to its full path with shutil.which. On Windows
    a bare "npx" is not found by subprocess.Popen, because npx is a .cmd shim and Popen
    does not consult PATHEXT; resolving it first is what the MCP libraries do to spawn
    npx, and on Mac and Linux which returns the same plain path."""
    path = str((HERE / worker["file"]).resolve())
    if worker["runner"] == "python":
        return [shutil.which("uv") or "uv", "run", path, str(task_id), str(board_path)]
    return [shutil.which("npx") or "npx", "tsx", path, str(task_id), str(board_path)]


def launch_container(worker: dict, task_id: int, site_dir: Path) -> Container:
    try:
        path = str(worker["file"].split('.')[0]).replace('/', '.')
        sitepath = str(site_dir).split('/')[-1]
        sitepath = f"/workspace/{sitepath}"
        # Spin up an ephemeral, resource-constrained container
        # 1. Create the container without running it automatically
        print(f"Container path - {path}, sitepath - {sitepath}")
        container = client.containers.run(
            image="workers-sandbox:latest",
            command=[
                "-m",
                f"{path}",
                str(task_id),
                f"{sitepath}",
            ],
            volumes={
                str(HERE): {
                    "bind": "/workspace",
                    "mode": "rw",
                }
            },
            working_dir="/workspace",
            environment={
                "WORKSPACE": "/workspace",
            },
            name=worker["key"],
            detach=True,
            auto_remove=False,
        )

        logger.debug(f"{container.name} started for worker {path}")
        return container
    except docker.errors.ContainerError as ce:
        logger.error(f"Execution Error: {ce.stderr.decode('utf-8')}")
        raise ce
    except Exception as e:
        logger.error(f"Launch Error: {e}")
        raise e
