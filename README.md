# 🧪 Dr Claude's Prompt Lab

Prompt engineering LLMs is a challenge. A new class of open source reasoning LLMs, like [DeepSeek R1](https://github.com/deepseek-ai/DeepSeek-R1/blob/main/DeepSeek_R1.pdf), expose their step-by-step thinking process via "thoughts" emitted during inference. This repo explores an evaluator-optimizer approach where Claude acts as a "prompt doctor", analyzing mistakes in the step-by-step thinking process and prescribing improved prompts as treatment. It focuses on (1) distilled reasoning models (via Ollama) that benefit from careful prompting and uses (2) Claude to evaluate reasoning model performance, diagnose where reasoning goes wrong, suggest targeted prompt improvements, and iteratively refine the prompt.
 
![dr_claude](https://github.com/user-attachments/assets/113460a2-6aa7-4afa-b12f-02b3eb321d16)

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

`src/claude_prompt_lab/claude_prompt_lab.ipynb` allows you to run the prompt lab in a notebook.

## How It Works

**Transparent Reasoning**

Open source models expose their step-by-step reasoning process. For example, the [DeepSeek R1 model](https://github.com/deepseek-ai/DeepSeek-R1/blob/main/DeepSeek_R1.pdf) and its [distilled versions](https://ollama.com/library/deepseek-r1) emit reasoning traces using the `<think>` tag. Here, we focus locally running distilled reasoning models, because they can be tricker to prompt due to their smaller size / lower capacity.

**Expert Evaluation**

The prompt lab is set up as an **[evaluator-optimizer workflow](https://www.anthropic.com/research/building-effective-agents)**, with Claude using **[tool calling](https://docs.anthropic.com/en/docs/build-with-claude/tool-use#json-mode)** to return a structured evaluation of the model's response and reasoning as JSON object. 

**Diagnostic Analysis**: 

When responses fail the evaluation, Claude analyzes the model's reasoning trace jointly with the input, output, current system prompt, and overall objective to diagnose the issue. We provide a [meta-prompt](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-generator) that [instructs Claude](https://github.com/aws-samples/claude-prompt-generator/blob/main/src/metaprompt.txt) to generate a new system prompt that will improve the distilled reasoning model's behavior. This workflow proceeds for a fixed number of attempts or until evaluation is passed.

## Example

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
Trace [here](https://smith.langchain.com/public/e9429828-8117-4062-bfa1-acfbac9f7f83/r)
