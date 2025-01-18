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
    assert all(part in url for part in expected_url_contains), f"Expected URL to contain {expected_url_contains}, but got {url}"
    print(f"Test passed for query: {query}")

# Test cases
if __name__ == "__main__":
    input_tags = """
    work:
      - work
      - ios
      - lee
    home:
      - home
      - food
      - wife
    """
    input_url_scheme = "sorted://x-callback-url/add?title=[title]&tags=[tags]&date=[today]"

    test_cases = [
        {
            "query": "Lee is working on iOS development.",
            "expected_tags": ["work"],
            "expected_url_contains": ["Lee%20is%20working%20on%20iOS%20development", "work"]
        },
        {
            "query": "Lee's PR is long and tedious.",
            "expected_tags": ["work"],
            "expected_url_contains": ["Lee's%20PR%20is%20long%20and%20tedious", "work"]
        },
        {
            "query": "At home, we had delicious food.",
            "expected_tags": ["home"],
            "expected_url_contains": ["At%20home%2C%20we%20had%20delicious%20food", "home"]
        },
        {
            "query": "Flee from evil.",
            "expected_tags": [],
            "expected_url_contains": ["Flee%20from%20evil"]
        },
        {
            "query": "Visit https://example.com for more info.",
            "expected_tags": [],
            "expected_url_contains": ["Visit%20for%20more%20info"]
        },
    ]

    for case in test_cases:
        validate_output(case["query"], input_tags, input_url_scheme, case["expected_tags"], case["expected_url_contains"])
