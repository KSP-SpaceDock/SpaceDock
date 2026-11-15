# Rename SpaceDock → Spacedock: Complete Checklist

## Package Rename (code)
| File | Change |
|------|--------|
| `SpaceDock/` directory | Rename to `Spacedock/` |
| `SpaceDock/__init__.py` | Rename to `Spacedock/__init__.py` |
| All `from SpaceDock.` imports | Change to `from Spacedock.` |
| `run-tests.sh:39` | `SpaceDock` → `Spacedock` in pytest coverage |
| `mypy.yml:23` | `SpaceDock` → `Spacedock` |
| `docker-compose.yml:41` | `FLASK_APP=Spacedock.app:app` |
| `docker-compose.yml:70` | `Spacedock.celery:app` |
| `docker-compose-prod.yml:33` | `Spacedock.app:app` |
| `docker-compose-prod.yml:59` | `Spacedock.celery:app` |
| `logging.ini.example:15` | `qualname = Spacedock.app` |
| `conftest.py:8` | `from Spacedock.app import app` |
| `.dockerignore:15` | `!Spacedock` |
| `.python_history:6-7` | Import lines |

## Package Metadata (no code change)
| File | Change |
|------|--------|
| `SpaceDock.egg-info/top_level.txt` | `Spacedock` |
| `SpaceDock.egg-info/SOURCES.txt` | All `SpaceDock/` paths → `Spacedock/` |

## Documentation (prose)
| File | Change |
|------|--------|
| `THANKS:3` | "Original SpaceDock Credits" → "Original Credits" (optional) |
| `README.md:157` | "SpaceDock mailer daemon" → "SpaceDock mailer daemon" |
| `CONTINUE.md:87` | `python Spacedock/app.py` |
| `CONTINUE.md:92` | `gunicorn Spacedock.app:app` |
| `CONTINUE.md:97` | `Spacedock.celery:app` |

## Keep as "SpaceDock" (historical/brand)
| Reference | Reason |
|-----------|--------|
| `THANKS:5-18` | Historical credit names (Drew "SirCmpwn" DeVault, etc.) |
| GitHub repo URL | `KSP-SpaceDock` (different) |
| Domain `spacedock.info` | Already Spacedock |
| Docker images | Already `spacedock_*` |

## Impact
- **Code changes**: ~30 files with import paths
- **Package metadata**: 2 egg-info files (auto-generated on reinstall)
- **Prose changes**: ~6 documentation lines
- **Directory rename**: 1 top-level directory

**Estimated effort**: 30 min (mechanical find/replace + tests)

## Risk
- Low: Import paths are mechanical; tests will catch breakage
- **Verify**: All tests pass after rename
- **Verify**: Docker containers start successfully
- **Verify**: CLI tools work (`spacedock database wait`, etc.)