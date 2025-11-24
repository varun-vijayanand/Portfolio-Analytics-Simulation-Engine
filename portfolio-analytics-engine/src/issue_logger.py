import json
import os
from datetime import datetime

ISSUE_LOG_FILE = "governance/issues.json"


class IssueLogger:

    def __init__(self):
        os.makedirs("governance", exist_ok=True)

        # If file doesn't exist or is empty, initialize it
        if not os.path.exists(ISSUE_LOG_FILE) or os.path.getsize(ISSUE_LOG_FILE) == 0:
            with open(ISSUE_LOG_FILE, "w") as f:
                json.dump([], f)

    def log_issue(self, issue_type, description, severity, source):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        issue_id = f"ISSUE-{int(datetime.now().timestamp())}"

        new_issue = {
            "id": issue_id,
            "timestamp": timestamp,
            "type": issue_type,
            "severity": severity,
            "source": source,
            "description": description
        }

        try:
            with open(ISSUE_LOG_FILE, "r") as f:
                issues = json.load(f)
        except json.JSONDecodeError:
            # Auto heal corrupted file
            issues = []

        issues.append(new_issue)

        with open(ISSUE_LOG_FILE, "w") as f:
            json.dump(issues, f, indent=4)

        return issue_id
