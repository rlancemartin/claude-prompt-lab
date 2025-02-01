# 🏥 Dr Claude's Prompt Lab

A tool for analyzing and optimizing prompts for local reasoning models using Claude as an expert system. Designed to work with models running via Ollama that emit thinking/reasoning traces.

## Overview

Claude Prompt Lab helps you improve your prompts by:
- Running your prompt against a local reasoning model (via Ollama)
- Capturing and analyzing the model's thinking process
- Using Claude to evaluate responses and suggest prompt improvements
- Iteratively refining the prompt until desired performance is achieved

The tool generates a detailed "medical report" style analysis of each attempt, tracking the progression of prompt improvements.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dr-claudes-prompt-lab.git
cd dr-claudes-prompt-lab
```

2. (Recommended) Create a virtual environment:
```
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Ensure you have API keys for Claude and optionally LangSmith for tracing.
```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key
export LANGSMITH_API_KEY=your_langsmith_api_key
```

5. Download the Ollama app [here](https://ollama.com/download).
 
6. Pull a local reasoning LLM from [Ollama](https://ollama.com/search). As an [example](https://ollama.com/library/deepseek-r1:8b): 
```bash
ollama pull deepseek-r1:8b
```

## Usage

Run as a test without any arguments (this will use the built-in example):
```bash
python src/claude_prompt_lab/claude_prompt_lab.py --help
```

### Command Line Options

The script supports the following command-line arguments:

```bash
- `--local-reasoning-model`: Name of the local Ollama model to use (default: "deepseek-r1:8b")
- `--claude-model`: Name of the Claude model for evaluation (default: "claude-3-5-sonnet-20240620")
- `--objective`: Task objective for the model (default: uses built-in example)
- `--system-prompt`: Initial system prompt to test (default: uses built-in example)
- `--input`: Input text to test with (default: uses built-in example)
- `--max-attempts`: Maximum number of improvement attempts (default: 3)
- `--think-tag`: Opening tag for thinking steps (default: "<think>")
- `--think-end-tag`: Closing tag for thinking steps (default: "</think>")
```

### Jupyter Notebook

The `claude_prompt_lab.ipynb` file is a Jupyter notebook that allows you to run the prompt lab in a more interactive way.

## How It Works

1. **Generation**: Runs your prompt against the local reasoning model with [Ollama](https://github.com/ollama/ollama-python)
2. **Evaluation**: Uses Claude to assess if the response meets objectives
3. **Analysis**: If the response fails evaluation, Claude analyzes the thinking process and suggests improvements
4. **Refinement**: Updates the system prompt based on suggestions
5. **Iteration**: Repeats the process until success or max attempts reached

The tool generates a detailed report showing:
- Assessment of each attempt
- Diagnosis of issues
- Suggested improvements
- Final optimized prompt (on success)
