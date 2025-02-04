# 🧪 Dr Claude's Prompt Lab

Prompt engineering LLMs is a challenge. A new class of open source reasoning LLMs, like [DeepSeek R1](https://github.com/deepseek-ai/DeepSeek-R1/blob/main/DeepSeek_R1.pdf), expose their step-by-step thinking process via "thoughts" emitted during inference. This repo aims to use this step-by-step thinking process to diagnose where reasoning goes wrong and prescribe improved prompts as treatment.

It uses an evaluator-optimizer workflow where Claude acts as a "prompt doctor", first evaluating whether the reasoning model's response satisfies the user's objective. If not, Claude examines the model's step-by-step thinking process to diagnose where reasoning may have gone wrong and suggests an improved prompt as treatment. The process repeats until the model passes the evaluation or a fixed number of attempts is reached. The tool generates a report summarizing the progression of prompt treatments.
 
![dr_claude](https://github.com/user-attachments/assets/113460a2-6aa7-4afa-b12f-02b3eb321d16)

## Installation

1. Clone the repository:

```bash
git https://github.com/rlancemartin/claude-prompt-lab.git
cd claude-prompt-lab
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

4. Ensure you have API key for Claude:
```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key
```

5. Download the Ollama app [here](https://ollama.com/download).
 
6. Pull a local reasoning LLM from [Ollama](https://ollama.com/search), such as [DeepSeek R1:8B](https://ollama.com/library/deepseek-r1:8b): 
```bash
ollama pull deepseek-r1:8b
```

## Quickstart

Test it on the default example in `src/claude_prompt_lab/claude_prompt_lab.py`:
* Ollama model: [DeepSeek R1:8B](https://ollama.com/library/deepseek-r1:8b)
* Claude model: [Claude 3.5 Sonnet](https://docs.anthropic.com/en/docs/models/sonnet)
* Objective: Test the ability of the reasoning model to update a summary with new search results.
* See the specific prompts in `src/claude_prompt_lab/prompts.py`.

```bash
python src/claude_prompt_lab/claude_prompt_lab.py 
```

You will see the reasoning model start thinking and the provided system prompt:
![Screenshot 2025-02-03 at 7 53 49 PM](https://github.com/user-attachments/assets/d096287f-4cd6-4aae-aac7-7358e30fc74b)

You will then see the result of evaluation:
![Screenshot 2025-02-03 at 7 54 20 PM](https://github.com/user-attachments/assets/ab93608b-1087-47eb-bd3a-e85a291e5e7b)

The cycle will repeast until evaluation passes or a fixed number of tries is reached, and a report will be provided at the end:
![Screenshot 2025-02-03 at 7 54 39 PM](https://github.com/user-attachments/assets/3054979a-bc31-4894-97c0-edc6a7819a9b)

## Running your own tests

The tool can be run either through the command line interface or using the Jupyter notebook.

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
