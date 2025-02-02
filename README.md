# 🏥 Dr Claude's Prompt Lab

A laboratory for designing and optimizing prompts for open source reasoning models, using Claude as an expert evaluator and prompt doctor. This tool leverages the unique ability of open source models to expose their reasoning process, allowing us to diagnose and improve their behavior through better prompting. It also leverages Claude as a strong evaluator and [meta-prompter](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-generator).

## Overview

Dr Claude's Prompt Lab helps you design better prompts through a novel diagnostic approach:

1. **Transparent Reasoning**: Utilizes open source models that expose their step-by-step reasoning process
2. **Expert Evaluation**: Uses Claude to assess if the model's response and reasoning meet objectives
3. **Diagnostic Analysis**: When responses fall short, Claude analyzes the model's reasoning trace
4. **Prompt Treatment**: Claude acts as a meta-prompter to prescribe improved prompts
5. **Iterative Refinement**: Repeats the process until the model achieves desired performance

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
 
6. Pull a local reasoning LLM from [Ollama](https://ollama.com/search), such as [DeepSeek R1:8B](https://ollama.com/library/deepseek-r1:8b): 
```bash
ollama pull deepseek-r1:8b
```

## Usage

### Command Line Options

```bash
python src/claude_prompt_lab/claude_prompt_lab.py --help
```

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

### Example

**Research assistant**

Used to optimize prompts for [Ollama Deep Researcher](https://github.com/langchain-ai/ollama-deep-researcher):

In particular, the summarizer instructions:
```
When EXTENDING an existing summary:                                                                                                                 
1. Read the existing summary and new search results carefully.                                                    
2. Compare the new information with the existing summary.                                                         
3. For each piece of new information:                                                                             
    a. If it's related to existing points, integrate it into the relevant paragraph.                               
    b. If it's entirely new but relevant, add a new paragraph with a smooth transition.                            
    c. If it's not relevant to the user topic, skip it.                                                            
4. Ensure all additions are relevant to the user's topic.                                                         
5. Verify that your final output differs from the input summary.    
```
Trace [here](https://smith.langchain.com/public/e9429828-8117-4062-bfa1-acfbac9f7f83/r))