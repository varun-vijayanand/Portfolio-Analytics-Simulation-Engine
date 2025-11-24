# src/issue_logger.py
import json
import pandas as pd
from datetime import datetime

class IssueLogger:
    def __init__(self, log_file='governance/issue_log.json'):
        self.log_file = log_file
        
    def log_issue(self, issue_type, description, severity='MEDIUM', component=None):
        """Log an issue to the governance log"""
        try:
            # Load existing issues
            with open(self.log_file, 'r') as f:
                issues = json.load(f)
        except FileNotFoundError:
            issues = {'issues': []}
        
        # Create new issue
        new_issue = {
            'id': f"ISS-{len(issues['issues']) + 1:06d}",
            'type': issue_type,
            'description': description,
            'severity': severity,
            'component': component,
            'timestamp': datetime.now().isoformat(),
            'status': 'OPEN',
            'resolution': None
        }
        
        issues['issues'].append(new_issue)
        
        # Save updated issues
        with open(self.log_file, 'w') as f:
            json.dump(issues, f, indent=2)
        
        return new_issue['id']
    
    def resolve_issue(self, issue_id, resolution):
        """Resolve an issue"""
        with open(self.log_file, 'r') as f:
            issues = json.load(f)
        
        for issue in issues['issues']:
            if issue['id'] == issue_id:
                issue['status'] = 'RESOLVED'
                issue['resolution'] = resolution
                issue['resolved_at'] = datetime.now().isoformat()
                break
        
        with open(self.log_file, 'w') as f:
            json.dump(issues, f, indent=2)
    
    def get_open_issues(self):
        """Get all open issues"""
        with open(self.log_file, 'r') as f:
            issues = json.load(f)
        
        return [issue for issue in issues['issues'] if issue['status'] == 'OPEN']