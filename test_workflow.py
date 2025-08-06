#!/usr/bin/env python3
import yaml
import sys

try:
    with open('.github/workflows/annual-review.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    print('✅ Anniversary workflow YAML syntax is valid')
    print(f'✅ Workflow name: {workflow.get("name", "Unknown")}')
    
    on_config = workflow.get("on", {})
    if isinstance(on_config, dict):
        if "schedule" in on_config:
            print(f'✅ Scheduled for: {on_config["schedule"][0]["cron"]}')
        if "workflow_dispatch" in on_config:
            print('✅ Manual trigger: enabled')
    
    jobs = workflow.get("jobs", {})
    print(f'✅ Jobs defined: {len(jobs)}')
    
    if "anniversary-review" in jobs:
        steps = jobs["anniversary-review"].get("steps", [])
        print(f'✅ Steps in anniversary-review job: {len(steps)}')
    
    print('✅ All workflow validation checks passed')
    
except Exception as e:
    print(f'❌ Workflow YAML error: {e}')
    print('Raw YAML content:')
    with open('.github/workflows/annual-review.yml', 'r') as f:
        print(f.read()[:500] + '...')
    sys.exit(1)
