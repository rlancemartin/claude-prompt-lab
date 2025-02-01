import argparse

from anthropic import Anthropic
from langsmith import traceable
from ollama import chat, ChatResponse

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from utils import extract_xml, grade_response_schema
from prompts import meta_prompt_input, evaluator_input_prompt, evaluator_system_prompt, meta_prompt_system

# Anthropic client
client = Anthropic()

# Define the console
console = Console()

@traceable
def run_generator(model: str, 
                model_input: str, 
                system_prompt: str, 
                think_tag: str,
                think_end_tag: str):
  
  """Chat with an Ollama reasoning model, which has designated thinking tags.
    
    Args:
        model (str): The name of the reasoning model to use
        model_input (str): The user message to send to the model
        system_prompt (str): System prompt to set context/behavior.
        think_tag (str): Tag for the start of thinking steps
        think_end_tag (str): Tag for the end of thinking steps
        
    Returns:
        chat_message (str): The model's response text
        thinking_steps (list[str]): The model's thinking steps"""

  # Call Ollama 
  with console.status("[bold yellow]🤔 Generating reasoning model response...[/bold yellow]"):
    response: ChatResponse = chat(model=model, messages=[
        {
        'role': 'system',
        'content': system_prompt,
        },
        {
        'role': 'user',
        'content': model_input,
        },
    ])

    console.print("[bold green]✓[/bold green] Reasoning model response generated")

  # Response
  chat_message = response['message']['content']

  # Extract thinking content (if present) and remaining message
  thinking_steps = ""
  if chat_message.startswith(think_tag):
      # Split on end tag to separate thinking content from rest of message
      think_content, chat_message = chat_message[len(think_tag):].split(think_end_tag, 1)
      thinking_steps = think_content.strip()  

  return chat_message, thinking_steps

@traceable
def run_evaluator(model, reasoning_model_objective, reasoning_model_input, reasoning_model_response):
    """Evaluates an AI model's response against a given objective using Claude.
    
    Args:
        model (str): The name of the model to use for evaluation
        reasoning_model_objective (str): The task objective that the model response should meet
        reasoning_model_input (str): The original input/prompt given to the model
        reasoning_model_response (str): The model's response to be evaluated
        
    Returns:
        dict: Evaluation results containing:
            - passed (bool): Whether the response meets requirements
            - justification (str): Brief explanation of the grading decision
    """
     
    # Format the input
    input_formatted=evaluator_input_prompt.format(reasoning_model_objective=reasoning_model_objective, 
                                                  reasoning_model_input=reasoning_model_input, 
                                                  reasoning_model_response=reasoning_model_response)

    with console.status("[bold yellow]🤔 Evaluating reasoning model response...[/bold yellow]"):
        # Run the evaluator
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            system=evaluator_system_prompt,
            tools=[
                grade_response_schema
            ],
            tool_choice={"type": "tool", "name": "grade_response"},
            messages=[
                {
                    "role": "user", 
                    "content": input_formatted
                }
            ]
            )

    console.print("[bold green]✓[/bold green] Reasoning model response evaluated")
    return message.content[0].input

@traceable
def run_meta_prompt(model,
                    reasoning_model_objective, 
                    reasoning_model_system_prompt, 
                    reasoning_model_input, 
                    reasoning_model_thinking, 
                    reasoning_model_response,
                    grader_feedback,
                    medical_report):
    """Analyzes an AI model's performance and generates improved system prompts using Claude.
    
    This function evaluates the model's reasoning process and output quality, then provides
    feedback and suggestions for improvement through an expert system analyst perspective.
    
    Args:
        model (str): The name of the model to use for evaluation
        reasoning_model_objective (str): The intended goal or task objective for the model
        reasoning_model_system_prompt (str): The current system prompt used to guide the model
        reasoning_model_input (str): The original input/prompt given to the model
        reasoning_model_thinking (str): The model's intermediate reasoning or thinking steps
        reasoning_model_response (str): The model's final response or output
        grader_feedback (str): Feedback from the grader that the output didn't meet the task
        medical_report (str]: Medical report on prior attempts
    Returns:
        str: A structured analysis containing:
            - Assessment of the model's performance
            - Specific suggestions for improvement
            - An improved version of the system prompt"""

    # Format the meta prompt
    input_formatted = meta_prompt_input.format(reasoning_model_objective=reasoning_model_objective, 
                                     reasoning_model_system_prompt=reasoning_model_system_prompt, 
                                     reasoning_model_input=reasoning_model_input, 
                                     reasoning_model_thinking=reasoning_model_thinking, 
                                     reasoning_model_response=reasoning_model_response,
                                     grader_feedback=grader_feedback,
                                     medical_report=medical_report)

    # Response
    with console.status("[bold yellow]🔄 Analyzing and improving prompt...[/bold yellow]"):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=meta_prompt_system,
            messages=[{"role": "user", "content": input_formatted}],
            temperature=0.1,
            )
    
    console.print("[bold green]✓[/bold green] Prompt analyzed and improved")
    
    return response.content[0].text

def generate_report_entry(attempt, grade, parsed_response=None):
    """Generate a medical-style report entry for each iteration"""
    report = [
        f"\n### 🏥 Attempt {attempt} Assessment Report",
        f"\n**Status**: {'✅ PASSED' if grade['passed'] else '❌ FAILED'}",
        f"\n**Diagnosis**: {grade['justification']}",
    ]
    
    if not grade['passed'] and parsed_response:
        report.extend([
            "\n**Specialist Notes** 🔬:",
            f"\n- Assessment: {parsed_response['assessment']}",
            f"\n- Treatment Plan: {parsed_response['suggestions']}",
            "\n**Prescribed System Prompt** 💊:",
            f"\n```\n{parsed_response['improved_prompt']}\n```"
        ])
    
    return "\n".join(report)

def run_prompt_lab(reasoning_model: str,
                   claude_model: str,
                   reasoning_model_input: str,
                   reasoning_model_objective: str,
                   reasoning_model_system_prompt: str,
                   think_tag: str,
                   think_end_tag: str,
                   max_attempts: int) -> str:
    """Run the prompt lab to test and improve system prompts.
    
    Args:
        reasoning_model: Name of the Ollama reasoning model to use
        claude_model: Name of the claude model to use
        reasoning_model_input: The user input to test with
        reasoning_model_objective: The task objective that responses should meet
        reasoning_model_system_prompt: Initial system prompt to test and improve
        think_tag: Tag for the start of thinking steps
        think_end_tag: Tag for the end of thinking steps
        max_attempts: Maximum number of improvement attempts
        
    Returns:
        str: A complete medical-style report of the prompt improvement process
    """

    # Initialize the medical report
    medical_report = ["# 🏥 Dr Claude's Prompt Lab: Report", 
                    f"\n## Patient Information: {reasoning_model}",
                    f"\n- **Treatment Objective**: {reasoning_model_objective}",
                    "\n## Treatment History"]
     
    attempt = 1
    
    # Run the loop
    while attempt <= max_attempts:
        console.print(f"\n[bold cyan]🔄 Attempt {attempt}/{max_attempts}[/bold cyan]")

        # Step 1: Run generator
        console.print("[yellow]Step 1: Running generator with system prompt:[/yellow]")
        console.print(Panel(reasoning_model_system_prompt, title="Current System Prompt", border_style="blue"))
       
        # Run the generator
        reasoning_model_response, reasoning_model_thinking = run_generator(
            model=reasoning_model,
            model_input=reasoning_model_input, 
            system_prompt=reasoning_model_system_prompt,
            think_tag=think_tag,
            think_end_tag=think_end_tag
        )
        
        # Grade the response
        # Step 2: Grade the response
        console.print("\n[yellow]Step 2: Evaluating response...[/yellow]")
        grade = run_evaluator(model=claude_model, reasoning_model_objective=reasoning_model_objective, reasoning_model_input=reasoning_model_input, reasoning_model_response=reasoning_model_response)

        status = "✅ PASSED" if grade['passed'] else "❌ FAILED"
        console.print(f"[bold]Evaluation Result:[/bold] {status}")
        console.print(f"[bold]Justification:[/bold] {grade['justification']}")

        # Generate report entry
        parsed_response = None
        if not grade['passed']:
            console.print("\n[yellow]Step 3: Response failed evaluation, running meta-prompt analysis...[/yellow]")
            reasoning_model_diagnosis = run_meta_prompt(
                model=claude_model,
                reasoning_model_objective=reasoning_model_objective, 
                reasoning_model_system_prompt=reasoning_model_system_prompt, 
                reasoning_model_input=reasoning_model_input, 
                reasoning_model_thinking=reasoning_model_thinking, 
                reasoning_model_response=reasoning_model_response,
                grader_feedback=grade['justification'],
                medical_report=medical_report
            )

            console.print("\n[yellow]Step 4: Extracting improvements from analysis...[/yellow]")
            parsed_response = {
                'assessment': extract_xml(reasoning_model_diagnosis, 'assessment'),
                'suggestions': extract_xml(reasoning_model_diagnosis, 'suggestions'),
                'improved_prompt': extract_xml(reasoning_model_diagnosis, 'improved_prompt')
            }
            
            # Update system prompt for next attempt
            # Step 5: Update system prompt for next attempt
            console.print("\n[yellow]Step 5: Updating system prompt for next attempt...[/yellow]")
            reasoning_model_system_prompt = parsed_response['improved_prompt']
        
        # Add to medical report
        medical_report.append(generate_report_entry(attempt, grade, parsed_response))
        
        # Check if we should continue
        if grade['passed']:
            medical_report.extend([
                "\n## 🎉 Final Diagnosis",
                "\nPatient has achieved optimal response quality. Treatment successful!",
                "\n### Final System Prompt:",
                f"\n```\n{reasoning_model_system_prompt}\n```",
                "\n### Final Response:",
                f"\n```\n{reasoning_model_response}\n```"
            ])
            break
        
        attempt += 1

    if attempt > max_attempts:
        medical_report.extend([
            "\n## ⚠️ Treatment Terminated",
            "\nMaximum attempts reached without achieving optimal response.",
            "\n### Latest Response:",
            f"\n```\n{reasoning_model_response}\n```"
        ])
    
    return "\n".join(medical_report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Claude Prompt Lab')
    
    # Add arguments
    parser.add_argument('--local-reasoning-model', 
                       default="deepseek-r1:8b",
                       help='Name of the reasoning model to use')
    
    parser.add_argument('--claude-model', 
                       default="claude-3-5-sonnet-20240620",
                       help='Name of the claude model to use')

    parser.add_argument('--objective', 
                       default=None,
                       help='Task objective for the model')
    
    parser.add_argument('--system-prompt', 
                       default=None,
                       help='Initial system prompt')
    
    parser.add_argument('--input', 
                       default=None,
                       help='Input text with existing summary and new content')
    
    parser.add_argument('--max-attempts', 
                       type=int,
                       default=3,
                       help='Maximum number of improvement attempts')

    parser.add_argument('--think-tag', 
                       default="<think>",
                       help='Tag for the start of thinking steps')
    
    parser.add_argument('--think-end-tag', 
                       default="</think>",
                       help='Tag for the end of thinking steps')
    
    args = parser.parse_args()

    # Use default examples if no arguments provided as a test
    reasoning_model_objective = args.objective or """I am prompting a distilled reasoning model to produce research summaries. 
    I want it to be able to create a high quality summary and seamlessly integrate new search results into 
    the existing summary. If there's no new or useful information, return the existing summary unchanged. 
    If there is new information, weave it in smoothly rather than just adding a new section."""

    reasoning_model_system_prompt = args.system_prompt or """Your goal is to generate a high-quality summary of the web search results.
    When EXTENDING an existing summary:
    1. Seamlessly integrate new information without repeating what's already covered
    2. Maintain consistency with the existing content's style and depth
    3. Only add new, non-redundant information
    4. Ensure smooth transitions between existing and new content
    
    CRITICAL REQUIREMENTS:
    - Start IMMEDIATELY with the summary content - no introductions
    - Focus ONLY on factual, objective information
    - Maintain a consistent technical depth
    - Avoid redundancy and repetition"""

    reasoning_model_input = args.input or """Extend the existing summary:
    Large language models have demonstrated remarkable capabilities in natural language processing tasks. 
    GPT-3, with 175 billion parameters, showed strong zero-shot and few-shot learning abilities across 
    various tasks. These models can perform tasks like translation, question-answering, and text generation 
    with high accuracy. However, they still face challenges with factual consistency and reasoning.
    
    Include new search results:
    Recent developments in LLMs have shown significant improvements in reasoning capabilities. Claude 3, 
    released in March 2024, demonstrates enhanced logical reasoning and reduced hallucination rates 
    compared to previous models. The model shows particular strength in mathematical reasoning and 
    code generation tasks. Additionally, new training techniques focusing on chain-of-thought prompting 
    have improved models' ability to break down complex problems into smaller steps."""
    
    # Print header
    console.print("\n[bold blue]🧪 Starting Claude's Prompt Lab...[/bold blue]\n", style="bold")
    
    # Run the prompt lab
    report = run_prompt_lab(
        reasoning_model=args.local_reasoning_model,
        claude_model=args.claude_model,
        reasoning_model_input=reasoning_model_input,
        reasoning_model_objective=reasoning_model_objective,
        reasoning_model_system_prompt=reasoning_model_system_prompt,
        think_tag=args.think_tag,
        think_end_tag=args.think_end_tag,
        max_attempts=args.max_attempts
    )
    
    # Print the report with markdown formatting
    console.print(Markdown(report))
    console.print("\n[bold green]🎬 Prompt Lab Session Complete![/bold green]\n", style="bold")