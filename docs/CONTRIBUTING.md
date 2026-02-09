This file is a "green flag" for senior engineers. It shows you know how to work in a team and set standards.

```markdown
# Contributing to Gloaks-CLI

First off, thank you for considering contributing to Gloaks! It's people like you that make the open-source community such an amazing place to learn, inspire, and create.

## 🛠 Development Setup

To start working on Gloaks, follow these steps to set up a consistent development environment:

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/gloaks-cli.git](https://github.com/YOUR_USERNAME/gloaks-cli.git)
    cd gloaks-cli
    ```
3.  **Create a virtual environment** (Recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  **Install development dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🧪 Testing

Before submitting a Pull Request, please ensure your code runs without errors.
* Currently, we perform manual testing by running `python main.py` against `scanme.nmap.org` (authorized testing target).
* *Upcoming:* We are implementing `pytest` for unit testing in v2.3.

## 📝 Coding Standards

* **Style:** We follow [PEP 8](https://peps.python.org/pep-0008/) guidelines.
* **Imports:** Keep imports organized (Standard Lib -> Third Party -> Local).
* **Comments:** Write docile code, but add comments for complex logic (especially in `scanner.py`).

## 🔏 Reporting Vulnerabilities

If you find a security vulnerability within Gloaks itself, please do **not** open a public issue. Email the maintainer directly at `[Your Email]`.