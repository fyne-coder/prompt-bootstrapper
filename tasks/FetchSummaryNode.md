# Task: FetchSummaryNode

## Objective
Implement a PocketFlow node that fetches the HTML content from a given URL, extracts and concatenates the visible text, truncates it to 4,000 characters, and returns the result.

## Requirements
- Use the PocketFlow `Node` decorator with `retries=3`.
- Fetch the URL’s HTML using `httpx` with a 10-second timeout.
- On network or HTTP errors, retry up to 3 times before failing.
- Parse HTML into plain text (e.g., with BeautifulSoup), joining fragments with spaces.
- Truncate the final text to a maximum of 4,000 characters.
- Return the truncated text as a single string.

## Acceptance Criteria
- Given a valid URL, the node returns a string of length ≤ 4000.
- If the remote server returns a non-2xx status code or a network exception, the node retries up to 3 times, then raises an exception.
- Text extraction strips HTML tags and collapses whitespace.