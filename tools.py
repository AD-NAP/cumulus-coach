from retrieve import get_col


def lookup_service(name: str, limit: int = 3) -> list[dict]:
    """Find doc chunks that mention an AWS service by its exact name, such as "Amazon S3"."""
    found = get_col().get(where_document={"$contains": name}, limit=limit)
    return [
        {"text": text, "source": metadata.get("source")}
        for text, metadata in zip(found["documents"], found["metadatas"])
    ]


# What Claude sees: when to use the tool and what to pass. Claude never sees the Python code.
LOOKUP_SERVICE_TOOL = {
    "name": "lookup_service",
    "description": (
        "Look up one AWS service by its official name and get the documentation excerpts that mention it. "
        "Use it when the user asks what a specific AWS service is or does. "
        "The match is exact and case-sensitive, so pass the full official name, such as \"Amazon S3\" "
        "or \"AWS Lambda\", not \"s3\" or \"lambda\". An empty result means the documents don't mention it."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Official AWS service name, for example \"Amazon S3\".",
            },
        },
        "required": ["name"],
    },
}

# The menu Claude sees, and the kitchen that cooks each order: tool name -> Python function.
TOOL_DEFINITIONS = [LOOKUP_SERVICE_TOOL]
TOOLS = {"lookup_service": lookup_service}
