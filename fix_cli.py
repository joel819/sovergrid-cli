import sys
content = open("sovergrid/orchestrator.py").read()
content = content.replace('log.error(f"Backend deployment failed: {str(e)}")', 'msg = str(e)\n        if hasattr(e, "response") and e.response is not None:\n            try:\n                msg = e.response.json().get("detail", str(e))\n            except:\n                pass\n        log.error(f"Backend deployment failed: {msg}")')
with open("sovergrid/orchestrator.py", "w") as f:
    f.write(content)
