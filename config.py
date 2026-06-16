import os

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def missing_required_keys():
    return [
        name
        for name, value in {
            "SERPAPI_KEY": SERPAPI_KEY,
            "OPENAI_API_KEY": OPENAI_API_KEY,
        }.items()
        if not value
    ]
