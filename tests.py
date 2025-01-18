import subprocess
import os

def run_script(query, input_tags, input_url_scheme):
    """Runs the tagging script with the given inputs."""
    # Set environment variables
    os.environ['input_tags'] = input_tags
    os.environ['input_url_scheme'] = input_url_scheme

    # Call the script
    result = subprocess.run(
        ["python3", "process_url.py", query],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Return stdout and stderr
    return result.stdout, result.stderr

def validate_output(query, input_tags, input_url_scheme, expected_tags, expected_url_contains):
    """Validates the output of the script against expected values."""
    stdout, stderr = run_script(query, input_tags, input_url_scheme)

    # Parse stdout for validation
    lines = stdout.strip().split("\n")
    matched_tags = []
    url = ""

    for line in lines:
        if line.startswith("Matched Tags:"):
            matched_tags = eval(line.replace("Matched Tags:", "").strip())
        elif line.startswith("URL:"):
            url = line.replace("URL:", "").strip()

    # Validate
    assert matched_tags == expected_tags, f"Expected tags {expected_tags}, but got {matched_tags}"
    # assert all(part in url for part in expected_url_contains), f"Expected URL to contain {expected_url_contains}, but got {url}"
    # print(f"Test passed for query: {query}")

# Test cases
if __name__ == "__main__":
    input_tags = """
    work 📁:
      - work
      - ios
      - pr

    review 👀:
      - pr
      - doc
      - review

    Card 💡:
      - create card
      - create a card

    Important 🔺:
      - ' !!'
      - '!! '
    """
    input_url_scheme = "sorted://x-callback-url/add?title=[title]&tags=[tags]&date=[today]"

    test_cases = [
        {
            "query": "Lee is working on iOS development.",
            "expected_tags": ["work 📁"],
            "expected_url_contains": ["Lee%20is%20working%20on%20iOS%20development", "work%20%F0%9F%93%81"]
        },
        {
            "query": "This PR needs to be reviewed.",
            "expected_tags": ["work 📁", "review 👀"],
            "expected_url_contains": ["This%20PR%20needs%20to%20be%20reviewed", "work%20%F0%9F%93%81", "review%20%F0%9F%91%80"]
        },
        {
            "query": "Create a card for this task.",
            "expected_tags": ["Card 💡"],
            "expected_url_contains": ["Create%20a%20card%20for%20this%20task", "Card%20%F0%9F%92%A1"]
        },
        {
            "query": "This is very important !!",
            "expected_tags": ["Important 🔺"],
            "expected_url_contains": ["This%20is%20very%20important %21%21", "Important%20%F0%9F%94%BA"]
        },
        {
            "query": "Visit https://example.com for more info.",
            "expected_tags": [],
            "expected_url_contains": ["Visit%20for%20more%20info"]
        },
        {
            "query": "The document needs a final review.",
            "expected_tags": ["review 👀"],
            "expected_url_contains": ["The%20document%20needs%20a%20final%20review", "review%20%F0%9F%91%80"]
        },
    ]

    for case in test_cases:
        validate_output(case["query"], input_tags, input_url_scheme, case["expected_tags"], case["expected_url_contains"])
