# {{crew_name}} Crew

Welcome to the {{crew_name}} Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/prototype3/config/agents.yaml` to define your agents
- Modify `src/prototype3/config/tasks.yaml` to define your tasks
- Modify `src/prototype3/crew.py` to add your own logic, tools and specific args
- Modify `src/prototype3/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your flow and begin execution, run this from the root folder of your project:

```bash
crewai run
```

This command initializes the prototype3 Flow as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The prototype3 Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Setup in OneDrive Environment

Since this project is housed in a OneDrive folder, special setup is required to handle hardlink incompatibilities:

### Quick Start (Recommended)

Use the safe launcher script to run the flow:

```bash
safe_crewai.bat flow kickoff
```

Or simply:

```bash
safe_crewai.bat run
```

### Alternative Methods

1. **Direct Python execution:**
   ```
   python run_flow.py
   ```

2. **Standard CrewAI command** (may have hardlink issues with OneDrive):
   ```
   crewai flow kickoff
   ```

## Project Structure

- `src/prototype3/`: Main project code
  - `main.py`: Entry point and flow definition
  - `crews/`: Agent crew definitions
  - `tools/`: Custom tools for data analysis
  - `utils/`: Utility functions
- `data/`: Contains CSV data files
- `metadata/`: Contains metadata about data schemas
- `run_flow.py`: Alternative runner for OneDrive environments

## Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `PHOENIX_API_KEY`: Arize Phoenix API key

## Dependencies

This project requires Python 3.10-3.12.

## Support

For support, questions, or feedback regarding the {{crew_name}} Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
