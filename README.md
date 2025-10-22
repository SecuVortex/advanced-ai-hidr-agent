# Multi-Agent Host Intrusion Detection and Response System

This repository contains the source code for my final project for the Agentic AI Developer Certification Program, Module 2. It is a sophisticated, multi-agent Host Intrusion Detection and Response (HIDR) system designed to analyze and neutralize security threats in real-time.

## Project Overview

This system is built around a team of specialized AI agents that collaborate to provide a robust security solution. Each agent has a distinct role, and they work together under the coordination of an orchestration framework to analyze suspicious files and processes.

### Key Features

*   **Multi-Agent Architecture:** The system is composed of five specialized agents:
    *   **Detection Agent:** Monitors for suspicious activity and initiates the analysis workflow.
    *   **Intelligence Agent:** Enriches the analysis with external threat intelligence from sources like VirusTotal.
    *   **Analyst Agent:** Uses a Large Language Model to perform an in-depth, AI-powered analysis of the threat.
    *   **Coordinator Agent:** Synthesizes the findings from the other agents to determine the threat level and recommend a course of action.
    *   **Response Agent:** Executes the final response action, which can range from allowing the process to continue to terminating it and quarantining the associated files.
*   **Orchestration:** The agents are orchestrated using the `LangGraph` framework, which allows for a flexible and powerful workflow.
*   **Tool Integration:** The agents are equipped with a variety of tools to aid in their analysis, including:
    *   **VirusTotal Tool:** Queries the VirusTotal API for file reputation data.
    *   **Process Tools:** Provides utilities for interacting with system processes.
    *   **Security Tools:** A collection of tools for performing security-related tasks like file hashing and suspicious path detection.
*   **Human-in-the-Loop:** The system includes an optional "human-in-the-loop" feature, which allows a human operator to make the final decision on how to respond to a threat.

## Getting Started

### Prerequisites

*   Python 3.8+
*   An API key from [VirusTotal](https://www.virustotal.com/gui/my-apikey)
*   An API key from [Google AI](https://makersuite.google.com/app/apikey) (for the Analyst Agent)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/advanced-ai-hidr-agent.git
    cd advanced-ai-hidr-agent
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file in the root of the project by copying the example file:
    ```bash
    cp .env.example .env
    ```

2.  Open the `.env` file and add your API keys:
    ```
    VIRUSTOTAL_API_KEY="your_virustotal_api_key_here"
    GOOGLE_API_KEY="your_google_api_key_here"
    ```

### Usage

The main entry point for the system is the `core/multiagent_monitor.py` file. You can run it directly to see a test case in action:

```bash
python3 core/multiagent_monitor.py
```

This will trigger an analysis of a simulated suspicious process and print the results to the console.
