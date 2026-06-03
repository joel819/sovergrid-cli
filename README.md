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

### Full Stack

| Command | Description |
|---------|-------------|
| `sovergrid init` | Scaffold a new project (generates sovergrid.yaml and Dockerfile) |
| `sovergrid deploy` | Deploy your app to the decentralized network (compute + storage) |
| `sovergrid status` | Check the status of your active deployment |
| `sovergrid info` | Display SoverGrid version and current config |

### Standalone Services

Each service works **completely independently**. You do not need to use all of them.

| Command | Service | Description |
|---------|---------|-------------|
| `sovergrid train` | ML Training | Train AI models on decentralized GPUs (Bittensor, Gensyn, io.net) |
| `sovergrid store` | Storage | Pin files to decentralized storage (Filecoin, Arweave, IPFS) |
| `sovergrid db` | Database | Provision a decentralized database (Kwil SQL, Polybase NoSQL) |
| `sovergrid cdn` | CDN | Distribute content via decentralized CDN (Fleek, Saturn) |

## Green Compute

SoverGrid supports eco-friendly deployments. By adding `green: true` to your `sovergrid.yaml`, your code will only be routed to providers that are powered by renewable energy. This feature ensures that your infrastructure has a lower carbon footprint, and it will expand as more green-certified DePIN nodes join the network.

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
|                 |     |                  |     |                         |
|  Python/Node    |     |  Config Validator |     |  Akash     (Compute)   |
|  Application    | --> |  Auto-Dockerizer | --> |  Filecoin  (Storage)   |
|                 |     |  Service Router  |     |  Bittensor (ML/AI)     |
|  sovergrid.yaml |     |                  |     |  Kwil      (Database)  |
|                 |     |  Services:       |     |  Fleek     (CDN)       |
+-----------------+     |   compute.py     |     |                         |
                        |   storage.py     |     |  Smart Contract Vault   |
                        |   ml_training.py |     |  (60/20/15/5 split)    |
                        |   database.py    |     |                         |
                        |   cdn.py         |     +-------------------------+
                        +------------------+
```

Each service is an **independent Python module**. They share a common `BaseService` abstract class but have zero dependencies on each other. A bug in `ml_training.py` cannot break `compute.py`.

## Examples

The `examples/` folder contains ready-to-use configs for every use case:

| File | Use Case | Command |
|------|----------|---------|
| `sovergrid.yaml` | All services combined (default) | `sovergrid deploy` |
| `compute-only.yaml` | Just deploy an app to decentralized compute | `sovergrid deploy -c examples/compute-only.yaml` |
| `storage-only.yaml` | Just pin files to Filecoin/IPFS | `sovergrid store -c examples/storage-only.yaml` |
| `ml-training-only.yaml` | Just train an AI model on decentralized GPUs | `sovergrid train -c examples/ml-training-only.yaml` |
| `database-only.yaml` | Just provision a decentralized database | `sovergrid db -c examples/database-only.yaml` |
| `cdn-only.yaml` | Just push content to a decentralized CDN | `sovergrid cdn -c examples/cdn-only.yaml` |
| `full-stack.yaml` | Complete infrastructure (all 5 services) | All commands |

## License

MIT
