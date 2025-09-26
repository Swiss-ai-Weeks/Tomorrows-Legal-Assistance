import os
import re

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate


def _extract_input_variables(markdown_content: str) -> list[str]:
    # Use regex to find the section with input_variables
    input_variables_section = re.search(
        r"- input_variables:\s*((?:\n\s*-\s*\w+)+)", markdown_content
    )

    if not input_variables_section:
        raise ValueError("input_variables section not found in the markdown content.")

    # Extract the variables
    input_variables = re.findall(r"-\s*(\w+)", input_variables_section.group(1))

    return input_variables


def _strip_markdown_metadata(markdown_content: str) -> str:
    match = re.search(r"(#.*)", markdown_content, re.DOTALL)

    # If a match is found, return the matched text
    if match:
        return match.group(1)
    else:
        raise ValueError("Markdown content is invalid. No content found.")


def _validate_variables_in_content(
    stripped_content: str, input_variables: list[str]
) -> bool:
    # Extract all {variables} in the stripped content
    content_variables = re.findall(r"\{(\w+)\}", stripped_content)

    # Check if all {variables} in the content are in input_variables
    for var in content_variables:
        if var not in input_variables:
            raise ValueError(
                f"Variable {var} found in content is not in input_variables."
            )

    # Check if all input_variables are in the content
    for var in input_variables:
        if var not in content_variables:
            raise ValueError(f"Input variable {var} is not used in the content.")

    return True


def _validate_chat_message_format(markdown_content: str) -> None:
    titles = re.findall(r"#+ [^#\n]*", markdown_content)
    # filter out not main titles
    titles = [title for title in titles if "##" not in title]
    titles = [title.replace("#", "").strip() for title in titles]

    # Check if one of the titles is not system, human, ai, placeholder, function or tool messages
    if any(
        [
            title.lower()
            not in ["system", "human", "ai", "placeholder", "function", "tool"]
            for title in titles
        ]
    ):
        raise ValueError(
            "Invalid markdown content for Chat template prompt. All titles should be either human, ai, placeholder, function or tool messages."
        )


def _validate_markdown_for_prompt_template_and_strip_content(file_path: str) -> str:
    """
    Validate the markdown content for prompt template and strip the metadata from the content.
    this returns the stripped content.
    :param file_path:
    :return:
    """
    with open(file_path, "r") as f:
        markdown_content = f.read()

    # Extract input_variables
    input_variables = _extract_input_variables(markdown_content)

    # Strip input_variables from the content
    stripped_content = _strip_markdown_metadata(markdown_content)

    # Validate the variables in the content
    if not _validate_variables_in_content(stripped_content, input_variables):
        raise ValueError("Invalid markdown content.")
    return stripped_content


@staticmethod
def _markdown_content_to_chat_template_pairs(
    markdown_content: str,
) -> list[tuple[str, str]]:
    pattern = re.compile(
        r"(?i)^# (System|Human|AI|Placeholder|Function|Tool)\n(.*?)(?=\n# (System|Human|AI|Placeholder|Function|Tool)|\Z)",
        re.DOTALL | re.MULTILINE,
    )

    # Find all matches using regex
    matches = re.findall(pattern, markdown_content)

    # Create a list of pairs (title_name, content)
    sections = [
        (match[0].strip("# ").lower().strip(), match[1].strip()) for match in matches
    ]

    return sections


def load_markdown_as_prompt_template(file_path: str) -> PromptTemplate:
    stripped_content = _validate_markdown_for_prompt_template_and_strip_content(
        file_path
    )
    return PromptTemplate.from_template(stripped_content)


def load_markdown_as_chat_prompt_template(file_path: str) -> ChatPromptTemplate:
    stripped_content = _validate_markdown_for_prompt_template_and_strip_content(
        file_path
    )

    # Validate that all the '#' title in the markdown is either human, ai, placeholder, function or tool messages
    _validate_chat_message_format(stripped_content)
    chat_template_pairs = _markdown_content_to_chat_template_pairs(stripped_content)
    return ChatPromptTemplate.from_messages(chat_template_pairs)


def markdown_to_prompt_template(
    relative_prompt_path: str,
) -> PromptTemplate | ChatPromptTemplate:
    absolute_prompt_path = (
        f"{os.path.dirname(os.path.abspath(__file__))}/{relative_prompt_path}"
    )
    with open(absolute_prompt_path, "r") as f:
        markdown_content = f.read()

    # Define the regex pattern to match _type
    pattern = r"_type\s*:\s*(\S+)"

    # Search for the pattern in the markdown text
    match = re.search(pattern, markdown_content)

    # If a match is found, return the value, else return None
    if match:
        if match.group(1) and match.group(1).replace('"', "") == "chat":
            return load_markdown_as_chat_prompt_template(absolute_prompt_path)
        else:
            return load_markdown_as_prompt_template(absolute_prompt_path)
    else:
        print("No type found in the markdown content. Loading as a prompt template.")
        return load_markdown_as_prompt_template(absolute_prompt_path)
