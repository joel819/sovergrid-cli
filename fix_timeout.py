import sys
content = open("sovergrid/orchestrator.py").read()
content = content.replace('client = httpx.AsyncClient()', 'client = httpx.AsyncClient(timeout=60.0)')
with open("sovergrid/orchestrator.py", "w") as f:
    f.write(content)
