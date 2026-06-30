# SoverGrid — Akash Network Incubator Grant Application
**Applicant:** Joel Oyewole
**GitHub:** github.com/joel819/sovergrid-cli
**Grant Tier:** Incubator — $6,000 AKT
**Date:** May 2026 | **Last Updated:** June 2026

---

## Project Name
SoverGrid — The Open-Source Developer Platform for Decentralized Infrastructure

## Tagline
One CLI command. Deploy anywhere. No AWS. No censorship. Pay only for what you use.

---

## The Problem

Web3 compute networks like Akash have solved the hard infrastructure problem — decentralized, censorship-resistant, 60-85% cheaper than AWS.

But developer adoption is stalling because of one unsolved problem:

**Deploying to Akash requires managing AKT tokens, learning the Akash CLI, writing SDL files, and understanding Kubernetes — before a developer can deploy a single app.**

Compare this to Vercel:
```
vercel deploy    ← one command, app is live in 30 seconds
```

Or Railway:
```
railway up       ← one command, app is live in 30 seconds
```

There is no equivalent for Akash. This friction is why developers default back to centralized providers even when they want to decentralize.

SoverGrid fixes this.

---

## The Solution

```bash
pip install sovergrid
sovergrid deploy
```

SoverGrid is an open-source Python CLI that abstracts the full complexity of deploying to Akash. Developers write standard Python or Node.js applications — no SDL files, no AKT management, no Kubernetes knowledge required.

**What SoverGrid does automatically:**
- Detects the framework (FastAPI, Next.js, Express, etc.)
- Scans project dependencies and warns about missing environment variables before deploy
- Generates an optimized Dockerfile automatically
- Submits the deployment to Akash with correct SDL configuration
- Falls back to Spheron if Akash provider is unavailable
- Handles all payment routing via smart contract in USDC (no AKT required from the developer)
- Returns a live URL in under 60 seconds

---

## Why This Benefits Akash Network Directly

Every developer who uses SoverGrid is a new Akash tenant.

SoverGrid does not compete with Akash. SoverGrid is a distribution layer that brings Web2 developers — who have never heard of SDL files or AKT — directly onto the Akash network.

Current Akash user: experienced Web3 developer who knows the native CLI.
SoverGrid's target: any Python or Node.js developer who currently uses Vercel, Railway, or AWS.

That is a market of millions of developers who currently have no path to Akash.

**Important pricing note:** SoverGrid uses transparent, per-service pricing. Developers are never surprised by bills because the cost breakdown is shown before every deployment. No flat fees that underprice expensive workloads (like AI training) and no overcharging for simple ones.

---

## What Is Already Built

> **Progress Update (June 2026):** Since the initial grant submission, significant additional infrastructure has been completed beyond what was originally committed. The items marked [DONE] below were already present at submission. Items marked [NEW] have been completed since.

The SoverGrid CLI is live on GitHub at github.com/joel819/sovergrid-cli.
The SoverGrid Backend API is live on Railway at github.com/joel819/sovergrid-backend.

**CLI — Completed:**
- [DONE] `sovergrid init` — scaffolds project, auto-detects framework, generates Dockerfile
- [DONE] `sovergrid deploy` — reads config, verifies payment, routes to provider
- [DONE] `sovergrid train` — deploys ML training jobs to Bittensor/io.net/Gensyn
- [DONE] `sovergrid store` — pins files to Filecoin/Arweave/IPFS via Lighthouse
- [DONE] `sovergrid db` — provisions decentralized database (Kwil/Tableland)
- [DONE] `sovergrid cdn` — deploys to decentralized CDN (Saturn/4EVERLAND)
- [DONE] Provider Plugin Architecture (ABC base class) — new providers added with one Python file
- [DONE] Provider fallback chain — Akash → Spheron automatic failover
- [NEW] `sovergrid env set/list/unset` — manage environment variables on live deployments at no charge
- [NEW] `sovergrid subscription status/list/history` — full subscription management from CLI
- [NEW] Smart dependency scanner — scans `requirements.txt` / `package.json` on init and deploy, warns about missing environment variables for 40+ known SDKs (Stripe, OpenAI, PostgreSQL, Redis, etc.)

**Backend API — Completed:**
- [DONE] FastAPI backend deployed on Railway with JWT authentication
- [DONE] Web3 payment firewall — on-chain transaction verification before any deployment is processed
- [DONE] Provider strategy pattern — 6 DePIN providers behind a unified interface
- [NEW] Per-service pricing engine (`app/core/pricing.py`) — single source of truth for all service fees
- [NEW] Subscription billing system — `subscription_store.py` records every active deployment
- [NEW] Subscription monitor — daily billing cron via `POST /subscriptions/billing-run`, auto-collects USDC via `transferFrom`, full grace period and suspension lifecycle
- [NEW] `GET /pricing` public endpoint — CLI reads live pricing before showing cost to user
- [NEW] Demo/production toggle — single `DEMO_MODE` env var switches between simulated billing and live blockchain calls

**Current status:** All payment and subscription logic is complete and deployed. In `DEMO_MODE=True` (current), no real blockchain calls fire. Flipping `DEMO_MODE=False` and funding the treasury activates real USDC collection. The Akash real API integration (Milestone 1) is the remaining primary code item.

---

## Grant Milestones

### Milestone 1 — Real Akash API Integration ($4,000)
**Deliverable:** Replace mock `_simulate_provider_call()` in `services/akash_provider.py` with real Akash Network SDK calls.

Specifically:
- Integrate `akash-py` SDK for real SDL deployment submission
- Connect live Akash marketplace pricing API for real cost estimates
- Implement real lease creation, status polling, and endpoint retrieval
- End-to-end test: `sovergrid deploy` successfully deploys a real container to Akash mainnet and returns a live URL

**Timeline:** 6 weeks from grant approval
**Verification:** Live demo video showing real deployment + GitHub commit history

---

### Milestone 2 — Web3 Payment Routing Layer ($2,500)
**Deliverable:** Deploy USDC payment routing contract and subscription billing system to production.

> **Progress Update (June 2026):** The subscription billing architecture is already complete in demo mode. The remaining work for this milestone is deploying the smart contracts to Base mainnet, funding the treasury, and switching `DEMO_MODE=False`.

Specifically:
- [DONE] USDC payment router architecture — routes infrastructure cost to provider, SoverGrid keeps the service margin
- [DONE] Per-service pricing engine — compute $10/month, storage $5/month, AI training $0.80/GPU hour
- [DONE] Subscription monitor — daily `transferFrom` billing via cron, grace period, suspension, termination lifecycle
- [TODO] Deploy `SoverGridVault.sol` to Base mainnet
- [TODO] Connect treasury private key and fund for gas
- [TODO] Set `DEMO_MODE=False` in Railway

**Timeline:** 10 weeks from grant approval
**Verification:** Mainnet contract addresses + working demo of real USDC subscription collection

---

### Milestone 3 — Public Testnet Launch + Documentation ($2,500)
**Deliverable:** Public testnet where any developer can install SoverGrid and deploy a real app to Akash.

Specifically:
- PyPI publication (`pip install sovergrid` works globally)
- Full documentation at docs.sovergrid.network
- Video walkthrough: zero to deployed in under 5 minutes
- Akash community presentation (office hours or community call)
- 10 external developers successfully deployed using SoverGrid in testnet

**Timeline:** 14 weeks from grant approval
**Verification:** PyPI install count + 10 verified external deployments + community call recording

---

## Budget Breakdown

| Item | Amount | Purpose |
|---|---|---|
| Developer Time (14 Weeks) | $4,500 | Funding for the 14-week development sprint required to deliver Milestones 1, 2, and 3 |
| Infrastructure & API costs | $1,500 | Akash testnet deployments, RPC access, domain, docs hosting, and integration reserves |
| **Total** | **$6,000** | |

---

## About The Builder

**Joel Oyewole** — Founder of Nexus Arch, an AI automation agency. Builder of Invoice Sentinel (invoicesentinel.app), an AI-powered invoice recovery SaaS with 42+ active users built on FastAPI, Neo4j, and GPT-4o.

Member of the **NVIDIA 6G Developer Program** — researching decentralized edge infrastructure at the intersection of DePIN and next-generation wireless networks.

Computer Engineering student at Bahçeşehir Cyprus University.

Published researcher — "An Engineer Built a $1.79B Infrastructure System. Then Got Fired. Here's What Nobody Is Talking About." — 2,100+ impressions on LinkedIn, documenting the gap in DePIN developer tooling that SoverGrid addresses.

Based in Cyprus. Building in public since February 2026.

**GitHub:** github.com/joel819
**LinkedIn:** linkedin.com/in/joel-oyewole-51b614125
**X:** @joel_depin

---

## Open Source Commitment

SoverGrid is and will remain fully open source under the MIT License. All development funded by this grant will be publicly committed to github.com/joel819/sovergrid-cli with weekly progress updates posted to the Akash community forum.

---

## Why SoverGrid Will Succeed Where Others Have Not

**Fleek** ($30M raised) shut down its IPFS hosting product in January 2026 and pivoted to AI agent hosting. The Web3 developer community lost its most well-known decentralized hosting option overnight. This validates the need for a provider-agnostic layer like SoverGrid: when a single provider goes down, your entire deployment pipeline should not break.

**Spheron** ($7M raised) focuses on a marketplace model but does not solve the developer experience problem.

**Neither provides a one-command CLI that works with zero Web3 knowledge.**

SoverGrid's Provider Plugin Architecture means it is not competing with Akash or Spheron — it routes to all of them. When Fleek shut down, SoverGrid replaced it with 4EVERLAND in a single code change. As new DePIN compute networks launch, they integrate into SoverGrid by adding a single Python file. SoverGrid becomes the universal developer interface for all decentralized compute — with Akash as the primary and preferred provider.

---

## What Success Looks Like in 6 Months

```
pip install sovergrid
sovergrid deploy

[OK] Scanning project dependencies...
  → Stripe detected     STRIPE_SECRET_KEY [OK]
  → OpenAI detected     OPENAI_API_KEY [OK]

[OK] Calculating deployment cost...
  Services selected:  compute + storage
  Deploy fee:         $7.00 USDC (one-time)
  Monthly billing:    $15.00 USDC/month (auto-collected from vault)

[OK] App live at: https://myapp.sovergrid.network
[OK] Deployed on: Akash Network (EU-West)
[OK] Subscription active. Next billing: 2026-07-25
[OK] Manage with: sovergrid subscription status
```

Any developer. Any app. One command. Running on Akash.

---

*Full technical documentation, architecture diagrams, and whitepaper available at github.com/joel819/sovergrid-cli*
