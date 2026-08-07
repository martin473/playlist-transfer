# Verification command map

## Dispatch 0001 — 001.01
Working directory: `repository root`

```bash
test -d runtime/src/playlist_bridge
```

## Dispatch 0002 — 001.02
Working directory: `repository root`

```bash
test -d runtime/tests
```

## Dispatch 0003 — 001.03
Working directory: `repository root`

```bash
test -d extension
```

## Dispatch 0004 — 001.04
Working directory: `repository root`

```bash
test -d fixtures
```

## Dispatch 0005 — 001.05
Working directory: `repository root`

```bash
test -d docs
```

## Dispatch 0006 — 008.01
Working directory: `repository root`

```bash
git check-ignore -q --no-index .venv/
```

```bash
git check-ignore -q --no-index runtime/__pycache__/x.pyc
```

## Dispatch 0007 — 002.01
Working directory: `runtime`

```bash
python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"
```

## Dispatch 0008 — 008.02
Working directory: `repository root`

```bash
git check-ignore -q --no-index runtime/example.sqlite
```

```bash
git check-ignore -q --no-index reports/example.json
```

## Dispatch 0009 — 002.02
Working directory: `runtime`

```bash
python3 - <<'PY'
import tomllib
d=tomllib.load(open('pyproject.toml','rb'))
assert d['project']['name']=='playlist-bridge'
assert d['project']['requires-python']=='>=3.12'
PY
```

## Dispatch 0010 — 008.03
Working directory: `repository root`

```bash
git check-ignore -q --no-index client_secret.json
```

```bash
git check-ignore -q --no-index token-export.json
```

## Dispatch 0011 — 002.03
Working directory: `runtime`

```bash
python3 - <<'PY'
import tomllib
d=tomllib.load(open('pyproject.toml','rb'))
assert d['project']['scripts']['playlist-bridge']=='playlist_bridge.cli:app'
PY
```

## Dispatch 0012 — 008.04
Working directory: `repository root`

```bash
git check-ignore -q --no-index extension/node_modules/pkg/index.js
```

```bash
git check-ignore -q --no-index runtime/dist/example.whl
```

## Dispatch 0013 — 003.01
Working directory: `runtime`

```bash
python3 - <<'PY'
import tomllib
d=tomllib.load(open('pyproject.toml','rb'))
required={'typer','pydantic','platformdirs','spotipy','google-api-python-client','google-auth','google-auth-oauthlib','keyring','SQLAlchemy','alembic','rapidfuzz','tenacity','isodate'}
actual={x.split('[',1)[0].split('>',1)[0].split('=',1)[0] for x in d['project']['dependencies']}
assert required <= actual, required-actual
PY
```

## Dispatch 0014 — 004.01
Working directory: `runtime`

```bash
python3 - <<'PY'
import tomllib
d=tomllib.load(open('pyproject.toml','rb'))
text=str(d)
for name in ('pytest','pytest-cov','hypothesis','ruff','mypy','build'):
    assert name in text, name
PY
```

## Dispatch 0015 — 005.01, 005.02
Working directory: `repository root`

```bash
PYTHONPATH=runtime/src python3 - <<'PY'
import playlist_bridge
assert isinstance(playlist_bridge.__version__,str) and playlist_bridge.__version__
PY
```

## Dispatch 0016 — 006.01
Working directory: `runtime`

```bash
python3 -m py_compile src/playlist_bridge/cli.py
```

```bash
python3 - <<'PY'
import ast
t=ast.parse(open('src/playlist_bridge/cli.py').read())
assert any(isinstance(n,ast.Assign) and any(getattr(x,'id',None)=='app' for x in n.targets) for n in t.body)
PY
```

## Dispatch 0017 — 004.02, 004.03, 004.04
Working directory: `runtime`

```bash
uv sync
```

```bash
uv run pytest --version
```

```bash
uv run ruff --version
```

```bash
uv run mypy --version
```

```bash
uv run python -m build --version
```

```bash
test -f uv.lock
```

```bash
before=$(shasum -a 256 uv.lock | awk '{print $1}'); uv sync --frozen; after=$(shasum -a 256 uv.lock | awk '{print $1}'); test "$before" = "$after"
```

## Dispatch 0018 — 156.01
Working directory: `extension`

```bash
node -e "const p=require('./package.json'); if(!p.name||p.private!==true) process.exit(1)"
```

## Dispatch 0019 — 013.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.enums')
assert hasattr(m,'SourceService'), 'SourceService'
PY
```

## Dispatch 0020 — 093.01, 093.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0021 — 066.01, 066.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0022 — 006.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_version.py -q
```

## Dispatch 0023 — 002.04
Working directory: `runtime`

```bash
rm -rf dist
```

```bash
uv run python -m build
```

```bash
test -n "$(find dist -maxdepth 1 -name '*.whl' -print -quit)"
```

```bash
test -n "$(find dist -maxdepth 1 -name '*.tar.gz' -print -quit)"
```

## Dispatch 0024 — 003.02
Working directory: `runtime`

```bash
uv sync --frozen
```

```bash
uv run python - <<'PY'
import typer,pydantic,platformdirs,spotipy,keyring,sqlalchemy,alembic,rapidfuzz,tenacity,isodate
import googleapiclient,google.auth,google_auth_oauthlib
print('runtime dependencies import successfully')
PY
```

## Dispatch 0025 — 156.02
Working directory: `extension`

```bash
node -e "const p=require('./package.json'); for(const n of ['@earendil-works/pi-coding-agent','typebox']) if(!(n in (p.dependencies||{}))) process.exit(1)"
```

## Dispatch 0026 — 013.02, 013.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_enums.py -q
```

## Dispatch 0027 — 007.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_version.py --collect-only -q
```

## Dispatch 0028 — 156.03
Working directory: `extension`

```bash
node -e "const p=require('./package.json'); if(!('typescript' in (p.devDependencies||{}))) process.exit(1)"
```

## Dispatch 0029 — 015.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_enums.py -q
```

## Dispatch 0030 — 014.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_enums.py -q
```

## Dispatch 0031 — 019.01, 019.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0032 — 017.01, 017.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0033 — 056.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.errors')
assert hasattr(m,'ProviderError'), 'ProviderError'
PY
```

## Dispatch 0034 — 007.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_version.py -q
```

## Dispatch 0035 — 156.04
Working directory: `extension`

```bash
node -e "const p=require('./package.json'); if(!(p.scripts&&p.scripts.typecheck)) process.exit(1)"
```

## Dispatch 0036 — 009.01
Working directory: `runtime`

```bash
ruff check
```

## Dispatch 0037 — 015.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_enums.py -q
```

## Dispatch 0038 — 014.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_enums.py -q
```

## Dispatch 0039 — 056.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.errors')
assert hasattr(m,'AuthenticationRequired'), 'AuthenticationRequired'
PY
```

## Dispatch 0040 — 156.05
Working directory: `extension`

```bash
node -e "const p=require('./package.json'); if(!(p.scripts&&p.scripts.test)) process.exit(1)"
```

## Dispatch 0041 — 009.02
Working directory: `runtime`

```bash
mypy
```

## Dispatch 0042 — 015.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_enums.py -q
```

## Dispatch 0043 — 056.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.errors')
assert hasattr(m,'PermissionDenied'), 'PermissionDenied'
PY
```

## Dispatch 0044 — 156.06, 156.07
Working directory: `extension`

```bash
npm install --package-lock-only --ignore-scripts
```

```bash
test -f package-lock.json
```

```bash
npm ci
```

## Dispatch 0045 — 009.03
Working directory: `runtime`

```bash
pytest
```

## Dispatch 0046 — 016.01, 016.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0047 — 018.01, 018.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0048 — 056.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.errors')
assert hasattr(m,'ProviderNotFound'), 'ProviderNotFound'
PY
```

## Dispatch 0049 — 157.01, 157.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0050 — 189.01, 189.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_ports.py -q
```

```bash
uv run mypy src/playlist_bridge/ports.py
```

## Dispatch 0051 — 190.01, 190.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0052 — 190.03
Working directory: `extension`

```bash
npm run typecheck
```

```bash
npm test -- test/types.test.ts
```

## Dispatch 0053 — 039.01, 039.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/credentials/test_store.py -q
```

## Dispatch 0054 — 020.01, 020.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0055 — 101.01, 101.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0056 — 056.05
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.errors')
assert hasattr(m,'RateLimited'), 'RateLimited'
PY
```

## Dispatch 0057 — 010.01
Working directory: `repository root`

```bash
bash -n scripts/verify-runtime.sh
```

## Dispatch 0058 — 158.01, 158.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0059 — 040.01, 040.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/credentials/test_store.py -q
```

## Dispatch 0060 — 021.01, 021.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0061 — 056.06
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.errors')
assert hasattr(m,'InvalidProviderResponse'), 'InvalidProviderResponse'
PY
```

## Dispatch 0062 — 010.02
Working directory: `repository root`

```bash
bash -n scripts/verify-runtime.sh
```

## Dispatch 0063 — 158.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0064 — 040.03, 040.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/credentials/test_store.py -q
```

## Dispatch 0065 — 022.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0066 — 056.07
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.errors')
assert hasattr(m,'TemporaryProviderFailure'), 'TemporaryProviderFailure'
PY
```

## Dispatch 0067 — 010.03
Working directory: `repository root`

```bash
bash -n scripts/verify-runtime.sh
```

## Dispatch 0068 — 158.04
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0069 — 040.05, 040.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/credentials/test_store.py -q
```

## Dispatch 0070 — 022.02, 022.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0071 — 057.01, 057.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0072 — 010.04, 010.05
Working directory: `repository root`

```bash
bash -n scripts/verify-runtime.sh
```

## Dispatch 0073 — 158.05
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0074 — 041.01, 041.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/credentials/test_store.py -q
```

## Dispatch 0075 — 022.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0076 — 011.01, 011.02
Working directory: `repository root`

```bash
playlist-bridge
```

## Dispatch 0077 — 042.01, 042.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/credentials/test_store.py -q
```

## Dispatch 0078 — 022.05, 022.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0079 — 011.03, 011.04
Working directory: `repository root`

```bash
playlist-bridge
```

## Dispatch 0080 — 022.07
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0081 — 011.05, 011.06
Working directory: `repository root`

```bash
playlist-bridge
```

## Dispatch 0082 — 022.08
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0083 — 011.07, 011.08
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_paths.py -q
```

## Dispatch 0084 — 022.09
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0085 — 011.09, 011.10
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_paths.py -q
```

## Dispatch 0086 — 022.10, 022.11
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_models.py -q
```

## Dispatch 0087 — 011.11, 011.12
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_paths.py -q
```

## Dispatch 0088 — 047.01, 047.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_youtube_auth.py -q
```

## Dispatch 0089 — 023.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0090 — 116.01, 116.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_job_creation.py -q
```

## Dispatch 0091 — 012.01, 012.02
Working directory: `repository root`

```bash
test -d ensure_app_directories()
```

## Dispatch 0092 — 058.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.youtube')
assert hasattr(m,'SourceAdapter'), 'SourceAdapter'
PY
```

## Dispatch 0093 — 043.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.settings')
assert hasattr(m,'SpotifyOAuthSettings'), 'SpotifyOAuthSettings'
PY
```

## Dispatch 0094 — 048.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_youtube_auth.py -q
```

## Dispatch 0095 — 023.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0096 — 025.01, 025.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_engine.py -q
```

## Dispatch 0097 — 058.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.youtube')
assert hasattr(m,'SourceAdapter'), 'SourceAdapter'
PY
```

## Dispatch 0098 — 043.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.settings')
assert hasattr(m,'SpotifyOAuthSettings'), 'SpotifyOAuthSettings'
PY
```

## Dispatch 0099 — 048.02, 048.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_youtube_auth.py -q
```

## Dispatch 0100 — 023.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0101 — 026.01, 026.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_base.py -q
```

## Dispatch 0102 — 058.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.youtube')
assert hasattr(m,'SourceAdapter'), 'SourceAdapter'
PY
```

## Dispatch 0103 — 043.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.settings')
assert hasattr(m,'SpotifyOAuthSettings'), 'SpotifyOAuthSettings'
PY
```

## Dispatch 0104 — 043.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.auth.spotify')
assert hasattr(m,'SpotifyOAuthSettings'), 'SpotifyOAuthSettings'
PY
```

## Dispatch 0105 — 049.01, 049.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_youtube_auth.py -q
```

## Dispatch 0106 — 023.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0107 — 028.01, 028.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_models.py -q
```

## Dispatch 0108 — 027.01, 027.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_models.py -q
```

## Dispatch 0109 — 031.01, 031.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_models.py -q
```

## Dispatch 0110 — 032.01, 032.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_models.py -q
```

## Dispatch 0111 — 058.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0112 — 044.01, 044.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0113 — 050.01, 050.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_youtube_auth.py -q
```

## Dispatch 0114 — 023.05
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0115 — 028.03, 028.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_models.py -q
```

## Dispatch 0116 — 045.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0117 — 051.01, 051.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_youtube_auth.py -q
```

## Dispatch 0118 — 023.06
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0119 — 029.01, 029.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_models.py -q
```

## Dispatch 0120 — 045.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0121 — 023.07
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'failure'), 'failure'
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0122 — 030.01, 030.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_models.py -q
```

## Dispatch 0123 — 059.01, 059.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0124 — 045.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0125 — 023.08
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'cancellation'), 'cancellation'
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0126 — 033.01, 033.02
Working directory: `runtime`

```bash
uv run pytest tests/migration/test_migrations.py -q
```

## Dispatch 0127 — 060.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0128 — 033.03
Working directory: `runtime`

```bash
uv run pytest tests/migration/test_migrations.py -q
```

## Dispatch 0129 — 045.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0130 — 023.09
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.domain.events')
assert hasattr(m,'completion'), 'completion'
assert hasattr(m,'type'), 'type'
PY
```

## Dispatch 0131 — 060.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0132 — 033.04
Working directory: `runtime`

```bash
uv run pytest tests/migration/test_migrations.py -q
```

## Dispatch 0133 — 023.10, 023.11
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_events.py -q
```

## Dispatch 0134 — 060.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0135 — 046.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0136 — 118.01, 118.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_interfaces.py -q
```

## Dispatch 0137 — 033.05
Working directory: `runtime`

```bash
uv run pytest tests/migration/test_migrations.py -q
```

## Dispatch 0138 — 060.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0139 — 046.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0140 — 024.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_fixtures.py -q
```

## Dispatch 0141 — 118.03, 118.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_interfaces.py -q
```

## Dispatch 0142 — 060.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0143 — 046.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0144 — 024.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_fixtures.py -q
```

## Dispatch 0145 — 033.06
Working directory: `runtime`

```bash
uv run pytest tests/migration/test_migrations.py -q
```

## Dispatch 0146 — 119.01, 119.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_jsonl_emitter.py -q
```

## Dispatch 0147 — 037.01, 037.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0148 — 035.01, 035.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0149 — 036.01, 036.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0150 — 034.01, 034.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0151 — 061.01, 061.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0152 — 046.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_spotify_auth.py -q
```

## Dispatch 0153 — 024.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_fixtures.py -q
```

## Dispatch 0154 — 052.01, 052.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_status_logout.py -q
```

## Dispatch 0155 — 037.03, 037.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0156 — 035.03, 035.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0157 — 036.03, 036.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0158 — 034.03, 034.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0159 — 083.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.spotify')
assert hasattr(m,'SpotifyAdapter'), 'SpotifyAdapter'
PY
```

## Dispatch 0160 — 062.01, 062.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0161 — 024.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_domain_fixtures.py -q
```

## Dispatch 0162 — 052.03, 052.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_status_logout.py -q
```

## Dispatch 0163 — 037.05, 037.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0164 — 035.05, 035.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0165 — 036.05, 036.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0166 — 034.05, 034.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0167 — 083.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.spotify')
assert hasattr(m,'SpotifyAdapter'), 'SpotifyAdapter'
PY
```

## Dispatch 0168 — 063.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0169 — 037.07, 037.08
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0170 — 035.07, 035.08
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0171 — 036.07, 036.08
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0172 — 053.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_status_logout.py -q
```

## Dispatch 0173 — 083.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.spotify')
assert hasattr(m,'SpotifyAdapter'), 'SpotifyAdapter'
PY
```

## Dispatch 0174 — 063.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0175 — 053.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_status_logout.py -q
```

## Dispatch 0176 — 126.01, 126.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0177 — 123.01, 123.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0178 — 037.09, 037.10
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0179 — 035.09, 035.10
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0180 — 083.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.spotify')
assert hasattr(m,'SpotifyAdapter'), 'SpotifyAdapter'
PY
```

## Dispatch 0181 — 063.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0182 — 053.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_status_logout.py -q
```

## Dispatch 0183 — 035.11, 035.12
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0184 — 083.05
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.spotify')
assert hasattr(m,'SpotifyAdapter'), 'SpotifyAdapter'
PY
```

## Dispatch 0185 — 064.01, 064.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0186 — 035.13, 035.14
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0187 — 053.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_status_logout.py -q
```

## Dispatch 0188 — 083.06
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.providers.spotify')
assert hasattr(m,'SpotifyAdapter'), 'SpotifyAdapter'
PY
```

## Dispatch 0189 — 065.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0190 — 054.01, 054.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_status_logout.py -q
```

## Dispatch 0191 — 035.15, 035.16
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0192 — 083.07
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0193 — 065.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0194 — 054.03, 054.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/auth/test_status_logout.py -q
```

## Dispatch 0195 — 035.17, 035.18
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0196 — 084.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0197 — 065.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0198 — 035.19, 035.20
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repositories.py -q
```

## Dispatch 0199 — 189.03, 189.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_ports.py -q
```

```bash
uv run mypy src/playlist_bridge/ports.py
```

## Dispatch 0200 — 189.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/credentials/test_store.py -q
```

## Dispatch 0201 — 189.06, 189.07, 189.08
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repository_adapters.py -q
```

## Dispatch 0202 — 189.09, 189.10, 189.11
Working directory: `runtime`

```bash
uv run pytest tests/unit/persistence/test_repository_adapters.py -q
```

## Dispatch 0203 — 189.12, 189.13
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_bootstrap.py -q
```

## Dispatch 0204 — 189.14, 189.15
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_bootstrap.py -q
```

## Dispatch 0205 — 084.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0206 — 067.01, 067.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0207 — 055.01
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_auth_commands.py -q
```

## Dispatch 0208 — 117.01, 117.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_job_creation.py -q
```

## Dispatch 0209 — 124.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0210 — 084.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0211 — 068.01, 068.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_youtube.py -q
```

## Dispatch 0212 — 055.02
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_auth_commands.py -q
```

## Dispatch 0213 — 038.01, 038.02
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_transactions_and_leases.py -q
```

## Dispatch 0214 — 124.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0215 — 120.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'load_source_stage'), 'load_source_stage'
PY
```

## Dispatch 0216 — 084.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0217 — 055.03
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_auth_commands.py -q
```

## Dispatch 0218 — 069.01
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0219 — 038.03
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_transactions_and_leases.py -q
```

## Dispatch 0220 — 124.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0221 — 120.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'load_source_stage'), 'load_source_stage'
PY
```

## Dispatch 0222 — 084.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0223 — 055.04
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_auth_commands.py -q
```

## Dispatch 0224 — 069.02
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0225 — 038.04
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_transactions_and_leases.py -q
```

## Dispatch 0226 — 120.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'load_source_stage'), 'load_source_stage'
PY
```

## Dispatch 0227 — 084.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0228 — 069.03
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0229 — 038.05
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_transactions_and_leases.py -q
```

## Dispatch 0230 — 120.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'load_source_stage'), 'load_source_stage'
PY
```

## Dispatch 0231 — 085.01, 085.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0232 — 189.16, 189.17
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_bootstrap.py -q
```

## Dispatch 0233 — 069.04
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0234 — 086.01, 086.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0235 — 089.01, 089.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0236 — 090.01, 090.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0237 — 096.01, 096.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0238 — 069.05
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0239 — 087.01, 087.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0240 — 092.01, 092.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0241 — 069.06
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0242 — 094.01, 094.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0243 — 069.07
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0244 — 095.01, 095.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0245 — 069.08
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0246 — 097.01, 097.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0247 — 069.09
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_youtube_adapter.py -q
```

## Dispatch 0248 — 070.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.normalize')
assert hasattr(m,'normalize_unicode_text'), 'normalize_unicode_text'
PY
```

## Dispatch 0249 — 070.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.normalize')
assert hasattr(m,'normalize_unicode_text'), 'normalize_unicode_text'
PY
```

## Dispatch 0250 — 070.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.normalize')
assert hasattr(m,'normalize_unicode_text'), 'normalize_unicode_text'
PY
```

## Dispatch 0251 — 070.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.normalize')
assert hasattr(m,'normalize_unicode_text'), 'normalize_unicode_text'
PY
```

## Dispatch 0252 — 070.05, 070.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0253 — 071.01, 071.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0254 — 072.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0255 — 091.01, 091.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0256 — 125.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resolve_destination'), 'resolve_destination'
PY
```

## Dispatch 0257 — 072.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0258 — 125.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resolve_destination'), 'resolve_destination'
PY
```

## Dispatch 0259 — 073.01, 073.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0260 — 125.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resolve_destination'), 'resolve_destination'
PY
```

## Dispatch 0261 — 074.01, 074.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0262 — 075.01, 075.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0263 — 125.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resolve_destination'), 'resolve_destination'
PY
```

## Dispatch 0264 — 076.01, 076.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0265 — 077.01, 077.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0266 — 127.01, 127.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0267 — 078.01, 078.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0268 — 128.01, 128.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0269 — 132.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0270 — 079.01, 079.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0271 — 132.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0272 — 129.01, 129.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0273 — 080.01, 080.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0274 — 081.01, 081.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0275 — 099.01, 099.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0276 — 100.01, 100.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0277 — 102.01, 102.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0278 — 103.01, 103.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0279 — 104.01, 104.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0280 — 132.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0281 — 130.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0282 — 082.01, 082.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0283 — 105.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0284 — 088.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0285 — 132.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0286 — 130.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0287 — 082.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0288 — 105.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0289 — 088.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0290 — 132.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0291 — 130.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0292 — 082.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_normalize.py tests/property/test_normalize_properties.py -q
```

## Dispatch 0293 — 105.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0294 — 088.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/providers/test_spotify.py -q
```

## Dispatch 0295 — 133.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0296 — 130.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0297 — 105.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0298 — 098.01
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_spotify_adapter.py -q
```

## Dispatch 0299 — 133.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0300 — 131.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0301 — 106.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0302 — 098.02
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_spotify_adapter.py -q
```

## Dispatch 0303 — 133.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0304 — 131.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0305 — 106.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0306 — 098.03
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_spotify_adapter.py -q
```

## Dispatch 0307 — 133.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0308 — 131.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0309 — 106.03, 106.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0310 — 098.04
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_spotify_adapter.py -q
```

## Dispatch 0311 — 133.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0312 — 131.04, 131.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0313 — 107.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0314 — 110.01, 110.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_matcher.py -q
```

## Dispatch 0315 — 098.05
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_spotify_adapter.py -q
```

## Dispatch 0316 — 133.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0317 — 131.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0318 — 107.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0319 — 098.06
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_spotify_adapter.py -q
```

## Dispatch 0320 — 107.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0321 — 098.07
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_spotify_adapter.py -q
```

## Dispatch 0322 — 107.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0323 — 098.08
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_spotify_adapter.py -q
```

## Dispatch 0324 — 182.01
Working directory: `repository root`

```bash
find fixtures/providers -type f -name '*.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
```

## Dispatch 0325 — 108.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0326 — 182.02
Working directory: `repository root`

```bash
find fixtures/providers -type f -name '*.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
```

## Dispatch 0327 — 108.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0328 — 182.03
Working directory: `repository root`

```bash
cd runtime && uv run pytest tests/contract/test_provider_consumed_fields.py -q
```

## Dispatch 0329 — 108.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0330 — 182.04
Working directory: `repository root`

```bash
cd runtime && uv run pytest tests/contract/test_provider_consumed_fields.py -q
```

## Dispatch 0331 — 108.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_scoring.py -q
```

## Dispatch 0332 — 137.01, 137.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_reports.py -q
```

## Dispatch 0333 — 113.01, 113.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_matcher.py -q
```

## Dispatch 0334 — 109.01, 109.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_matcher.py -q
```

## Dispatch 0335 — 111.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.matcher')
assert hasattr(m,'match_source_track'), 'match_source_track'
PY
```

## Dispatch 0336 — 111.02, 111.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.matcher')
assert hasattr(m,'match_source_track'), 'match_source_track'
PY
```

## Dispatch 0337 — 111.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.matcher')
assert hasattr(m,'match_source_track'), 'match_source_track'
PY
```

## Dispatch 0338 — 111.05
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.matcher')
assert hasattr(m,'match_source_track'), 'match_source_track'
PY
```

## Dispatch 0339 — 111.06
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.matcher')
assert hasattr(m,'match_source_track'), 'match_source_track'
PY
```

## Dispatch 0340 — 111.07
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.matcher')
assert hasattr(m,'match_source_track'), 'match_source_track'
PY
```

## Dispatch 0341 — 111.08
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.matching.matcher')
assert hasattr(m,'match_source_track'), 'match_source_track'
PY
```

## Dispatch 0342 — 112.01, 112.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/matching/test_matcher.py -q
```

## Dispatch 0343 — 114.01
Working directory: `runtime`

```bash
uv run pytest tests/property/test_matching_properties.py -q
```

## Dispatch 0344 — 114.02
Working directory: `runtime`

```bash
uv run pytest tests/property/test_matching_properties.py -q
```

## Dispatch 0345 — 114.03
Working directory: `runtime`

```bash
uv run pytest tests/property/test_matching_properties.py -q
```

## Dispatch 0346 — 114.04
Working directory: `runtime`

```bash
uv run pytest tests/property/test_matching_properties.py -q
```

## Dispatch 0347 — 115.01
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0348 — 115.02
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0349 — 115.03
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0350 — 115.04
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0351 — 115.05
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0352 — 115.06
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0353 — 115.07
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0354 — 115.08
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0355 — 115.09
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0356 — 115.10
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0357 — 115.11
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0358 — 115.12
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0359 — 115.13
Working directory: `runtime`

```bash
uv run pytest tests/contract/test_matching_benchmark.py -q
```

## Dispatch 0360 — 121.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'match_one_stage'), 'match_one_stage'
PY
```

## Dispatch 0361 — 121.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'match_one_stage'), 'match_one_stage'
PY
```

## Dispatch 0362 — 121.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'match_one_stage'), 'match_one_stage'
PY
```

## Dispatch 0363 — 121.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'match_one_stage'), 'match_one_stage'
PY
```

## Dispatch 0364 — 121.05
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'match_one_stage'), 'match_one_stage'
PY
```

## Dispatch 0365 — 122.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'run_match_loop'), 'run_match_loop'
PY
```

## Dispatch 0366 — 122.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'run_match_loop'), 'run_match_loop'
PY
```

## Dispatch 0367 — 122.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'run_match_loop'), 'run_match_loop'
PY
```

## Dispatch 0368 — 122.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'run_match_loop'), 'run_match_loop'
PY
```

## Dispatch 0369 — 134.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0370 — 134.02, 134.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0371 — 134.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0372 — 134.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0373 — 134.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0374 — 135.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0375 — 135.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0376 — 135.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0377 — 135.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0378 — 135.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0379 — 135.06
Working directory: `runtime`

```bash
uv run pytest tests/unit/jobs/test_stages.py tests/integration/test_resume_reconciliation.py -q
```

## Dispatch 0380 — 153.01, 153.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0381 — 136.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.reports')
assert hasattr(m,'write_json_report'), 'write_json_report'
PY
```

## Dispatch 0382 — 161.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0383 — 146.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0384 — 154.01, 154.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0385 — 149.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0386 — 151.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0387 — 152.01, 152.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0388 — 141.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0389 — 142.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0390 — 143.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0391 — 144.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0392 — 145.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0393 — 136.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.reports')
assert hasattr(m,'write_json_report'), 'write_json_report'
PY
```

## Dispatch 0394 — 161.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0395 — 146.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0396 — 149.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0397 — 151.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0398 — 152.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0399 — 141.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0400 — 142.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0401 — 143.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0402 — 144.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0403 — 145.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0404 — 136.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.reports')
assert hasattr(m,'write_json_report'), 'write_json_report'
PY
```

## Dispatch 0405 — 161.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0406 — 146.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0407 — 149.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0408 — 151.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0409 — 141.03, 141.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0410 — 142.03, 142.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0411 — 143.03, 143.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0412 — 144.03, 144.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0413 — 145.03, 145.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0414 — 136.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.reports')
assert hasattr(m,'write_json_report'), 'write_json_report'
PY
```

## Dispatch 0415 — 161.04
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0416 — 164.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0417 — 146.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0418 — 136.05, 136.06
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.reports')
assert hasattr(m,'write_json_report'), 'write_json_report'
PY
```

## Dispatch 0419 — 161.05
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0420 — 164.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0421 — 146.05
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0422 — 150.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0423 — 138.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
from playlist_bridge.jobs.runner import RuntimeDependencies
assert RuntimeDependencies.__name__ == 'RuntimeDependencies'
PY
```

## Dispatch 0424 — 189.18
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_bootstrap.py -q
```

## Dispatch 0425 — 189.19
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_bootstrap.py -q
```

## Dispatch 0426 — 189.20
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_bootstrap_composition.py -q
```

## Dispatch 0427 — 166.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0428 — 164.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0429 — 150.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0430 — 138.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'RuntimeDependencies'), 'RuntimeDependencies'
assert hasattr(m,'run_transfer'), 'run_transfer'
PY
```

## Dispatch 0431 — 166.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0432 — 164.04
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0433 — 150.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0434 — 138.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'RuntimeDependencies'), 'RuntimeDependencies'
assert hasattr(m,'run_transfer'), 'run_transfer'
PY
```

## Dispatch 0435 — 166.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0436 — 150.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0437 — 138.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'RuntimeDependencies'), 'RuntimeDependencies'
assert hasattr(m,'run_transfer'), 'run_transfer'
PY
```

## Dispatch 0438 — 166.04
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0439 — 138.05
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'RuntimeDependencies'), 'RuntimeDependencies'
assert hasattr(m,'run_transfer'), 'run_transfer'
PY
```

## Dispatch 0440 — 166.05
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0441 — 138.06
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'RuntimeDependencies'), 'RuntimeDependencies'
assert hasattr(m,'run_transfer'), 'run_transfer'
PY
```

## Dispatch 0442 — 138.07, 138.08
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'RuntimeDependencies'), 'RuntimeDependencies'
assert hasattr(m,'run_transfer'), 'run_transfer'
PY
```

## Dispatch 0443 — 138.09
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'RuntimeDependencies'), 'RuntimeDependencies'
assert hasattr(m,'run_transfer'), 'run_transfer'
PY
```

## Dispatch 0444 — 138.10
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'RuntimeDependencies'), 'RuntimeDependencies'
assert hasattr(m,'run_transfer'), 'run_transfer'
PY
```

## Dispatch 0445 — 147.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0446 — 139.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resume_transfer'), 'resume_transfer'
PY
```

## Dispatch 0447 — 147.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0448 — 139.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resume_transfer'), 'resume_transfer'
PY
```

## Dispatch 0449 — 147.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0450 — 139.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resume_transfer'), 'resume_transfer'
PY
```

## Dispatch 0451 — 147.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0452 — 139.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resume_transfer'), 'resume_transfer'
PY
```

## Dispatch 0453 — 139.05
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'resume_transfer'), 'resume_transfer'
PY
```

## Dispatch 0454 — 148.01
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0455 — 140.01
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'rerun_unresolved_reviews'), 'rerun_unresolved_reviews'
PY
```

## Dispatch 0456 — 148.02
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0457 — 140.02
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'rerun_unresolved_reviews'), 'rerun_unresolved_reviews'
PY
```

## Dispatch 0458 — 148.03
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0459 — 140.03
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'rerun_unresolved_reviews'), 'rerun_unresolved_reviews'
PY
```

## Dispatch 0460 — 148.04
Working directory: `runtime`

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

## Dispatch 0461 — 140.04
Working directory: `runtime`

```bash
uv run python - <<'PY'
import importlib
m=importlib.import_module('playlist_bridge.jobs.runner')
assert hasattr(m,'rerun_unresolved_reviews'), 'rerun_unresolved_reviews'
PY
```

## Dispatch 0462 — 159.01, 159.02
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0463 — 155.01
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_cli.py -q
```

## Dispatch 0464 — 159.03, 159.04
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0465 — 155.02
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_cli.py -q
```

## Dispatch 0466 — 159.05, 159.06
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0467 — 159.07
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0468 — 155.03
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_cli.py -q
```

## Dispatch 0469 — 160.01
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0470 — 155.04
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_cli.py -q
```

## Dispatch 0471 — 160.02
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0472 — 155.05
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_cli.py -q
```

## Dispatch 0473 — 160.03
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0474 — 155.06
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_cli.py -q
```

## Dispatch 0475 — 160.04
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0476 — 155.07
Working directory: `runtime`

```bash
uv run pytest tests/integration/test_cli.py -q
```

## Dispatch 0477 — 183.01
Working directory: `repository root`

- Open `docs/acceptance/dry-run-live.md` and add a section headed `Dispatch 0463 — 183.01`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Specify one small owned YouTube playlist, authenticated profiles, and a no-write expectation.
- Record concrete evidence proving: The checklist has explicit prerequisites.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/dry-run-live.md`; otherwise mark FAIL.

## Dispatch 0478 — 185.01
Working directory: `repository root`

- Open `docs/acceptance/review-live.md` and add a section headed `Dispatch 0464 — 185.01`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Include at least one source item expected to require manual match review.
- Record concrete evidence proving: The dry run reports it as ambiguous or unmatched.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/review-live.md`; otherwise mark FAIL.

## Dispatch 0479 — 184.01
Working directory: `repository root`

- Open `docs/acceptance/write-live.md` and add a section headed `Dispatch 0465 — 184.01`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Specify one small owned YouTube playlist and a temporary private Spotify destination.
- Record concrete evidence proving: The checklist has explicit cleanup-safe prerequisites.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/write-live.md`; otherwise mark FAIL.

## Dispatch 0480 — 160.05
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0481 — 183.02
Working directory: `repository root`

- Open `docs/acceptance/dry-run-live.md` and add a section headed `Dispatch 0467 — 183.02`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Record playlist identity and source item count.
- Record concrete evidence proving: The checklist includes the observed count.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/dry-run-live.md`; otherwise mark FAIL.

## Dispatch 0482 — 185.02
Working directory: `repository root`

- Open `docs/acceptance/review-live.md` and add a section headed `Dispatch 0468 — 185.02`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Include at least one unavailable source item.
- Record concrete evidence proving: The item remains represented in reports.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/review-live.md`; otherwise mark FAIL.

## Dispatch 0483 — 184.02
Working directory: `repository root`

- Open `docs/acceptance/write-live.md` and add a section headed `Dispatch 0469 — 184.02`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Run create mode once using the documented CLI or Pi tool.
- Record concrete evidence proving: A destination playlist ID is recorded.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/write-live.md`; otherwise mark FAIL.

## Dispatch 0484 — 167.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0485 — 162.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0486 — 163.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0487 — 183.03
Working directory: `repository root`

- Open `docs/acceptance/dry-run-live.md` and add a section headed `Dispatch 0473 — 183.03`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Record matched, ambiguous, unavailable, skipped, and non-track outcomes.
- Record concrete evidence proving: Every source item has an explicit outcome.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/dry-run-live.md`; otherwise mark FAIL.

## Dispatch 0488 — 185.03
Working directory: `repository root`

- Open `docs/acceptance/review-live.md` and add a section headed `Dispatch 0474 — 185.03`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Include at least one remix/version-sensitive source item.
- Record concrete evidence proving: The decision records version reasoning.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/review-live.md`; otherwise mark FAIL.

## Dispatch 0489 — 184.03
Working directory: `repository root`

- Open `docs/acceptance/write-live.md` and add a section headed `Dispatch 0475 — 184.03`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Compare source accepted order/count with destination items.
- Record concrete evidence proving: Order and count match the expected accepted sequence.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/write-live.md`; otherwise mark FAIL.

## Dispatch 0490 — 167.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0491 — 162.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0492 — 163.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0493 — 183.04
Working directory: `repository root`

- Open `docs/acceptance/dry-run-live.md` and add a section headed `Dispatch 0479 — 183.04`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Check that no Spotify playlist was created or changed.
- Record concrete evidence proving: The checklist records absence of destination mutation.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/dry-run-live.md`; otherwise mark FAIL.

## Dispatch 0494 — 185.04
Working directory: `repository root`

- Open `docs/acceptance/review-live.md` and add a section headed `Dispatch 0480 — 185.04`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Include at least one non-track item.
- Record concrete evidence proving: The item is classified explicitly.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/review-live.md`; otherwise mark FAIL.

## Dispatch 0495 — 184.04
Working directory: `repository root`

- Open `docs/acceptance/write-live.md` and add a section headed `Dispatch 0481 — 184.04`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Manually inspect the selected remix/live/remaster variants represented by the test playlist.
- Record concrete evidence proving: The checklist records the selected versions.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/write-live.md`; otherwise mark FAIL.

## Dispatch 0496 — 167.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0497 — 162.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0498 — 163.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0499 — 185.05
Working directory: `repository root`

- Open `docs/acceptance/review-live.md` and add a section headed `Dispatch 0485 — 185.05`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Use review apply with a Spotify track ID or skip for the unresolved item.
- Record concrete evidence proving: The correction is persisted.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/review-live.md`; otherwise mark FAIL.

## Dispatch 0500 — 184.05
Working directory: `repository root`

- Open `docs/acceptance/write-live.md` and add a section headed `Dispatch 0486 — 184.05`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Inspect JSON and CSV/report outputs for counts and exceptions.
- Record concrete evidence proving: Required report sections are present.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/write-live.md`; otherwise mark FAIL.

## Dispatch 0501 — 162.04, 162.05
Working directory: `extension`

```bash
npm test -- test/process-control.test.ts
```

## Dispatch 0502 — 163.04
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0503 — 160.06
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0504 — 185.06
Working directory: `repository root`

- Open `docs/acceptance/review-live.md` and add a section headed `Dispatch 0489 — 185.06`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Resume or rerun unresolved review processing.
- Record concrete evidence proving: Only unresolved decisions are rematched.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/review-live.md`; otherwise mark FAIL.

## Dispatch 0505 — 184.06
Working directory: `repository root`

- Open `docs/acceptance/write-live.md` and add a section headed `Dispatch 0490 — 184.06`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Interrupt at a controlled checkpoint, resume, and compare destination items.
- Record concrete evidence proving: No duplicate write is introduced.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/write-live.md`; otherwise mark FAIL.

## Dispatch 0506 — 165.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0507 — 168.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0508 — 170.01
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0509 — 185.07
Working directory: `repository root`

- Open `docs/acceptance/review-live.md` and add a section headed `Dispatch 0494 — 185.07`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Inspect the final report for all prepared exception types.
- Record concrete evidence proving: Each exception is handled explicitly.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/review-live.md`; otherwise mark FAIL.

## Dispatch 0510 — 165.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0511 — 168.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0512 — 170.02
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0513 — 165.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0514 — 168.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0515 — 170.03
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0516 — 165.04
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0517 — 168.04
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0518 — 170.04
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0519 — 165.05
Working directory: `extension`

```bash
npm run typecheck
```

## Dispatch 0520 — 169.01, 169.02
Working directory: `extension`

```bash
npm test -- test/tools.test.ts
```

## Dispatch 0521 — 186.01
Working directory: `repository root`

- Open `docs/acceptance/credential-revocation.md` and add a section headed `Dispatch 0506 — 186.01`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Revoke the Spotify authorization externally for the test profile.
- Record concrete evidence proving: The grant is absent in the provider dashboard.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/credential-revocation.md`; otherwise mark FAIL.

## Dispatch 0522 — 177.01
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/security.md'); assert p.is_file()
text=p.read_text().lower()
assert 'keychain' in text, 'keychain'
assert 'token' in text, 'token'
PY
```

## Dispatch 0523 — 171.01, 171.02
Working directory: `extension`

```bash
npm test -- test/tools.test.ts
```

## Dispatch 0524 — 172.01, 172.02
Working directory: `extension`

```bash
npm test -- test/render.test.ts
```

## Dispatch 0525 — 175.01
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('SKILL.md'); assert p.is_file()
text=p.read_text().lower()
assert 'playlist_auth' in text, 'playlist_auth'
PY
```

## Dispatch 0526 — 186.02
Working directory: `repository root`

- Open `docs/acceptance/credential-revocation.md` and add a section headed `Dispatch 0511 — 186.02`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Run CLI status or a safe operation and observe authentication required.
- Record concrete evidence proving: Job data remains readable and uncorrupted.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/credential-revocation.md`; otherwise mark FAIL.

## Dispatch 0527 — 177.02
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/security.md'); assert p.is_file()
text=p.read_text().lower()
assert 'sqlite' in text, 'sqlite'
assert 'credential' in text, 'credential'
PY
```

## Dispatch 0528 — 173.01
Working directory: `extension`

```bash
npm test -- test/tools.test.ts
```

## Dispatch 0529 — 175.02
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('SKILL.md'); assert p.is_file()
text=p.read_text().lower()
assert 'playlist_transfer' in text, 'playlist_transfer'
assert 'dry_run' in text, 'dry_run'
assert 'create' in text, 'create'
assert 'merge' in text, 'merge'
assert 'replace' in text, 'replace'
PY
```

## Dispatch 0530 — 186.03
Working directory: `repository root`

- Open `docs/acceptance/credential-revocation.md` and add a section headed `Dispatch 0515 — 186.03`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Authenticate again under the same profile name.
- Record concrete evidence proving: Access is restored without creating a new local profile.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/credential-revocation.md`; otherwise mark FAIL.

## Dispatch 0531 — 177.03
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/security.md'); assert p.is_file()
text=p.read_text().lower()
assert 'oauth' in text, 'oauth'
assert 'browser' in text, 'browser'
assert 'api' in text, 'api'
PY
```

## Dispatch 0532 — 173.02
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0533 — 175.03
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('SKILL.md'); assert p.is_file()
text=p.read_text().lower()
assert 'playlist_review' in text, 'playlist_review'
assert 'list' in text, 'list'
assert 'apply' in text, 'apply'
PY
```

## Dispatch 0534 — 186.04
Working directory: `repository root`

- Open `docs/acceptance/credential-revocation.md` and add a section headed `Dispatch 0519 — 186.04`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Revoke the Google/YouTube authorization externally for the test profile.
- Record concrete evidence proving: The grant is absent in the provider dashboard.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/credential-revocation.md`; otherwise mark FAIL.

## Dispatch 0535 — 177.04
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/security.md'); assert p.is_file()
text=p.read_text().lower()
assert 'redaction' in text, 'redaction'
assert 'oauth code' in text, 'oauth code'
assert 'token' in text, 'token'
PY
```

## Dispatch 0536 — 173.03
Working directory: `extension`

```bash
npm test -- test/jsonl.test.ts
```

## Dispatch 0537 — 175.04
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('SKILL.md'); assert p.is_file()
text=p.read_text().lower()
assert 'token' in text, 'token'
assert 'password' in text, 'password'
PY
```

## Dispatch 0538 — 186.05
Working directory: `repository root`

- Open `docs/acceptance/credential-revocation.md` and add a section headed `Dispatch 0523 — 186.05`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Run CLI status or a safe operation and observe authentication required.
- Record concrete evidence proving: Job data remains readable and uncorrupted.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/credential-revocation.md`; otherwise mark FAIL.

## Dispatch 0539 — 177.05
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/security.md'); assert p.is_file()
text=p.read_text().lower()
assert 'shell' in text, 'shell'
assert 'spawn' in text, 'spawn'
assert 'permission' in text, 'permission'
PY
```

## Dispatch 0540 — 173.04
Working directory: `extension`

```bash
npm test -- test/process-control.test.ts
```

## Dispatch 0541 — 175.05
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('SKILL.md'); assert p.is_file()
text=p.read_text().lower()
assert 'shell' in text, 'shell'
assert 'registered tools' in text, 'registered tools'
PY
```

## Dispatch 0542 — 186.06
Working directory: `repository root`

- Open `docs/acceptance/credential-revocation.md` and add a section headed `Dispatch 0527 — 186.06`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Authenticate again under the same profile name.
- Record concrete evidence proving: Access is restored without creating a new local profile.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/credential-revocation.md`; otherwise mark FAIL.

## Dispatch 0543 — 177.06
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/security.md'); assert p.is_file()
text=p.read_text().lower()
assert 'threat' in text, 'threat'
assert 'dependency' in text, 'dependency'
assert 'metadata' in text, 'metadata'
PY
```

## Dispatch 0544 — 173.05
Working directory: `extension`

```bash
npm test -- test/tools.test.ts
```

## Dispatch 0545 — 175.06
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('SKILL.md'); assert p.is_file()
text=p.read_text().lower()
assert 'youtube-to-spotify' in text, 'youtube-to-spotify'
assert 'deferred' in text, 'deferred'
PY
```

## Dispatch 0546 — 177.07
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('docs/security.md'); assert p.is_file()
text=p.read_text().lower()
assert 'revoke' in text, 'revoke'
assert 'spotify' in text, 'spotify'
assert 'google' in text, 'google'
PY
```

## Dispatch 0547 — 173.06
Working directory: `extension`

```bash
npm test -- test/process.test.ts
```

## Dispatch 0548 — 175.07
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('SKILL.md'); assert p.is_file()
text=p.read_text().lower()
assert 'oauth' in text, 'oauth'
assert 'browser automation' in text, 'browser automation'
assert 'provider api' in text, 'provider api'
PY
```

## Dispatch 0549 — 173.07
Working directory: `extension`

```bash
npm test -- test/tools.test.ts
```

## Dispatch 0550 — 174.01
Working directory: `repository root`

```bash
bash -n scripts/verify-pi-extension.sh
```

## Dispatch 0551 — 174.02
Working directory: `repository root`

```bash
bash scripts/verify-pi-extension.sh
```

## Dispatch 0552 — 176.01
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'install' in text, 'install'
PY
```

## Dispatch 0553 — 181.01
Working directory: `repository root`

```bash
bash -n scripts/verify-all.sh
```

```bash
grep -F 'uv sync --frozen' scripts/verify-all.sh
```

## Dispatch 0554 — 176.02
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'spotify' in text, 'spotify'
assert 'google' in text, 'google'
assert 'redirect' in text, 'redirect'
assert 'client' in text, 'client'
PY
```

## Dispatch 0555 — 181.02
Working directory: `repository root`

```bash
bash -n scripts/verify-all.sh
```

```bash
grep -E 'ruff( check)?' scripts/verify-all.sh
```

## Dispatch 0556 — 176.03
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'configuration' in text, 'configuration'
assert 'placeholder' in text, 'placeholder'
for forbidden in ('client_secret = \"','refresh_token = \"','access_token = \"'):
    assert forbidden not in text
PY
```

## Dispatch 0557 — 181.03
Working directory: `repository root`

```bash
bash -n scripts/verify-all.sh
```

```bash
grep -F 'mypy' scripts/verify-all.sh
```

## Dispatch 0558 — 176.04
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'auth spotify' in text, 'auth spotify'
assert 'auth youtube' in text, 'auth youtube'
assert 'auth status' in text, 'auth status'
assert 'auth logout' in text, 'auth logout'
PY
```

## Dispatch 0559 — 181.04
Working directory: `repository root`

```bash
bash -n scripts/verify-all.sh
```

```bash
grep -E 'pytest|pytest-cov' scripts/verify-all.sh
```

```bash
grep -E 'branch|--cov-branch' scripts/verify-all.sh
```

## Dispatch 0560 — 176.05
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'inspect youtube' in text, 'inspect youtube'
assert 'dry_run' in text, 'dry_run'
PY
```

## Dispatch 0561 — 181.05, 181.06
Working directory: `repository root`

```bash
bash -n scripts/verify-all.sh
```

```bash
grep -E '85|cov-fail-under' scripts/verify-all.sh
```

```bash
grep -F 'npm ci' scripts/verify-all.sh
```

## Dispatch 0562 — 176.06
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'create' in text, 'create'
assert 'merge' in text, 'merge'
assert 'replace' in text, 'replace'
PY
```

## Dispatch 0563 — 181.07
Working directory: `repository root`

```bash
bash -n scripts/verify-all.sh
```

```bash
grep -E 'typecheck|tsc' scripts/verify-all.sh
```

## Dispatch 0564 — 176.07
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'review list' in text, 'review list'
assert 'review apply' in text, 'review apply'
PY
```

## Dispatch 0565 — 181.08, 181.09
Working directory: `repository root`

```bash
bash -n scripts/verify-all.sh
```

```bash
grep -E 'npm (test|run test)' scripts/verify-all.sh
```

```bash
grep -F 'verify-pi-extension.sh' scripts/verify-all.sh
```

## Dispatch 0566 — 176.08
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'jobs' in text, 'jobs'
assert 'resume' in text, 'resume'
PY
```

## Dispatch 0567 — 181.10
Working directory: `repository root`

```bash
python3 scripts/validate-build-plan.py docs/build/pi-playlist-bridge-plan.md docs/build/symbol-contracts.yaml
```

```bash
cd runtime && uv run pytest tests/contract/test_build_plan.py -q
```

## Dispatch 0568 — 181.11
Working directory: `repository root`

```bash
bash scripts/verify-all.sh
```

## Dispatch 0569 — 181.12
Working directory: `repository root`

```bash
bash scripts/test-verify-all-failfast.sh && cd runtime && uv run pytest tests/contract/test_verify_all_pipeline.py -q && cd .. && bash scripts/verify-all.sh
```

## Dispatch 0570 — 176.09
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'json' in text, 'json'
assert 'jsonl' in text, 'jsonl'
assert 'csv' in text, 'csv'
assert 'report' in text, 'report'
PY
```

## Dispatch 0571 — 176.10
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'youtube-to-spotify' in text, 'youtube-to-spotify'
assert 'oauth' in text, 'oauth'
assert 'rapidfuzz' in text, 'rapidfuzz'
PY
```

## Dispatch 0572 — 176.11
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'ytmusicapi' in text, 'ytmusicapi'
assert 'spotify source' in text, 'spotify source'
assert 'youtube destination' in text, 'youtube destination'
assert 'deferred' in text, 'deferred'
PY
```

## Dispatch 0573 — 176.12
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('README.md'); assert p.is_file()
text=p.read_text().lower()
assert 'spotdl' in text, 'spotdl'
assert 'ffmpeg' in text, 'ffmpeg'
assert 'attribution' in text, 'attribution'
PY
```

## Dispatch 0574 — 178.01
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('config.example.toml'); assert p.is_file()
text=p.read_text().lower()
assert text.strip()
PY
```

## Dispatch 0575 — 178.02
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('config.example.toml'); assert p.is_file()
text=p.read_text().lower()
assert text.strip()
PY
```

## Dispatch 0576 — 178.03
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('config.example.toml'); assert p.is_file()
text=p.read_text().lower()
assert text.strip()
PY
```

## Dispatch 0577 — 178.04
Working directory: `repository root`

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('config.example.toml'); assert p.is_file()
text=p.read_text().lower()
assert text.strip()
PY
```

## Dispatch 0578 — 179.01
Working directory: `repository root`

```bash
bash -n scripts/install.sh
```

## Dispatch 0579 — 179.02
Working directory: `repository root`

```bash
playlist-bridge version
```

## Dispatch 0580 — 179.03
Working directory: `extension`

```bash
npm ci
```

## Dispatch 0581 — 179.04, 179.05
Working directory: `repository root`

```bash
bash -n scripts/install.sh
```

## Dispatch 0582 — 180.01
Working directory: `repository root`

```bash
bash -n scripts/uninstall.sh
```

## Dispatch 0583 — 180.02
Working directory: `repository root`

```bash
bash -n scripts/uninstall.sh
```

## Dispatch 0584 — 180.03
Working directory: `repository root`

```bash
bash -n scripts/uninstall.sh
```

## Dispatch 0585 — 180.04
Working directory: `repository root`

```bash
bash -n scripts/uninstall.sh
```

## Dispatch 0586 — 180.05
Working directory: `repository root`

```bash
bash -n scripts/uninstall.sh
```

## Dispatch 0587 — 187.01
Working directory: `repository root`

```bash
rm -rf runtime/dist
```

```bash
(cd runtime && uv run python -m build --wheel)
```

```bash
test -n "$(find runtime/dist -name '*.whl' -print -quit)"
```

## Dispatch 0588 — 187.02
Working directory: `repository root`

```bash
(cd runtime && uv run python -m build --sdist)
```

```bash
test -n "$(find runtime/dist -name '*.tar.gz' -print -quit)"
```

## Dispatch 0589 — 187.03
Working directory: `repository root`

```bash
(cd extension && npm pack --dry-run)
```

```bash
(cd extension && npm pack)
```

```bash
test -n "$(find extension -maxdepth 1 -name '*.tgz' -print -quit)"
```

## Dispatch 0590 — 187.04
Working directory: `repository root`

```bash
set -euo pipefail
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

WHEEL=$(find runtime/dist -name '*.whl' -print -quit)
TGZ=$(find extension -maxdepth 1 -name '*.tgz' -print -quit)
test -n "$WHEEL"
test -n "$TGZ"

python3 -m venv "$TMP/venv"
"$TMP/venv/bin/pip" install "$WHEEL"
"$TMP/venv/bin/playlist-bridge" version

mkdir -p "$TMP/packed-extension"
tar -xzf "$TGZ" -C "$TMP/packed-extension"
test -f "$TMP/packed-extension/package/package.json"
(
  cd "$TMP/packed-extension/package"
  npm install --omit=dev --ignore-scripts
)
PI_EXTENSION_PATH="$TMP/packed-extension/package" bash scripts/verify-pi-extension.sh
```

## Dispatch 0591 — 188.01
Working directory: `repository root`

- Open `docs/acceptance/final-e2e.md` and add a section headed `Dispatch 0574 — 188.01`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Call the registered auth tool for the selected YouTube and Spotify profiles.
- Record concrete evidence proving: Both profiles report authenticated.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/final-e2e.md`; otherwise mark FAIL.

## Dispatch 0592 — 188.02
Working directory: `repository root`

- Open `docs/acceptance/final-e2e.md` and add a section headed `Dispatch 0575 — 188.02`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Request the owned YouTube playlist transfer in dry-run mode.
- Record concrete evidence proving: No destination write occurs and reports are returned.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/final-e2e.md`; otherwise mark FAIL.

## Dispatch 0593 — 188.03
Working directory: `repository root`

- Open `docs/acceptance/final-e2e.md` and add a section headed `Dispatch 0576 — 188.03`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: List unresolved decisions and apply explicit choices where needed.
- Record concrete evidence proving: Corrections are persisted.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/final-e2e.md`; otherwise mark FAIL.

## Dispatch 0594 — 188.04
Working directory: `repository root`

- Open `docs/acceptance/final-e2e.md` and add a section headed `Dispatch 0577 — 188.04`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Execute create mode using the reviewed job/request.
- Record concrete evidence proving: A Spotify destination is created with accepted items.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/final-e2e.md`; otherwise mark FAIL.

## Dispatch 0595 — 188.05
Working directory: `repository root`

- Open `docs/acceptance/final-e2e.md` and add a section headed `Dispatch 0578 — 188.05`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Inspect the verification result and destination playlist.
- Record concrete evidence proving: Expected and actual URI order match.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/final-e2e.md`; otherwise mark FAIL.

## Dispatch 0596 — 188.06
Working directory: `repository root`

- Open `docs/acceptance/final-e2e.md` and add a section headed `Dispatch 0579 — 188.06`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Run the relevant repeat/resume path using persisted state.
- Record concrete evidence proving: No unintended duplicate writes occur.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/final-e2e.md`; otherwise mark FAIL.

## Dispatch 0597 — 188.07
Working directory: `repository root`

- Open `docs/acceptance/final-e2e.md` and add a section headed `Dispatch 0580 — 188.07`.
- Record the exact date/time, operating system, CLI/package version, account profile aliases, and non-secret source/destination IDs used.
- Perform this action exactly: Open the returned JSON/CSV/diagnostic paths and compare counts, decisions, and verification.
- Record concrete evidence proving: Pi returns the verified playlist plus valid report paths.
- Record the exact command or Pi tool invocation, exit/result status, observed counts/IDs, and report paths; redact tokens, OAuth codes, passwords, and client secrets.
- Record cleanup performed or explicitly state why no cleanup is required.
- Mark the dispatch PASS only when every item above is present in `docs/acceptance/final-e2e.md`; otherwise mark FAIL.
