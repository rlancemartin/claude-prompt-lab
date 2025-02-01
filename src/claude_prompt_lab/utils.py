import re

grade_response_schema =  {
                "name": "grade_response",
                "description": "Grade a response with pass/fail and provide justification.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "passed": {
                            "type": "boolean",
                            "description": "Whether the response meets requirements (true) or not (false)"
                        },
                        "justification": {
                            "type": "string",
                            "description": "Brief explanation of the grading decision in 1-2 sentences"
                        }
                    },
                    "required": ["passed", "justification"]
                }
            }

def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses 

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""