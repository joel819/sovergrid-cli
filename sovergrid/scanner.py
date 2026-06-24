"""
SoverGrid Dependency Scanner
Scans project files to detect third-party SDKs and warns the user
about required environment variables before deployment.

Detects payment providers, databases, email services, AI APIs, auth systems,
and more — then surfaces the exact env var names the user needs to configure.
"""
import json
import os
from pathlib import Path
from typing import NamedTuple

from sovergrid.logger import get_logger, Colors

log = get_logger(__name__)


# ─── SDK → Required Env Vars Registry ────────────────────────────────────────
#
# Format:
#   "package_name_fragment": {
#       "label": "Human-readable service name",
#       "category": "payment" | "database" | "email" | "auth" | "ai" | "cloud" | "other",
#       "env_vars": [
#           {"key": "ENV_VAR_NAME", "description": "What it is", "required": True/False}
#       ]
#   }
#
SDK_REGISTRY = {
    # ── Payment Providers ──────────────────────────────────────────────────────
    "stripe": {
        "label": "Stripe",
        "category": "payment",
        "env_vars": [
            {"key": "STRIPE_SECRET_KEY",      "description": "Secret API key (sk_live_...)",     "required": True},
            {"key": "STRIPE_PUBLISHABLE_KEY",  "description": "Publishable key (pk_live_...)",    "required": True},
            {"key": "STRIPE_WEBHOOK_SECRET",   "description": "Webhook signing secret",           "required": False},
        ],
    },
    "paypalrestsdk": {
        "label": "PayPal",
        "category": "payment",
        "env_vars": [
            {"key": "PAYPAL_CLIENT_ID",     "description": "PayPal app client ID",     "required": True},
            {"key": "PAYPAL_CLIENT_SECRET", "description": "PayPal app client secret", "required": True},
        ],
    },
    "@paypal": {
        "label": "PayPal (Node.js)",
        "category": "payment",
        "env_vars": [
            {"key": "PAYPAL_CLIENT_ID",     "description": "PayPal app client ID",     "required": True},
            {"key": "PAYPAL_CLIENT_SECRET", "description": "PayPal app client secret", "required": True},
        ],
    },
    "flutterwave": {
        "label": "Flutterwave",
        "category": "payment",
        "env_vars": [
            {"key": "FLW_SECRET_KEY",  "description": "Flutterwave secret key",  "required": True},
            {"key": "FLW_PUBLIC_KEY",  "description": "Flutterwave public key",  "required": True},
            {"key": "FLW_ENCRYPTION_KEY", "description": "Flutterwave encryption key", "required": False},
        ],
    },
    "rave-python": {
        "label": "Flutterwave (Rave)",
        "category": "payment",
        "env_vars": [
            {"key": "FLW_SECRET_KEY", "description": "Flutterwave secret key", "required": True},
            {"key": "FLW_PUBLIC_KEY", "description": "Flutterwave public key", "required": True},
        ],
    },
    "paystack": {
        "label": "Paystack",
        "category": "payment",
        "env_vars": [
            {"key": "PAYSTACK_SECRET_KEY", "description": "Paystack secret key (sk_live_...)", "required": True},
            {"key": "PAYSTACK_PUBLIC_KEY", "description": "Paystack public key (pk_live_...)", "required": True},
        ],
    },
    "pypaystack": {
        "label": "Paystack (Python)",
        "category": "payment",
        "env_vars": [
            {"key": "PAYSTACK_SECRET_KEY", "description": "Paystack secret key", "required": True},
        ],
    },
    "squareup": {
        "label": "Square",
        "category": "payment",
        "env_vars": [
            {"key": "SQUARE_ACCESS_TOKEN",    "description": "Square access token",    "required": True},
            {"key": "SQUARE_APPLICATION_ID",  "description": "Square application ID",  "required": True},
            {"key": "SQUARE_LOCATION_ID",     "description": "Square location ID",     "required": False},
        ],
    },
    "braintree": {
        "label": "Braintree (PayPal)",
        "category": "payment",
        "env_vars": [
            {"key": "BRAINTREE_MERCHANT_ID", "description": "Braintree merchant ID",  "required": True},
            {"key": "BRAINTREE_PUBLIC_KEY",  "description": "Braintree public key",   "required": True},
            {"key": "BRAINTREE_PRIVATE_KEY", "description": "Braintree private key",  "required": True},
        ],
    },
    "razorpay": {
        "label": "Razorpay",
        "category": "payment",
        "env_vars": [
            {"key": "RAZORPAY_KEY_ID",     "description": "Razorpay key ID",     "required": True},
            {"key": "RAZORPAY_KEY_SECRET", "description": "Razorpay key secret", "required": True},
        ],
    },
    "lemonsqueezy": {
        "label": "Lemon Squeezy",
        "category": "payment",
        "env_vars": [
            {"key": "LEMONSQUEEZY_API_KEY", "description": "Lemon Squeezy API key", "required": True},
            {"key": "LEMONSQUEEZY_STORE_ID", "description": "Your store ID",        "required": False},
        ],
    },
    "circle": {
        "label": "Circle (USDC Payments)",
        "category": "payment",
        "env_vars": [
            {"key": "CIRCLE_API_KEY", "description": "Circle API key", "required": True},
        ],
    },
    "paddle": {
        "label": "Paddle",
        "category": "payment",
        "env_vars": [
            {"key": "PADDLE_VENDOR_ID",     "description": "Paddle vendor ID",     "required": True},
            {"key": "PADDLE_VENDOR_AUTH_CODE", "description": "Paddle auth code",  "required": True},
        ],
    },

    # ── Databases ──────────────────────────────────────────────────────────────
    "psycopg2": {
        "label": "PostgreSQL (psycopg2)",
        "category": "database",
        "env_vars": [
            {"key": "DATABASE_URL", "description": "postgresql://user:pass@host:5432/db", "required": True},
        ],
    },
    "sqlalchemy": {
        "label": "SQLAlchemy",
        "category": "database",
        "env_vars": [
            {"key": "DATABASE_URL", "description": "postgresql:// or mysql:// connection string", "required": True},
        ],
    },
    "asyncpg": {
        "label": "AsyncPG (PostgreSQL)",
        "category": "database",
        "env_vars": [
            {"key": "DATABASE_URL", "description": "postgresql://user:pass@host:5432/db", "required": True},
        ],
    },
    "pymongo": {
        "label": "MongoDB (PyMongo)",
        "category": "database",
        "env_vars": [
            {"key": "MONGODB_URI", "description": "mongodb+srv://... connection string", "required": True},
        ],
    },
    "mongoose": {
        "label": "MongoDB (Mongoose)",
        "category": "database",
        "env_vars": [
            {"key": "MONGODB_URI", "description": "mongodb+srv://... connection string", "required": True},
        ],
    },
    "prisma": {
        "label": "Prisma ORM",
        "category": "database",
        "env_vars": [
            {"key": "DATABASE_URL", "description": "Database connection string", "required": True},
        ],
    },
    "redis": {
        "label": "Redis",
        "category": "database",
        "env_vars": [
            {"key": "REDIS_URL", "description": "redis://host:6379 connection string", "required": True},
        ],
    },
    "ioredis": {
        "label": "Redis (ioredis)",
        "category": "database",
        "env_vars": [
            {"key": "REDIS_URL", "description": "redis://host:6379 connection string", "required": True},
        ],
    },

    # ── Email Services ─────────────────────────────────────────────────────────
    "sendgrid": {
        "label": "SendGrid",
        "category": "email",
        "env_vars": [
            {"key": "SENDGRID_API_KEY", "description": "SendGrid API key (SG....)", "required": True},
        ],
    },
    "resend": {
        "label": "Resend",
        "category": "email",
        "env_vars": [
            {"key": "RESEND_API_KEY", "description": "Resend API key (re_...)", "required": True},
        ],
    },
    "mailgun": {
        "label": "Mailgun",
        "category": "email",
        "env_vars": [
            {"key": "MAILGUN_API_KEY",  "description": "Mailgun API key",  "required": True},
            {"key": "MAILGUN_DOMAIN",   "description": "Mailgun send domain", "required": True},
        ],
    },
    "postmark": {
        "label": "Postmark",
        "category": "email",
        "env_vars": [
            {"key": "POSTMARK_SERVER_TOKEN", "description": "Postmark server token", "required": True},
        ],
    },
    "ses": {
        "label": "AWS SES",
        "category": "email",
        "env_vars": [
            {"key": "AWS_ACCESS_KEY_ID",     "description": "AWS access key ID",     "required": True},
            {"key": "AWS_SECRET_ACCESS_KEY", "description": "AWS secret access key", "required": True},
            {"key": "AWS_SES_REGION",        "description": "SES region (e.g. us-east-1)", "required": True},
        ],
    },

    # ── Auth / Identity ────────────────────────────────────────────────────────
    "auth0": {
        "label": "Auth0",
        "category": "auth",
        "env_vars": [
            {"key": "AUTH0_DOMAIN",        "description": "your-tenant.auth0.com", "required": True},
            {"key": "AUTH0_CLIENT_ID",     "description": "Auth0 client ID",       "required": True},
            {"key": "AUTH0_CLIENT_SECRET", "description": "Auth0 client secret",   "required": True},
        ],
    },
    "@clerk": {
        "label": "Clerk",
        "category": "auth",
        "env_vars": [
            {"key": "CLERK_SECRET_KEY",       "description": "Clerk secret key (sk_live_...)",    "required": True},
            {"key": "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "description": "Clerk publishable key", "required": False},
        ],
    },
    "firebase-admin": {
        "label": "Firebase",
        "category": "auth",
        "env_vars": [
            {"key": "FIREBASE_PROJECT_ID",      "description": "Firebase project ID",          "required": True},
            {"key": "FIREBASE_PRIVATE_KEY",     "description": "Service account private key",  "required": True},
            {"key": "FIREBASE_CLIENT_EMAIL",    "description": "Service account client email", "required": True},
        ],
    },
    "supabase": {
        "label": "Supabase",
        "category": "auth",
        "env_vars": [
            {"key": "SUPABASE_URL",      "description": "Supabase project URL",  "required": True},
            {"key": "SUPABASE_ANON_KEY", "description": "Supabase anon key",     "required": True},
            {"key": "SUPABASE_SERVICE_ROLE_KEY", "description": "Service role key (server-side only)", "required": False},
        ],
    },

    # ── AI / LLM APIs ──────────────────────────────────────────────────────────
    "openai": {
        "label": "OpenAI",
        "category": "ai",
        "env_vars": [
            {"key": "OPENAI_API_KEY", "description": "OpenAI API key (sk-...)", "required": True},
        ],
    },
    "anthropic": {
        "label": "Anthropic (Claude)",
        "category": "ai",
        "env_vars": [
            {"key": "ANTHROPIC_API_KEY", "description": "Anthropic API key (sk-ant-...)", "required": True},
        ],
    },
    "google-generativeai": {
        "label": "Google Gemini",
        "category": "ai",
        "env_vars": [
            {"key": "GOOGLE_API_KEY", "description": "Google AI Studio API key", "required": True},
        ],
    },
    "replicate": {
        "label": "Replicate",
        "category": "ai",
        "env_vars": [
            {"key": "REPLICATE_API_TOKEN", "description": "Replicate API token", "required": True},
        ],
    },
    "pinecone": {
        "label": "Pinecone (Vector DB)",
        "category": "ai",
        "env_vars": [
            {"key": "PINECONE_API_KEY",     "description": "Pinecone API key",      "required": True},
            {"key": "PINECONE_ENVIRONMENT", "description": "Pinecone environment",  "required": True},
        ],
    },

    # ── Cloud / Infrastructure ─────────────────────────────────────────────────
    "boto3": {
        "label": "AWS (boto3)",
        "category": "cloud",
        "env_vars": [
            {"key": "AWS_ACCESS_KEY_ID",     "description": "AWS access key ID",      "required": True},
            {"key": "AWS_SECRET_ACCESS_KEY", "description": "AWS secret access key",  "required": True},
            {"key": "AWS_REGION",            "description": "AWS region",             "required": False},
        ],
    },

    # ── Communication ──────────────────────────────────────────────────────────
    "twilio": {
        "label": "Twilio (SMS / Voice)",
        "category": "other",
        "env_vars": [
            {"key": "TWILIO_ACCOUNT_SID", "description": "Twilio account SID",  "required": True},
            {"key": "TWILIO_AUTH_TOKEN",  "description": "Twilio auth token",   "required": True},
            {"key": "TWILIO_PHONE_NUMBER","description": "Twilio phone number",  "required": False},
        ],
    },
    "pusher": {
        "label": "Pusher (Real-time)",
        "category": "other",
        "env_vars": [
            {"key": "PUSHER_APP_ID",      "description": "Pusher app ID",       "required": True},
            {"key": "PUSHER_KEY",         "description": "Pusher key",          "required": True},
            {"key": "PUSHER_SECRET",      "description": "Pusher secret",       "required": True},
            {"key": "PUSHER_CLUSTER",     "description": "Pusher cluster",      "required": True},
        ],
    },
    "slack-sdk": {
        "label": "Slack",
        "category": "other",
        "env_vars": [
            {"key": "SLACK_BOT_TOKEN",    "description": "Slack bot token (xoxb-...)", "required": True},
            {"key": "SLACK_SIGNING_SECRET", "description": "Slack signing secret",     "required": False},
        ],
    },
}


class DetectedSDK(NamedTuple):
    package: str
    label: str
    category: str
    env_vars: list


def scan_project(project_dir: str = ".") -> list:
    """
    Scan a project directory for known SDK dependencies.

    Reads requirements.txt, package.json, Pipfile, and pyproject.toml.
    Returns a list of DetectedSDK objects for each match found.
    """
    project_path = Path(project_dir)
    detected = []
    seen_labels = set()

    all_deps = _collect_all_deps(project_path)

    for dep in all_deps:
        dep_lower = dep.lower().strip()
        for sdk_key, sdk_info in SDK_REGISTRY.items():
            if sdk_key.lower() in dep_lower or dep_lower.startswith(sdk_key.lower()):
                label = sdk_info["label"]
                if label not in seen_labels:
                    seen_labels.add(label)
                    detected.append(DetectedSDK(
                        package=dep,
                        label=label,
                        category=sdk_info["category"],
                        env_vars=sdk_info["env_vars"],
                    ))
                break

    return detected


def _collect_all_deps(project_path: Path) -> list:
    """Read all dependency files and return a flat list of package name strings."""
    deps = []

    # Python: requirements.txt
    req_file = project_path / "requirements.txt"
    if req_file.exists():
        for line in req_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                # Strip version specifiers: stripe>=5.0.0 → stripe
                pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split(">")[0].split("<")[0].split("[")[0]
                deps.append(pkg.strip())

    # Python: pyproject.toml (basic extraction)
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        for line in content.splitlines():
            if "=" in line and not line.strip().startswith("[") and not line.strip().startswith("#"):
                # Very basic: pick up quoted package names
                parts = line.split('"')
                for part in parts[1::2]:  # every other quoted string
                    if part and not part.startswith("^") and "." not in part[:2]:
                        deps.append(part.split(">=")[0].split("^")[0].strip())

    # Node.js: package.json
    pkg_json = project_path / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text())
            for section in ("dependencies", "devDependencies"):
                deps.extend(data.get(section, {}).keys())
        except json.JSONDecodeError:
            pass

    # Python: Pipfile (basic)
    pipfile = project_path / "Pipfile"
    if pipfile.exists():
        content = pipfile.read_text()
        in_packages = False
        for line in content.splitlines():
            if line.strip().startswith("[packages]"):
                in_packages = True
                continue
            if line.strip().startswith("[") and in_packages:
                in_packages = False
            if in_packages and "=" in line:
                pkg = line.split("=")[0].strip().strip('"')
                if pkg:
                    deps.append(pkg)

    return deps


def check_env_vars_set(detected_sdks: list, existing_env: dict = None) -> list:
    """
    Given a list of DetectedSDK objects, returns only the required env var keys
    that are NOT already set (either in the existing_env dict or in os.environ).
    """
    if existing_env is None:
        existing_env = {}

    missing = []
    for sdk in detected_sdks:
        for var in sdk.env_vars:
            key = var["key"]
            if var["required"] and key not in existing_env and key not in os.environ:
                missing.append({
                    "key": key,
                    "description": var["description"],
                    "service": sdk.label,
                    "category": sdk.category,
                })
    return missing


def print_scan_report(detected_sdks: list, missing_vars: list):
    """
    Print a formatted dependency scan report to the terminal.
    """
    if not detected_sdks:
        return

    CATEGORY_ICONS = {
        "payment":  "💳",
        "database": "🗄️ ",
        "email":    "📧",
        "auth":     "🔐",
        "ai":       "🤖",
        "cloud":    "☁️ ",
        "other":    "🔌",
    }

    log.info(f"\n  {Colors.BOLD}Dependency Scan Results{Colors.RESET}")
    log.info(f"  {Colors.DIM}{'─' * 40}{Colors.RESET}")

    for sdk in detected_sdks:
        icon = CATEGORY_ICONS.get(sdk.category, "📦")
        log.info(f"  {icon} {Colors.BOLD}{sdk.label}{Colors.RESET}  ({sdk.category})")

    if missing_vars:
        log.info(f"\n  {Colors.YELLOW}{Colors.BOLD}Missing Environment Variables Detected:{Colors.RESET}")
        log.info(f"  {Colors.DIM}These are required for your detected SDKs to work.{Colors.RESET}")
        log.info(f"  {Colors.DIM}Set them now with: sovergrid env set KEY=value{Colors.RESET}\n")

        # Group by service
        by_service = {}
        for var in missing_vars:
            svc = var["service"]
            if svc not in by_service:
                by_service[svc] = []
            by_service[svc].append(var)

        for service, vars_list in by_service.items():
            log.info(f"  {Colors.CYAN}{service}:{Colors.RESET}")
            for var in vars_list:
                log.info(f"    {Colors.YELLOW}{var['key']}{Colors.RESET}  — {var['description']}")
        log.info("")
    else:
        log.info(f"\n  {Colors.GREEN}All required environment variables appear to be set.{Colors.RESET}\n")
