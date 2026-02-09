# Gloaks-CLI 🕵️‍♂️

![Version](https://img.shields.io/badge/version-2.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-linux%7Cmacos%7Cwindows-lightgrey)

> **"Visibility is the first step to security."**

**Gloaks** is a lightweight, modular **OSINT (Open Source Intelligence)** and **Network Reconnaissance** framework. It aggregates disparate data points—GeoIP location, server headers, and open port metrics—into a single, unified terminal view for security researchers and system administrators.

![Gloaks Demo](assets/banner.png)

## 🚀 Key Features

* **🌐 Geo-Reconnaissance:** Instantly map target IPs to physical locations (City, Country, ISP).
* **🔌 Active Port Scanning:** Multi-threaded TCP connect scanning for critical vulnerabilities (FTP, SSH, HTTP, SQL).
* **🧠 HTTP Fingerprinting:** Automatic retrieval and analysis of server headers (Apache/Nginx versions) and security flags.
* **⚡ Zero-Config:** Built with minimal dependencies for instant deployment on Kali Linux, VPS, or local machines.

## 🛠️ Installation

Gloaks requires **Python 3.10+**.

```bash
# 1. Clone the repository
git clone [https://github.com/SpiralKudlon/gloaks-cli.git](https://github.com/SpiralKudlon/gloaks-cli.git)

# 2. Navigate to the directory
cd gloaks-cli

# 3. Install dependencies
pip install -r requirements.txt