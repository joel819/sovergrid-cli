# SoverGrid CLI

**The one-click, un-censorable decentralized AWS.**

SoverGrid is an open-source command-line tool that deploys your applications to decentralized networks (Akash, Filecoin, Spheron, Golem) with a single command. No rewriting code. No centralized gatekeepers. No surprise bills.

## Why SoverGrid?

Traditional cloud platforms (AWS, Railway, Vercel) can shut down your server, spike your bill, or censor your deployment at any time. SoverGrid routes your code to decentralized infrastructure where no single company controls the off switch.

**For Web2 Developers:** You don't need to learn blockchain. Write your normal Python or Node.js app, and SoverGrid handles the rest. It auto-generates Dockerfiles, calculates costs, and deploys to the cheapest available decentralized network.

**For Web3 Builders:** Pay for deployments with USDC or the $SVR utility token. Every transaction is transparent, with fees automatically split via a smart contract.

## Quick Start

```bash
# Install
pip install sovergrid

# Initialize your project
cd my-web-app
sovergrid init

# Deploy to the decentralized cloud
sovergrid deploy
```

## Commands

| Command | Description |
|---------|-------------|
| `sovergrid init` | Scaffold a new project (generates sovergrid.yaml and Dockerfile) |
| `sovergrid deploy` | Deploy your app to the decentralized network |
| `sovergrid status` | Check the status of your active deployment |
| `sovergrid info` | Display SoverGrid version and current config |

## Configuration

SoverGrid uses a `sovergrid.yaml` file in your project root:

```yaml
app:
  name: "my-web-app"

compute:
  provider: "akash"
  region: "us-west"
  resources:
    cpu: 1
    memory: "512Mi"

storage:
  provider: "filecoin"

build:
  port: 8080

payment:
  token: "USDC"
  max_budget: 5.00
```

## Cost Breakdown

Every deployment fee is transparently split:

| Split | Percentage | Purpose |
|-------|-----------|---------|
| Compute Provider | 60% | Pays Akash/Spheron/Golem for server resources |
| SoverGrid Treasury | 20% | Funds development, legal, and marketing |
| SVR Stakers | 15% | Rewards token holders who secure the network |
| Auto-Liquidity | 5% | Automatically deepens the SVR/USDC liquidity pool |

## Supported Stacks

SoverGrid auto-detects your project and generates optimized Dockerfiles:

| Stack | Detection |
|-------|----------|
| Python | `requirements.txt` |
| Python (FastAPI) | `requirements.txt` containing `fastapi` |
| Node.js | `package.json` |
| Node.js (Next.js) | `package.json` containing `next` |

## Architecture

```
Developer's Laptop          SoverGrid CLI              Decentralized Networks
+-----------------+     +------------------+     +-------------------------+
|  Python/Node    | --> |  Config Validator | --> |  Akash (Compute)        |
|  Application    |     |  Auto-Dockerizer |     |  Filecoin (Storage)     |
|  sovergrid.yaml |     |  Orchestrator    |     |  Smart Contract (Fees)  |
+-----------------+     +------------------+     +-------------------------+
```

## License

MIT
