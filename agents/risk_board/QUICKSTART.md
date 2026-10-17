# Risk Management Agent - Quick Start Guide

## What Is It?

The Risk Management Agent analyzes your AXIOM project's risks by examining:
- **Bugs & Defects** - Critical issues that could impact delivery
- **Resource Constraints** - Team members at high allocation (potential bottlenecks)
- **Domain Risks** - Technical risks by domain (Mobile, Vehicle, Security, etc.)
- **Sprint Status** - Risk assessment at sprint level
- **Mitigation Strategies** - Actionable recommendations

## Getting Started

### 1. Install Dependencies
```bash
cd C:\New folder\builder_axoim\AXIOM-main\agents\agent_pjm
pip install -r requirements.txt
```

### 2. Run CLI Analysis (Quick Report)
```bash
python risk_management_page.py
```

This will:
- Display risk summary in console
- Generate `risk_analysis_report.json` with full details

### 3. Start Interactive Dashboard (Web UI)
```bash
python risk_management_page.py --api
```

Then open: **http://localhost:5000** in your browser

## Dashboard Features

The web dashboard provides:
- 🎯 **Risk Score** - Overall project risk (0-100)
- 📊 **Risk Summary** - Count of critical issues, bottlenecks, at-risk sprints
- 🐛 **Critical Defects** - List of bugs with impact assessment
- 👥 **Resource Constraints** - Team allocation visualization
- 🏢 **Domain Risks** - Risks by technical area
- 📅 **Sprint Status** - Risk level per sprint
- 🛡️ **Mitigations** - Recommended actions to reduce risk

## API Query Examples

### Get Risk Score
```bash
curl http://localhost:5000/api/risk-score
```

### Get Critical Defects
```bash
curl "http://localhost:5000/api/critical-defects?priority=CRITICAL"
```

### Get Resource Bottlenecks
```bash
curl http://localhost:5000/api/resource-constraints
```

### Advanced Query (POST)
```bash
curl -X POST http://localhost:5000/api/risk-query \
  -H "Content-Type: application/json" \
  -d '{
    "include_defects": true,
    "include_resources": true,
    "include_sprints": true,
    "include_mitigations": true
  }'
```

## Risk Score Interpretation

| Score | Level | Meaning |
|-------|-------|---------|
| 0-30 | 🟢 Low | Project healthy, continue monitoring |
| 30-60 | 🟡 Medium | Implement mitigation strategies |
| 60-80 | 🔴 High | Escalate to project leadership |
| 80-100 | 🔴🔴 Critical | Immediate action required |

## Data Files Used

The agent reads from:
- `../../data/jira_issues.csv` - Issues, bugs, tasks
- `../../data/AXIOM_Capacity_Planning.csv` - Resource allocation
- `../../data/AXIOM_Competency_Matrix.csv` - Team skills
- `../../data/AXIOM_PI_Planning_2026.csv` - PI planning

## Key Metrics

**Current Status:**
- Critical Defects: 6
- Resource Bottlenecks: 6 (team members >80% allocated)
- At-Risk Sprints: 4
- Overall Risk Level: Medium (Score: ~50)

**Top Issues:**
1. Boundary-zone unlock intermittently fails (TWK-107)
2. Unlock latency exceeds target on low-power phone (TWK-108)
3. Revoked key remains accepted during vehicle cache window (TWK-112)

**Resource Alerts:**
- Anika Rao (Architecture): 100% allocated
- Kiran Das (Vehicle): 100% allocated
- Sonal Iyer (QA): 100% allocated

## Python API Usage

```python
from agents.agent_pjm import RiskAnalyzer

# Create analyzer
analyzer = RiskAnalyzer('../../data')

# Get report
report = analyzer.generate_risk_report()

# Access specific analysis
defects = analyzer.analyze_critical_defects()
resources = analyzer.analyze_resource_constraints()
domains = analyzer.analyze_domain_risks()
sprints = analyzer.analyze_sprint_risks()

# Print summary
analyzer.print_summary()

# Export report
analyzer.export_report('risk_report.json')
```

## Common Tasks

### Monitor a Specific Sprint
```bash
curl "http://localhost:5000/api/sprint-risks?sprint_id=SPR-03"
```

### Check Mobile Domain Risks
```bash
curl "http://localhost:5000/api/domain-risks?domain=Mobile"
```

### View Defects by Priority
```bash
curl "http://localhost:5000/api/critical-defects?priority=CRITICAL&status=OPEN"
```

### Get All Mitigation Strategies
```bash
curl http://localhost:5000/api/mitigation-strategies
```

## Troubleshooting

**Port 5000 already in use?**
```bash
python risk_management_page.py --api --port 8000
```

**Missing data files?**
Check that these exist in the `../../data/` directory:
- `jira_issues.csv`
- `AXIOM_Capacity_Planning.csv`
- `AXIOM_Competency_Matrix.csv`
- `AXIOM_PI_Planning_2026.csv`

**Dashboard not loading?**
- Ensure Flask and Flask-CORS are installed: `pip install flask flask-cors`
- Check that the API server is running on port 5000
- Open browser console (F12) to see any errors

## For More Information
See `README.md` for complete API documentation and architecture details.
