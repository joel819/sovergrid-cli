# SoverGrid CLI

**The one-click, un-censorable decentralized AWS.**

📚 **[Read the Official Developer Documentation](https://sovergrid-docs.vercel.app)**

SoverGrid is an open-source command-line tool that deploys your applications to decentralized networks (Akash, Filecoin, Spheron, Golem) with a single command. No rewriting code. No centralized gatekeepers. No surprise bills.

## Why SoverGrid?

Traditional cloud platforms (AWS, Railway, Vercel) can shut down your server, spike your bill, or censor your deployment at any time. SoverGrid routes your code to decentralized infrastructure where no single company controls the off switch.

**For Web2 Developers:** You don't need to learn blockchain. Write your normal Python or Node.js app, and SoverGrid handles the rest. It auto-generates Dockerfiles, calculates costs, and deploys to the cheapest available decentralized network.

**For Web3 Builders:** Deployments cost a flat $5 fee in USDC. Every transaction is transparent and payment is instantly verified on-chain.

## Current Status (Beta Phase 1 - Live Demo)

SoverGrid is currently in **Beta Phase 1**, designed specifically as a working proof-of-concept for investors and early developers. 

**What is currently working 100% (The Financial Plumbing):**
- **Web3 Payment Routing:** When a developer runs `sovergrid deploy`, the CLI securely connects to the blockchain, signs a transaction with their private key, and pays the decentralized network in USDC.
- **Smart Contract Automated Routing:** The Payment Router smart contract automatically directs the base cost to the provider and routes the Convenience Fee to the SoverGrid protocol.
- **Orchestration Logic:** The CLI properly parses the `sovergrid.yaml` file, calculates costs, and checks for budget limits.

**Infrastructure Provisioning:**
- **Decentralized Network Integration:** In this beta phase, the connection to Akash, Spheron, and Golem operates via our Phase 1 Testnet routing protocols.
- **Next Steps:** With V1 release, the protocol will transition from Testnet to Mainnet, connecting the live financial engine directly to Mainnet Akash, Filecoin, and Bittensor nodes.

## Quick Start

### 1. Installation

SoverGrid CLI is cross-platform. Ensure you have Python 3.8+ installed.

**Mac / Linux:**
```bash
pip3 install sovergrid
```

**Windows:**
```powershell
pip install sovergrid
```

### 2. Developer Authentication

Before deploying, you need to create a developer account. This allows you to manage deployments and (in the future) fund your wallet directly.

```bash
# Register a new account
sovergrid register
# (You will be prompted for an email and password)

# Log in to an existing account
sovergrid login
```

### 3. Get Testnet Funds (Beta Only)

Since the CLI requires testnet USDC to deploy, you can instantly fund your wallet using the built-in faucet:

```bash
sovergrid faucet
```

### 4. Deploy Your App

```bash
# Initialize your project
cd my-web-app
sovergrid init

# Test your deployment locally for free via Docker
sovergrid dev

# Deploy to the decentralized cloud
sovergrid deploy
```

### 5. Launch Your Own Token (Optional)

If your project needs its own cryptocurrency or governance token, SoverGrid can deploy a standard ERC-20 contract for you directly from the CLI. No Solidity knowledge required.

```bash
sovergrid token
# You will be prompted for:
#   Token Name:   My Project Token
#   Token Symbol: MPT
#   Total Supply: 1000000
#   Network:      sepolia (testnet) or mainnet
```

Once deployed, you will receive a contract address. Add it to your `sovergrid.yaml` under `token.contract_address` and your live website can connect to it automatically.

## Commands

### Full Stack

| Command | Description |
|---------|-------------|
| `sovergrid register` | Create a new SoverGrid developer account |
| `sovergrid login` | Authenticate your CLI |
| `sovergrid logout` | Log out of the CLI |
| `sovergrid faucet` | Mint $1,000 in free testnet USDC to test the CLI |
| `sovergrid init` | Scaffold a new project (generates sovergrid.yaml and Dockerfile) |
| `sovergrid dev` | Test your deployment locally via Docker for free |
| `sovergrid deploy` | Deploy your app to the decentralized network — costs $5 USDC |
| `sovergrid token` | Deploy your own ERC-20 token to the blockchain |
| `sovergrid status` | Check the status of your active deployment |
| `sovergrid info` | Display SoverGrid version and current config |

### Environment Variables (FREE)

These commands let you manage environment variables on a running deployment **without paying the $5 fee again**. They do not create a new compute lease — they only update the stored config.

| Command | Description |
|---------|-------------|
| `sovergrid env set KEY=VALUE` | Add or update one or more environment variables |
| `sovergrid env set K1=V1 K2=V2` | Set multiple variables in one command |
| `sovergrid env list` | List all configured variable keys (values are hidden) |
| `sovergrid env unset KEY` | Remove an environment variable |

Example workflow — fix a mistake without redeploying:

```bash
# You deployed but used the wrong database URL
sovergrid env set DATABASE_URL=postgresql://correct-host/db

# Confirm it was saved
sovergrid env list

# Remove an old variable you no longer need
sovergrid env unset OLD_API_KEY
```

### Standalone Services

Each service works **completely independently**. You do not need to use all of them.

| Command | Service | Description |
|---------|---------|-------------|
| `sovergrid train` | ML Training | Train AI models on decentralized GPUs (Bittensor, Gensyn, io.net) |
| `sovergrid store` | Storage | Pin files to decentralized storage (Filecoin, Arweave, IPFS) |
| `sovergrid db` | Database | Provision a decentralized database (Kwil SQL, Tableland on-chain SQL) |
| `sovergrid cdn` | CDN | Distribute content via decentralized CDN (4EVERLAND, Saturn) |
| `sovergrid secure` | Security | Integrate Web3 privacy, encryption, and KMS (Lit Protocol, Secret Network) |


## Smart Dependency Scanner

SoverGrid automatically scans your project for third-party SDKs and tells you exactly which environment variables are missing **before you pay a single cent**.

The scanner runs at two points:

**On `sovergrid init`** — immediately after your project is scaffolded, so you know what to configure before you even think about deploying.

**On `sovergrid deploy`** — as a pre-flight check before any blockchain payment is submitted. If required variables are missing, you are warned and given the option to cancel and fix them first.

### What It Detects

| Category | Services |
|----------|----------|
| **Payment** | Stripe, PayPal, Flutterwave, Paystack, Square, Braintree, Razorpay, Lemon Squeezy, Circle, Paddle |
| **Database** | PostgreSQL (psycopg2, asyncpg, SQLAlchemy), MongoDB, Redis, Prisma |
| **Email** | SendGrid, Resend, Mailgun, Postmark, AWS SES |
| **Auth** | Auth0, Clerk, Firebase, Supabase |
| **AI / LLM** | OpenAI, Anthropic (Claude), Google Gemini, Replicate, Pinecone |
| **Cloud** | AWS (boto3) |
| **Communication** | Twilio, Pusher, Slack |

### Example Output

When you run `sovergrid init` or `sovergrid deploy` in a project that uses Stripe and PostgreSQL:

```
  Dependency Scan Results
  ─────────────────────────────────────────
  💳 Stripe  (payment)
  🗄️  PostgreSQL / SQLAlchemy  (database)

  Missing Environment Variables Detected:
  These are required for your detected SDKs to work.
  Set them now with: sovergrid env set KEY=value

  Stripe:
    STRIPE_SECRET_KEY      — Secret API key (sk_live_...)
    STRIPE_PUBLISHABLE_KEY — Publishable key (pk_live_...)

  PostgreSQL:
    DATABASE_URL           — postgresql://user:pass@host:5432/db
```

You can then set them instantly without redeploying:

```bash
sovergrid env set STRIPE_SECRET_KEY=sk_live_xxx STRIPE_PUBLISHABLE_KEY=pk_live_xxx
sovergrid env set DATABASE_URL=postgresql://user:pass@host:5432/mydb
```

The scanner reads `requirements.txt`, `package.json`, `Pipfile`, and `pyproject.toml`. No code is sent to any server during the scan — it runs entirely on your machine.

## Pricing & Services

SoverGrid uses **different payment models for different services** because not every service has the same cost structure. A web app has predictable monthly costs. AI training is variable. A token deployment is a one-time action. Charging a flat price for all of them would either rip off users or lose you money.

Every payment comes directly from the developer's wallet. SoverGrid never fronts compute costs. The developer's funds pay the provider. SoverGrid takes a transparent margin on every transaction.

---

### Service 1 — Compute (Web App / API Hosting)

**Provider:** Akash Network (primary), Spheron (fallback)
**Payment model:** One-time deployment fee + flat monthly subscription

| Fee | Amount | What it covers |
|-----|--------|---------------|
| Deployment fee | **$5 USDC** | Container build, Akash lease setup, orchestration |
| Monthly subscription | **$10 USDC/month** | Ongoing compute — 1 CPU, 512MB RAM, always-on |

**How it works:** You pay $5 when you deploy. Your monthly $10 is automatically pulled from your wallet on the same date every month. If your wallet balance drops to zero, your app enters a 7-day grace period before being suspended.

**Your cost (provider side):** ~$1.50/month on Akash
**Your margin:** ~$8.50/month per app

```bash
# In sovergrid.yaml
compute:
  enabled: true
  cpu: 1
  memory: 512Mi
  port: 8080
```

---

### Service 2 — Decentralized Storage (Filecoin / IPFS)

**Provider:** Lighthouse (Filecoin + IPFS pinning)
**Payment model:** One-time setup fee + monthly flat per storage tier

| Fee | Amount | What it covers |
|-----|--------|---------------|
| Setup fee | **$2 USDC** | Wallet registration, pinning setup |
| Monthly (Starter) | **$5 USDC/month** | Up to 10GB stored on Filecoin |
| Monthly (Growth) | **$12 USDC/month** | Up to 50GB stored on Filecoin |
| Monthly (Scale) | **$30 USDC/month** | Up to 200GB stored on Filecoin |

**How it works:** Files are pinned to IPFS and stored on Filecoin with redundancy. They are accessible via a permanent IPFS CID that never changes, even if SoverGrid goes offline.

**Your cost (provider side):** ~$0.40-1.50/month depending on tier
**Your margin:** ~$4-10/month per storage subscriber

```bash
sovergrid store upload ./my-folder
sovergrid store list
```

---

### Service 3 — Decentralized Database (Kwil SQL / Tableland)

**Provider:** Kwil (SQL on-chain), Tableland (EVM-native SQL)
**Payment model:** One-time setup fee + monthly flat subscription

| Fee | Amount | What it covers |
|-----|--------|---------------|
| Setup fee | **$3 USDC** | Database provisioning, schema deployment |
| Monthly | **$8 USDC/month** | Query execution, data storage up to 1GB |

**How it works:** Your database runs on a decentralized SQL network. You query it exactly like PostgreSQL using standard SQL. No centralized database provider can delete your data.

**Your cost (provider side):** ~$1/month
**Your margin:** ~$7/month per database subscriber

```bash
sovergrid db create --name mydb --schema ./schema.sql
sovergrid db query "SELECT * FROM users LIMIT 10"
```

---

### Service 4 — CDN (Content Delivery Network)

**Provider:** 4EVERLAND, Saturn (decentralized CDN)
**Payment model:** One-time setup fee + monthly flat

| Fee | Amount | What it covers |
|-----|--------|---------------|
| Setup fee | **$2 USDC** | Domain routing, edge node registration |
| Monthly | **$5 USDC/month** | Up to 50GB bandwidth, global edge caching |

**How it works:** Your static files (images, videos, JavaScript bundles) are served from decentralized edge nodes worldwide. Faster than centralized CDNs in most regions. No single company controls your content delivery.

**Your cost (provider side):** ~$0.50/month
**Your margin:** ~$4.50/month per CDN subscriber

```bash
sovergrid cdn deploy ./dist
```

---

### Service 5 — AI / ML Training (GPU Compute)

**Provider:** io.net, Bittensor, Gensyn
**Payment model:** Pay-per-use from vault balance (NOT a flat monthly subscription)

| Fee | Amount | What it covers |
|-----|--------|---------------|
| Per GPU hour | **$0.80 USDC/hr** | Decentralized GPU compute for model training |

**This is the most important one to understand.** AI training costs are variable. Someone can use 1 GPU hour or 10,000 GPU hours in a month. A flat subscription would mean SoverGrid either overcharges light users or loses money on heavy users.

Instead, the developer pre-funds their SoverGridVault with USDC. Every GPU hour consumed pulls $0.80 from their vault. When the vault runs low, they top it up. When the vault is empty, training pauses automatically.

**You never front GPU costs.** The money is always in the developer's vault, not your pocket.

**Your cost (provider side):** ~$0.30/GPU hour on decentralized networks
**Your margin:** ~$0.50/GPU hour

**Compare to centralized alternatives:**
- AWS SageMaker: $3.06–$32.77/hr
- Google Cloud GPU: $2.48–$24.48/hr
- Lambda Labs: $0.80–$8.00/hr
- **SoverGrid: $0.80/hr** — powered by decentralized GPU networks

```bash
sovergrid train --model ./train.py --gpu A100 --hours 10
# Estimated cost: 10 × $0.80 = $8.00 USDC from your vault
```

---

### Service 6 — Token Deployment (ERC-20 Smart Contract)

**Provider:** Ethereum / Base / Polygon (your choice)
**Payment model:** One-time flat fee — no monthly charge

| Fee | Amount | What it covers |
|-----|--------|---------------|
| Deployment fee | **$20 USDC** | Smart contract compilation, deployment, verification |

**How it works:** SoverGrid deploys a standard ERC-20 token contract on your chosen network. The contract is verified on-chain and ownership is transferred to your wallet immediately. You pay once and the token lives on the blockchain forever.

**Your cost (provider side):** $2–5 in gas fees on Base network
**Your margin:** ~$15–18 per token deployed

```bash
sovergrid token deploy   --name "MyToken"   --symbol "MTK"   --supply 1000000   --network base
```

---

## Pricing Summary

| Service | Deploy Fee | Ongoing Cost | Model |
|---------|-----------|--------------|-------|
| Compute (Web App) | $5 | $10/month | Subscription |
| Storage (Filecoin) | $2 | $5–30/month | Tiered subscription |
| Database (Kwil) | $3 | $8/month | Subscription |
| CDN | $2 | $5/month | Subscription |
| AI Training (GPU) | None | $0.80/GPU hour | Pay-per-use from vault |
| Token Deployment | $20 | None | One-time |

## Cost Transparency

SoverGrid publishes its infrastructure costs openly so you know exactly where your money goes.

| Service | You Pay | Provider Cost | SoverGrid Margin |
|---------|---------|---------------|-----------------|
| Compute | $10/mo | ~$1.50/mo | ~$8.50/mo (85%) |
| Storage (10GB) | $5/mo | ~$0.40/mo | ~$4.60/mo (92%) |
| Database | $8/mo | ~$1.00/mo | ~$7.00/mo (87%) |
| CDN | $5/mo | ~$0.50/mo | ~$4.50/mo (90%) |
| AI Training | $0.80/hr | ~$0.30/hr | ~$0.50/hr (62%) |
| Token Deploy | $20 (once) | ~$3.00 gas | ~$17.00 (85%) |

Traditional cloud providers (AWS, GCP, Azure) charge 300–1000% markups on compute while hiding their infrastructure costs. SoverGrid uses cheaper decentralized infrastructure and shows you the numbers openly.

## Green Compute

SoverGrid supports eco-friendly deployments. By adding `green: true` to your `sovergrid.yaml`, your code will only be routed to providers that are powered by renewable energy. This feature ensures that your infrastructure has a lower carbon footprint, and it will expand as more green-certified DePIN nodes join the network.

## Configuration

SoverGrid uses a `sovergrid.yaml` file in your project root. Run `sovergrid init` to generate one automatically.

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

# --- Environment Variables ---
# Inject secrets into your container at runtime.
# These are encrypted and never stored in plain text on-chain.
# Works exactly like Railway's Variables tab or Docker --env-file.
env:
  DATABASE_URL: "postgresql://user:pass@host/db"
  STRIPE_SECRET_KEY: "sk_live_xxxx"
  NODE_ENV: "production"
  OPENAI_API_KEY: "sk-xxxx"

# --- Token Launch (Optional) ---
# Deploy your own ERC-20 token to the blockchain alongside your app.
# Uncomment this block and run: sovergrid token
# token:
#   name: "My Project Token"
#   symbol: "MPT"
#   supply: 1000000
#   network: "sepolia"   # use 'mainnet' when ready to go live
```

### Environment Variables Explained

The `env:` block works exactly like environment variables on Railway, Heroku, or Vercel. The values you put here are injected directly into your container when it boots on the decentralized network. Your app reads them with `os.environ.get("DATABASE_URL")` or `process.env.DATABASE_URL` exactly the same as in traditional cloud.

> **Security note:** Never commit real API keys to your `sovergrid.yaml`. Use the `env:` block only for values you are comfortable having in your project config. For production secrets, use `sovergrid.yaml` to reference environment variable names and set the real values in your local `.env` file instead.

## Cost Breakdown

SoverGrid simplifies pricing with a unified, predictable model.

| Component | Cost | Purpose |
|-----------|------|---------|
| Flat Deployment Fee | **$5.00 USDC** | Complete deployment onto the decentralized network. No hidden markup, no percentage fees. |

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
|                 |     |  Service Router  |     |  Bittensor (ML/AI)      |
|  sovergrid.yaml |     |                  |     |  Kwil      (Database)  |
|                 |     |  Services:       |     |  4EVERLAND (CDN)        |
+-----------------+     |   compute.py     |     |                         |
                        |   database.py    |     |  Payment Router         |
                        |   cdn.py         |     |  (Base Cost + Fee)      |
                        |   security.py    |     |  Lit Protocol(Security) |
                        +------------------+     +-------------------------+
```

### How Deployment Works (Behind the Scenes)

When you run `sovergrid deploy`, here is what happens to your code:
1. **Zip & Ship:** The CLI securely zips your local project and sends it to the SoverGrid Backend. It does *not* push your code to GitHub.
2. **Auto-Dockerizer:** The backend detects your framework (e.g., FastAPI, Next.js), auto-generates a `Dockerfile`, and builds your container image.
3. **Decentralized Registry:** Your compiled container image is pushed to the SoverGrid Container Registry (backed by decentralized storage like Filecoin). We use version tagging (`v1`, `v2`), meaning your old code is never deleted, and you can instantly rollback.
4. **Network Handoff:** The backend instructs the decentralized compute network (e.g., Akash) to pull your image from the registry and spin up your server.

This means you get the simplicity of Vercel/Heroku, with the censorship-resistance of Web3.

SoverGrid's services are fully modular. You only use the services you need, and they operate completely independently from one another.

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
| `token-launch.yaml` | Deploy a website + launch an ERC-20 token | `sovergrid deploy` then `sovergrid token` |
| `full-stack.yaml` | Complete infrastructure (all 5 services) | All commands |

## License

MIT
