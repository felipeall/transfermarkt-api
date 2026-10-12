# Python package releases

The SDK and HTTP service share one version. The first SDK release is `5.0.0`.

## One-time publisher setup

Configure a GitHub Trusted Publisher on PyPI and, separately, on TestPyPI:

| Field | Value |
| --- | --- |
| Project name | `transfermarkt-api` |
| GitHub owner | `felipeall` |
| Repository | `transfermarkt-api` |
| Workflow filename | `release.yml` |
| Environment | `pypi` on PyPI; `testpypi` on TestPyPI |

For a new project, use the account's pending-publisher form. The first successful upload creates the project;
configuring a pending publisher does not reserve its name. No API token is required.

## Release procedure

1. Update `pyproject.toml`, `transfermarkt_api/_version.py`, and `uv.lock` to the same version. Finalize the dated
   changelog entry. Merge the release changes after CI passes.
2. Create a tag on the merged commit and a draft GitHub release with its notes and verified distribution artifacts.
3. For a trial upload, manually run **Publish Python package** with that tag and `repository=testpypi`.
   Verify the TestPyPI package in an isolated environment. Install dependencies from PyPI first, then install the
   package from TestPyPI using `--no-deps` so the test registry does not supply dependencies.
4. Publish the GitHub release. The `release: published` event runs checks for the release tag, builds and verifies
   distributions, and publishes those same artifacts to PyPI using OIDC.
5. Verify `pip install transfermarkt-api==<version>` and a basic offline SDK call outside the source checkout.

The manual workflow can also target `pypi` to retry publication for an existing tag. It uses the registry's check URL
to skip identical uploaded files. Never overwrite a release with different artifacts; ship a new patch version.

Only commits reachable from `main` can publish. The tag, package version and SDK version must match, and the changelog
must be dated. Build/test jobs have read-only permissions; only the separate publishing job can obtain an OIDC token.
The `pypi` and `testpypi` GitHub environments identify the publishers. Repository administrators can configure
environment reviewers if release publication needs an additional approval step.

Compatible fixes use patch releases, compatible additions use minor releases, and breaking public API changes use
major releases. Fly deployment remains independent and continues to follow merged changes on `main`.

References: [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/),
[uv publishing from GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/#publishing-to-pypi).
