# Gloaks-CLI 🕵️‍♂️

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-linux%7Cmacos%7Cwindows-lightgrey)

> **"Visibility is the first step to security."**

**Gloaks** is a high-performance, modular **OSINT (Open Source Intelligence)** and **Network Reconnaissance** framework. Built on modern async technologies, it aggregates disparate data points into a unified security view.

![Gloaks CLI](https://via.placeholder.com/800x400?text=Gloaks+CLI+Demo)

## 🚀 Key Features v3.0

* **⚡ Async Core:** Built on `asyncio` and `httpx` for blazing fast concurrent scanning.
* **🌐 Geo-Reconnaissance:** Instantly map target IPs to physical locations (City, Country, ISP).
* **🔌 Async Port Scanning:** Non-blocking TCP connect scanning for critical services.
* **🧠 HTTP Analysis:** Deep inspection of headers, security flags (HSTS, CSP), and tech stack fingerprinting.
* **🔍 DNS Enumeration:** Rapid resolution of A, AAAA, MX, NS, and TXT records.
* **🛡️ Enterprise Security:** Strict scope validation and structured JSON audit logging.
* **🔌 API Mode:** Includes a `FastAPI` server for integration into security pipelines.

## 🛠️ Installation

Gloaks requires **Python 3.10+**.

### Quick Start (Linux/macOS)

```bash
# 1. Clone the repository
git clone https://github.com/SpiralKudlon/gloaks-cli.git
cd gloaks-cli

# 2. Run the installer
./scripts/install.sh

# 3. Activate environment
source venv/bin/activate

# 4. Verify installation
gloaks --help
```

### Docker

```bash
docker build -t gloaks .
docker run --rm gloaks --help
```

## 📖 Usage

### CLI Scans

**Basic Scan:**
```bash
gloaks scan example.com
```

**With Scope Validation (Recommended):**
Create a `scope.yaml` file to define authorized targets:
```yaml
allow:
  domains:
    - example.com
    - *.example.com
exclude:
  domains:
    - secret.example.com
```

Run scan with scope:
```bash
gloaks scan example.com --scope scope.yaml
```

**Export Results:**
```bash
gloaks scan example.com --output-file results.json
```

### API Mode

Start the REST API server:
```bash
uvicorn gloaks.api.app:app --host 0.0.0.0 --port 8000
```

Submit a scan:
```bash
curl -X POST http://localhost:8000/scans \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com"}'
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.