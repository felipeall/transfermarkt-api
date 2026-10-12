"""Run with a core-only installation outside the source checkout."""

import asyncio
import importlib.util
import os
from importlib.metadata import distribution
from pathlib import Path

# Invalid server settings and a local .env must not affect SDK imports.
os.environ["TFMKT_MAX_CONCURRENCY"] = "not-an-integer"
Path(".env").write_text("TFMKT_TIMEOUT_SECONDS=not-a-number\n")

import httpx  # noqa: E402

from transfermarkt_api import Transfermarkt, __version__  # noqa: E402
from transfermarkt_api.schemas import Countries  # noqa: E402


async def main() -> None:
    """Verify core dependencies, type metadata, isolation and offline assembly."""
    for module in ("fastapi", "uvicorn", "limits", "pydantic_settings"):
        assert importlib.util.find_spec(module) is None, module
    installed = distribution("transfermarkt-api")
    assert installed.version == __version__
    assert any(str(path) == "transfermarkt_api/py.typed" for path in installed.files or [])
    core_requirements = [requirement for requirement in installed.requires or [] if ";" not in requirement]
    assert len(core_requirements) == 3
    assert all("==" not in requirement for requirement in core_requirements)
    assert {requirement.split("<")[0].split(">")[0] for requirement in core_requirements} == {
        "cachetools",
        "httpx",
        "pydantic",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        """Answer entirely offline."""
        return httpx.Response(200, json={"success": True, "data": {"countries": []}})

    async with Transfermarkt(transport=httpx.MockTransport(handler), cache=None) as tm:
        result = await tm.countries()
        assert isinstance(result, Countries)
        assert result.countries == []
    print("Core-only distribution, import isolation and offline facade checks passed")


if __name__ == "__main__":
    asyncio.run(main())
