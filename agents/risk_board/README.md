# AXIOM Risk Management Agent

A comprehensive risk management module for the AXIOM E-Key 2W project that analyzes defects, resource constraints, and project risks with both CLI and API interfaces.

## Features

### Core Capabilities
- **Critical Defect Analysis**: Identifies and prioritizes bugs and critical issues
- **Resource Constraint Detection**: Monitors team member allocation and identifies bottlenecks
- **Domain Risk Analysis**: Analyzes risks by technical domain (Mobile, Vehicle, Security, etc.)
- **Sprint Risk Assessment**: Evaluates sprint-level risks and impact
- **Risk Scoring**: Calculates overall project risk score (0-100)
- **Mitigation Strategies**: Generates actionable mitigation recommendations

### Data Sources
Analyzes data from:
- `jira_issues.csv` - Bug and task data
- `AXIOM_Capacity_Planning.csv` - Resource allocation
- `AXIOM_Competency_Matrix.csv` - Team skills and expertise
- `AXIOM_PI_Planning_2026.csv` - Program increment planning

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### CLI Mode (Default)
Print risk summary and export JSON report:

```bash
python risk_management_page.py
```

This will:
1. Generate a console risk summary
2. Export full report to `risk_analysis_report.json`

### API Server Mode
Start interactive dashboard with REST API:

```bash
python risk_management_page.py --api
```

Or specify a custom port:

```bash
python risk_management_page.py --api --port 8000
```

## REST API Endpoints

### Health & Status
- `GET /api/health` - Health check

### Risk Data Endpoints
- `GET /api/risk-summary` - Overall risk summary (critical defects, bottlenecks, at-risk sprints)
- `GET /api/risk-score` - Overall project risk score and component breakdown
- `GET /api/critical-defects?priority=CRITICAL&status=OPEN` - List critical defects with filtering
- `GET /api/resource-constraints?threshold=80` - Resource bottlenecks (default >80% allocation)
- `GET /api/domain-risks?domain=Mobile` - Risks by technical domain
- `GET /api/sprint-risks?sprint_id=SPR-03&risk_level=HIGH` - Sprint-level risk analysis
- `GET /api/mitigation-strategies` - Recommended mitigation strategies
- `GET /api/full-report` - Complete risk management report

### Advanced Query
- `POST /api/risk-query` - Advanced query with custom filters

Example:
```json
{
  "include_defects": true,
  "include_resources": true,
  "include_domains": true,
  "include_sprints": true,
  "include_mitigations": true,
  "defect_priority": "CRITICAL"
}
```

## Dashboard

Access the interactive web dashboard at `http://localhost:5000` when running in API mode.

### Dashboard Features
- Real-time risk score visualization
- Critical defects list
- Resource constraint monitoring
- Domain risk heatmap
- Sprint risk status
- Mitigation strategy recommendations
- Advanced filtering by priority, sprint, and domain
- Auto-refresh every 30 seconds

## API Usage Examples

### Get Risk Summary
```bash
curl http://localhost:5000/api/risk-summary
```

### Get Critical Defects
```bash
curl "http://localhost:5000/api/critical-defects?priority=CRITICAL"
```

### Get Resource Bottlenecks
```bash
curl http://localhost:5000/api/resource-constraints
```

### Advanced Risk Query
```bash
curl -X POST http://localhost:5000/api/risk-query \
  -H "Content-Type: application/json" \
  -d '{
    "include_defects": true,
    "include_resources": true,
    "include_mitigations": true,
    "defect_priority": "CRITICAL"
  }'
```

## Risk Score Interpretation

- **0-30**: Low Risk - Project is healthy, continue monitoring
- **30-60**: Medium Risk - Moderate risks detected, implement mitigations
- **60-80**: High Risk - Significant risks present, escalate to leadership
- **80-100**: Critical Risk - Immediate action required

## Component Scoring

Total Risk Score = Defect Score (0-40) + Resource Score (0-30) + Sprint Score (0-30)

- **Defect Score**: 5 points per critical defect (max 40)
- **Resource Score**: 3 points per bottleneck resource (max 30)
- **Sprint Score**: 4 points per at-risk sprint (max 30)

## Architecture

```
risk_management_page.py
├── RiskAnalyzer
│   ├── load_data() - Load CSV files
│   ├── analyze_critical_defects() - Defect analysis
│   ├── analyze_resource_constraints() - Resource analysis
│   ├── analyze_domain_risks() - Domain-level risks
│   ├── analyze_sprint_risks() - Sprint-level risks
│   └── generate_risk_report() - Comprehensive report
│
└── RiskDashboardAPI (Flask)
    ├── REST endpoints
    ├── Error handling
    ├── Risk scoring
    └── Dashboard interface
```

## Report Output

### JSON Report Format
```json
{
  "generated_date": "2026-10-17T18:27:28.339069",
  "project": "AXIOM E-Key 2W",
  "summary": {
    "overall_risk_level": "Medium",
    "critical_defects": 6,
    "resource_bottlenecks": 6,
    "at_risk_sprints": 4
  },
  "critical_defects": [...],
  "resource_constraints": {...},
  "domain_risks": {...},
  "sprint_risks": [...],
  "mitigation_strategies": {...}
}
```

## Configuration

No configuration file needed. The module automatically:
- Discovers data files in `../../data/` relative to script location
- Generates reports in the same directory as the script
- Binds to `0.0.0.0:5000` for API server (accessible from any interface)

## Troubleshooting

### Port Already in Use
```bash
python risk_management_page.py --api --port 8000
```

### Missing Data Files
Ensure these files exist in the data directory:
- `jira_issues.csv`
- `AXIOM_Capacity_Planning.csv`
- `AXIOM_Competency_Matrix.csv`
- `AXIOM_PI_Planning_2026.csv`

### CORS Issues
CORS is enabled by default. If accessing from a different domain, ensure Flask-CORS is installed.

## Integration

### Programmatic Usage
```python
from risk_management_page import RiskAnalyzer

analyzer = RiskAnalyzer("../../data")
report = analyzer.generate_risk_report()
print(f"Critical Defects: {report['summary']['critical_defects']}")
```

### Dashboard Integration
Include `dashboard.html` in your project management portal as an iframe or embed the API calls directly in your dashboard application.

## License
Internal - AXIOM Project

## Version
1.0.0 - 2026-10-17
