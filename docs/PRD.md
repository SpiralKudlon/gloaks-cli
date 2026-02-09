1. Executive Summary

Gloaks-CLI is a lightweight, Python-based command-line interface designed to automate the initial phase of network reconnaissance ("Recon"). It aggregates disparate data points—GeoIP location, server headers, and open port status—into a single, unified terminal view.
1.1 Problem Statement

Security professionals and system administrators often rely on multiple disjointed tools (e.g., ping, nmap, browser plugins) to gather basic intelligence on a target. This process is manual, time-consuming, and fragmented.
1.2 Proposed Solution

Develop a unified CLI tool that accepts a target (Domain/IP) and synchronously executes multiple reconnaissance modules, presenting the data in a human-readable, color-coded format.
2. Target Audience (User Personas)

    The Penetration Tester: Needs a "quick-look" tool to identify low-hanging fruit (e.g., old server versions, open SSH ports) before launching heavy scanners.

    The System Administrator: Needs to audit their own infrastructure to ensure firewalls are correctly blocking non-essential ports.

    The Security Student: Needs a tool to understand the mechanics of HTTP requests and TCP handshakes.

3. Functional Requirements

The system must perform the following core functions:
3.1 Input Handling

    FR-01: The system shall accept a Target Domain (e.g., google.com) or IPv4 Address via CLI argument or interactive prompt.

    FR-02: The system must validate the input format. If the domain cannot be resolved to an IP, the system must return a descriptive error message and exit gracefully.

3.2 User Interface (UI)

    FR-03: The system shall display a distinct ASCII art banner reading "Gloaks" upon initialization.

    FR-04: The system shall use ANSI color coding to distinguish information hierarchy:

        Blue/Cyan: Section headers and informational logs.

        Green: Success states (e.g., Open Port, Target Locked).

        Red: Critical errors or warnings.

        Yellow: Data values (e.g., IP address, Lat/Long).

3.3 Reconnaissance Modules

    FR-05 (Geo-Location): The system must query an external API (e.g., ip-api.com) to retrieve the ISP, City, Country, and Lat/Long coordinates of the target.

    FR-06 (Port Scanning): The system must perform a TCP Connect Scan on a pre-defined list of "Top Critical Ports" (21, 22, 80, 443, 3306, 8080).

        Constraint: The default timeout per socket connection shall not exceed 0.5 seconds to ensure speed.

    FR-07 (Header Analysis): The system must perform an HTTP GET request to the target and extract key headers: Server, X-Powered-By, and Strict-Transport-Security.

4. Non-Functional Requirements (System Qualities)

    NFR-01 (Performance): The total execution time for a standard scan (assuming <100ms network latency) shall not exceed 5 seconds.

    NFR-02 (Compatibility): The application must be cross-platform, functioning on Linux (Kali/Ubuntu), macOS, and Windows.

    NFR-03 (Dependencies): The project must rely on minimal external libraries (requests, colorama, pyfiglet) to ensure easy installation via pip.

    NFR-04 (Error Handling): The system must handle network timeouts and connection refusals without crashing the Python interpreter.

5. User Interaction Flow

    Launch: User runs python main.py.

    Banner: Tool displays ASCII art and Version 2.1 tag.

    Prompt: Tool asks: [?] Enter Target Domain or IP:.

    Process:

        Log: [*] Resolving Target...

        Log: [+] Target Locked: 192.168.1.1

        Log: [*] Scanning HTTP Headers... -> Outputs headers.

        Log: [*] Quick Port Scan... -> Outputs open ports.

        Log: [*] Geolocation Data... -> Outputs location.

    Completion: Tool displays a completion footer and exits.

6. Technical Architecture
6.1 Tech Stack

    Language: Python 3.10+

    Networking: socket (Standard Lib), requests (HTTP).

    UI/UX: colorama (ANSI Colors), pyfiglet (ASCII Fonts).

6.2 Project Structure
Plaintext

gloaks-cli/
├── main.py            # Entry point & UI logic
├── scanner.py         # Business logic (API calls, Socket handling)
├── requirements.txt   # Dependency definitions
└── docs/              # Documentation
    └── PRD.md         # This document

7. Risks and Mitigation
Risk	Impact	Mitigation Strategy
API Rate Limiting	High (Geo-lookup fails)	Implement error handling for HTTP 429/403 responses from the Geolocation API.
Firewall Blocking	Medium (Port scan fails)	Use a conservative timeout (0.5s) and catch socket.timeout exceptions.
Legal Misuse	High	Include a strict "Disclaimer" in the CLI output and README forcing user acknowledgement.
8. Roadmap & Future Scope

    v2.1 (Current): Basic synchronous scanning and console output.

    v2.2: Export results to JSON/CSV file.

    v3.0: Implementation of asyncio for asynchronous port scanning (increasing speed by 10x) and support for custom port ranges.

Approval

    Lead Developer: SpiralKudlon

    Date Approved: Feb 9, 2026