"""
Risk Management Analysis Page for AXIOM E-Key 2W Project
Analyzes defects, tasks, and resource constraints to identify and manage project risks.
Provides REST API endpoints for dashboard integration and risk queries.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging


class RiskAnalyzer:
    """Analyzes project risks based on defects, capacity, and resource constraints."""
    
    def __init__(self, data_dir: str):
        """Initialize risk analyzer with data directory."""
        self.data_dir = Path(data_dir)
        self.jira_data = None
        self.capacity_data = None
        self.competency_data = None
        self.pi_data = None
        self.risks = []
        self.load_data()
    
    def load_data(self):
        """Load all required CSV data files."""
        try:
            # Load JIRA issues including bugs and tasks
            jira_path = self.data_dir / "jira_issues.csv"
            if jira_path.exists():
                self.jira_data = pd.read_csv(jira_path)
            
            # Load capacity planning
            capacity_path = self.data_dir / "AXIOM_Capacity_Planning.csv"
            if capacity_path.exists():
                self.capacity_data = pd.read_csv(capacity_path)
            
            # Load competency matrix
            competency_path = self.data_dir / "AXIOM_Competency_Matrix.csv"
            if competency_path.exists():
                self.competency_data = pd.read_csv(competency_path)
            
            # Load PI planning
            pi_path = self.data_dir / "AXIOM_PI_Planning_2026.csv"
            if pi_path.exists():
                self.pi_data = pd.read_csv(pi_path)
                
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def analyze_critical_defects(self) -> List[Dict]:
        """Identify and analyze critical and open defects."""
        defects = []
        
        if self.jira_data is None:
            return defects
        
        # Filter for bugs and critical/high priority items
        critical_items = self.jira_data[
            (self.jira_data['Type'].isin(['Bug', 'Defect'])) |
            (self.jira_data['Priority'].isin(['Critical', 'High']))
        ]
        
        for _, item in critical_items.iterrows():
            defect = {
                'id': item.get('Issue Key', 'N/A'),
                'summary': item.get('Summary', 'N/A'),
                'type': item.get('Type', 'Unknown'),
                'status': item.get('Status', 'Unknown'),
                'priority': item.get('Priority', 'Unknown'),
                'assignee': item.get('Assignee', 'Unassigned'),
                'sprint': item.get('Sprint', 'N/A'),
                'impact': self._assess_impact(item),
                'mitigation': self._suggest_mitigation(item)
            }
            defects.append(defect)
        
        return defects
    
    def analyze_resource_constraints(self) -> Dict:
        """Analyze resource allocation and identify bottlenecks."""
        constraints = {}
        
        if self.capacity_data is None:
            return constraints
        
        # Identify resources with high allocation (>80%)
        high_allocation = self.capacity_data[
            self.capacity_data['Allocation_%'] > 80
        ]
        
        for _, resource in high_allocation.iterrows():
            resource_id = resource.get('Resource_ID', 'Unknown')
            constraints[resource_id] = {
                'name': resource.get('Associate', 'Unknown'),
                'role': resource.get('Role', 'N/A'),
                'domain': resource.get('Domain', 'N/A'),
                'allocation': resource.get('Allocation_%', 0),
                'location': resource.get('Location', 'N/A'),
                'risk_level': 'High' if resource.get('Allocation_%', 0) >= 100 else 'Medium',
                'recommendations': self._resource_recommendations(resource)
            }
        
        return constraints
    
    def analyze_domain_risks(self) -> Dict:
        """Analyze risks by technical domain."""
        domain_risks = defaultdict(lambda: {
            'open_defects': 0,
            'critical_items': 0,
            'assigned_resources': [],
            'capacity_status': 'Unknown'
        })
        
        if self.jira_data is None:
            return domain_risks
        
        # Map issue assignees to domains
        for _, issue in self.jira_data.iterrows():
            assignee = issue.get('Assignee', 'Unknown')
            issue_type = issue.get('Type', 'Unknown')
            priority = issue.get('Priority', 'Unknown')
            status = issue.get('Status', 'Unknown')
            
            # Find domain from competency data if available
            domain = self._find_resource_domain(assignee)
            
            if status in ['Open', 'In Progress']:
                domain_risks[domain]['open_defects'] += 1
            
            if priority == 'Critical':
                domain_risks[domain]['critical_items'] += 1
            
            if assignee != 'Unknown' and assignee not in domain_risks[domain]['assigned_resources']:
                domain_risks[domain]['assigned_resources'].append(assignee)
        
        return dict(domain_risks)
    
    def analyze_sprint_risks(self) -> List[Dict]:
        """Analyze risks at sprint level."""
        sprint_risks = []
        
        if self.jira_data is None:
            return sprint_risks
        
        sprints = self.jira_data['Sprint'].unique()
        
        for sprint in sprints:
            if pd.isna(sprint):
                continue
                
            sprint_issues = self.jira_data[self.jira_data['Sprint'] == sprint]
            
            open_count = len(sprint_issues[sprint_issues['Status'].isin(['Open', 'In Progress'])])
            critical_count = len(sprint_issues[sprint_issues['Priority'] == 'Critical'])
            
            risk_level = self._calculate_sprint_risk(sprint_issues)
            
            sprint_risks.append({
                'sprint_id': sprint,
                'total_items': len(sprint_issues),
                'open_items': open_count,
                'critical_items': critical_count,
                'risk_level': risk_level,
                'focus_areas': self._identify_focus_areas(sprint_issues)
            })
        
        return sprint_risks
    
    def generate_risk_report(self) -> Dict:
        """Generate comprehensive risk management report."""
        report = {
            'generated_date': datetime.now().isoformat(),
            'project': 'AXIOM E-Key 2W',
            'summary': {
                'overall_risk_level': 'Medium',
                'critical_defects': 0,
                'resource_bottlenecks': 0,
                'at_risk_sprints': 0
            },
            'critical_defects': self.analyze_critical_defects(),
            'resource_constraints': self.analyze_resource_constraints(),
            'domain_risks': self.analyze_domain_risks(),
            'sprint_risks': self.analyze_sprint_risks(),
            'mitigation_strategies': self._generate_mitigations()
        }
        
        # Calculate summary metrics
        report['summary']['critical_defects'] = len([d for d in report['critical_defects'] 
                                                      if d['priority'] == 'Critical'])
        report['summary']['resource_bottlenecks'] = len(report['resource_constraints'])
        report['summary']['at_risk_sprints'] = len([s for s in report['sprint_risks'] 
                                                     if s['risk_level'] in ['High', 'Critical']])
        
        return report
    
    def _assess_impact(self, item: pd.Series) -> str:
        """Assess the business impact of a defect."""
        priority = item.get('Priority', 'Medium')
        summary = str(item.get('Summary', '')).lower()
        
        if priority == 'Critical' or 'security' in summary or 'boundary' in summary:
            return 'High'
        elif priority == 'High' or 'latency' in summary:
            return 'Medium'
        else:
            return 'Low'
    
    def _suggest_mitigation(self, item: pd.Series) -> str:
        """Suggest mitigation strategy for a defect."""
        summary = str(item.get('Summary', '')).lower()
        
        if 'security' in summary:
            return 'Prioritize security review and patching'
        elif 'latency' in summary:
            return 'Performance optimization task required'
        elif 'boundary' in summary:
            return 'Edge case testing and validation needed'
        else:
            return 'Standard defect resolution process'
    
    def _resource_recommendations(self, resource: pd.Series) -> List[str]:
        """Generate recommendations for high-allocation resources."""
        allocation = resource.get('Allocation_%', 0)
        recommendations = []
        
        if allocation >= 100:
            recommendations.append('Consider task redistribution')
            recommendations.append('Monitor for burnout and quality issues')
        elif allocation >= 90:
            recommendations.append('Limit new assignments')
            recommendations.append('Monitor capacity closely')
        
        return recommendations
    
    def _find_resource_domain(self, assignee: str) -> str:
        """Find the domain of a resource from competency data."""
        if self.competency_data is None or not assignee or assignee == 'Unknown':
            return 'Unknown'
        
        resource_data = self.competency_data[
            self.competency_data['associate'] == assignee
        ]
        
        if not resource_data.empty:
            return resource_data.iloc[0]['domain']
        
        return 'Unknown'
    
    def _calculate_sprint_risk(self, sprint_issues: pd.DataFrame) -> str:
        """Calculate overall risk level for a sprint."""
        critical_pct = len(sprint_issues[sprint_issues['Priority'] == 'Critical']) / len(sprint_issues) * 100
        open_pct = len(sprint_issues[sprint_issues['Status'].isin(['Open'])]) / len(sprint_issues) * 100
        
        if critical_pct > 20 or open_pct > 30:
            return 'Critical'
        elif critical_pct > 10 or open_pct > 15:
            return 'High'
        elif critical_pct > 5 or open_pct > 10:
            return 'Medium'
        else:
            return 'Low'
    
    def _identify_focus_areas(self, sprint_issues: pd.DataFrame) -> List[str]:
        """Identify key focus areas for a sprint based on issues."""
        focus = []
        
        if len(sprint_issues[sprint_issues['Priority'] == 'Critical']) > 0:
            focus.append('Critical items resolution')
        
        if len(sprint_issues[sprint_issues['Type'] == 'Bug']) > 0:
            focus.append('Defect fixing')
        
        if len(sprint_issues[sprint_issues['Status'] == 'In Progress']) > len(sprint_issues) / 2:
            focus.append('Completion acceleration')
        
        return focus if focus else ['Regular feature development']
    
    def _generate_mitigations(self) -> Dict:
        """Generate comprehensive mitigation strategies."""
        return {
            'resource_management': [
                'Balance workload across teams',
                'Cross-train team members for critical skills',
                'Prioritize security engineer allocation for Sprints 4-5',
                'Plan QA capacity expansion before Alpha exit'
            ],
            'defect_management': [
                'Implement boundary-zone testing protocol',
                'Add low-power phone validation to test matrix',
                'Establish revocation cache invalidation process',
                'Deploy security event audit logging'
            ],
            'schedule_management': [
                'Buffer time in PI-2 for latency optimization',
                'Pre-allocate security resources for PI-3',
                'Front-load QA activities in PI-2 and PI-3',
                'Plan release hardening activities early in PI-4'
            ],
            'technical_mitigations': [
                'Implement robust proximity decision algorithm',
                'Add firmware cache invalidation hooks',
                'Enhance security audit trail capabilities',
                'Develop offline synchronization mechanism'
            ]
        }
    
    def export_report(self, output_path: str):
        """Export risk report to JSON file."""
        report = self.generate_risk_report()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Risk report exported to {output_path}")
    
    def print_summary(self):
        """Print risk summary to console."""
        report = self.generate_risk_report()
        
        print("\n" + "="*80)
        print("AXIOM E-Key 2W PROJECT RISK MANAGEMENT REPORT")
        print("="*80)
        print(f"Generated: {report['generated_date']}")
        print(f"\nRISK SUMMARY:")
        print(f"  Overall Risk Level: {report['summary']['overall_risk_level']}")
        print(f"  Critical Defects: {report['summary']['critical_defects']}")
        print(f"  Resource Bottlenecks: {report['summary']['resource_bottlenecks']}")
        print(f"  At-Risk Sprints: {report['summary']['at_risk_sprints']}")
        
        print(f"\nCRITICAL DEFECTS ({len(report['critical_defects'])}):")
        for defect in report['critical_defects'][:5]:  # Top 5
            print(f"  - {defect['id']}: {defect['summary']}")
            print(f"    Status: {defect['status']}, Assignee: {defect['assignee']}")
            print(f"    Impact: {defect['impact']}")
        
        print(f"\nRESOURCE CONSTRAINTS:")
        for resource_id, constraint in list(report['resource_constraints'].items())[:5]:
            print(f"  - {resource_id} ({constraint['name']}): {constraint['allocation']}%")
            print(f"    Risk Level: {constraint['risk_level']}")
        
        print(f"\nDOMAIN RISKS:")
        for domain, risks in report['domain_risks'].items():
            print(f"  - {domain}: {risks['open_defects']} open, {risks['critical_items']} critical")
        
        print("\n" + "="*80 + "\n")


class RiskDashboardAPI:
    """Flask API for risk management dashboard and querying."""
    
    def __init__(self, analyzer: RiskAnalyzer, port: int = 5000):
        """Initialize dashboard API with risk analyzer."""
        self.app = Flask(__name__)
        CORS(self.app)
        self.analyzer = analyzer
        self.port = port
        self.logger = logging.getLogger(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes for risk management API."""
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'healthy', 'service': 'Risk Management Dashboard'})
        
        @self.app.route('/api/risk-summary', methods=['GET'])
        def risk_summary():
            """Get overall risk summary."""
            report = self.analyzer.generate_risk_report()
            return jsonify(report['summary'])
        
        @self.app.route('/api/critical-defects', methods=['GET'])
        def critical_defects():
            """Get critical defects with optional filtering."""
            priority = request.args.get('priority', 'all').upper()
            status = request.args.get('status', 'all').upper()
            domain = request.args.get('domain', 'all').upper()
            
            defects = self.analyzer.analyze_critical_defects()
            
            # Apply filters
            if priority != 'ALL':
                defects = [d for d in defects if d['priority'].upper() == priority]
            if status != 'ALL':
                defects = [d for d in defects if d['status'].upper() == status]
            
            return jsonify({
                'total_count': len(defects),
                'defects': defects
            })
        
        @self.app.route('/api/resource-constraints', methods=['GET'])
        def resource_constraints():
            """Get resource constraints and bottlenecks."""
            allocation_threshold = request.args.get('threshold', 80, type=int)
            
            constraints = self.analyzer.analyze_resource_constraints()
            
            return jsonify({
                'total_constrained': len(constraints),
                'threshold_percent': allocation_threshold,
                'resources': constraints
            })
        
        @self.app.route('/api/domain-risks', methods=['GET'])
        def domain_risks():
            """Get risks by technical domain."""
            domain = request.args.get('domain', None)
            
            risks = self.analyzer.analyze_domain_risks()
            
            if domain and domain in risks:
                return jsonify({domain: risks[domain]})
            
            return jsonify(risks)
        
        @self.app.route('/api/sprint-risks', methods=['GET'])
        def sprint_risks():
            """Get sprint-level risk analysis."""
            sprint_id = request.args.get('sprint_id', None)
            risk_level = request.args.get('risk_level', 'all').upper()
            
            risks = self.analyzer.analyze_sprint_risks()
            
            if sprint_id:
                risks = [r for r in risks if r['sprint_id'] == sprint_id]
            
            if risk_level != 'ALL':
                risks = [r for r in risks if r['risk_level'].upper() == risk_level]
            
            return jsonify({
                'total_sprints': len(risks),
                'sprints': risks
            })
        
        @self.app.route('/api/mitigation-strategies', methods=['GET'])
        def mitigation_strategies():
            """Get mitigation strategies for identified risks."""
            report = self.analyzer.generate_risk_report()
            return jsonify(report['mitigation_strategies'])
        
        @self.app.route('/api/risk-query', methods=['POST'])
        def risk_query():
            """Advanced risk query with custom filters."""
            query_params = request.get_json() or {}
            
            response = {
                'query_timestamp': datetime.now().isoformat(),
                'filters_applied': query_params,
                'results': {}
            }
            
            # Analyze defects if requested
            if query_params.get('include_defects', False):
                defects = self.analyzer.analyze_critical_defects()
                if query_params.get('defect_priority'):
                    defects = [d for d in defects 
                              if d['priority'].upper() == query_params['defect_priority'].upper()]
                response['results']['defects'] = defects
            
            # Analyze resources if requested
            if query_params.get('include_resources', False):
                resources = self.analyzer.analyze_resource_constraints()
                response['results']['resources'] = resources
            
            # Analyze domains if requested
            if query_params.get('include_domains', False):
                domains = self.analyzer.analyze_domain_risks()
                response['results']['domains'] = domains
            
            # Analyze sprints if requested
            if query_params.get('include_sprints', False):
                sprints = self.analyzer.analyze_sprint_risks()
                response['results']['sprints'] = sprints
            
            # Generate mitigation strategies
            if query_params.get('include_mitigations', False):
                full_report = self.analyzer.generate_risk_report()
                response['results']['mitigations'] = full_report['mitigation_strategies']
            
            # If no specific analysis requested, return full report
            if not response['results']:
                response['results'] = self.analyzer.generate_risk_report()
            
            return jsonify(response)
        
        @self.app.route('/api/full-report', methods=['GET'])
        def full_report():
            """Get complete risk management report."""
            report = self.analyzer.generate_risk_report()
            return jsonify(report)
        
        @self.app.route('/api/risk-score', methods=['GET'])
        def risk_score():
            """Calculate overall project risk score (0-100)."""
            report = self.analyzer.generate_risk_report()
            summary = report['summary']
            
            # Risk scoring logic
            defect_score = min(summary.get('critical_defects', 0) * 5, 40)
            resource_score = min(summary.get('resource_bottlenecks', 0) * 3, 30)
            sprint_score = min(summary.get('at_risk_sprints', 0) * 4, 30)
            
            total_score = defect_score + resource_score + sprint_score
            
            risk_level = 'Low' if total_score < 30 else 'Medium' if total_score < 60 else 'High'
            
            return jsonify({
                'overall_score': total_score,
                'risk_level': risk_level,
                'component_scores': {
                    'defects': defect_score,
                    'resources': resource_score,
                    'sprints': sprint_score
                },
                'recommendation': self._score_recommendation(total_score)
            })
        
        @self.app.errorhandler(400)
        def bad_request(error):
            """Handle bad request errors."""
            return jsonify({'error': 'Bad request', 'message': str(error)}), 400
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle not found errors."""
            return jsonify({'error': 'Not found', 'message': str(error)}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle internal server errors."""
            self.logger.error(f"Internal error: {error}")
            return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
    
    def _score_recommendation(self, score: float) -> str:
        """Generate recommendation based on risk score."""
        if score < 20:
            return "Project is healthy. Continue monitoring."
        elif score < 40:
            return "Minor risks detected. Increase monitoring frequency."
        elif score < 60:
            return "Moderate risks identified. Implement mitigation strategies."
        elif score < 80:
            return "High risks present. Escalate to project leadership."
        else:
            return "Critical risks identified. Immediate action required."
    
    def run(self, debug: bool = False):
        """Start Flask development server."""
        logging.basicConfig(level=logging.INFO)
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)
    
    def get_app(self):
        """Get Flask app instance for production deployment."""
        return self.app


def main():
    """Main function to run risk analysis and dashboard API."""
    import sys
    
    # Set data directory to AXIOM project data folder
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Create analyzer
    analyzer = RiskAnalyzer(str(data_dir))
    
    # Check if running as API server or CLI
    if '--api' in sys.argv or '--server' in sys.argv:
        # Start Flask API server
        port = 5000
        if '--port' in sys.argv:
            port_idx = sys.argv.index('--port') + 1
            if port_idx < len(sys.argv):
                port = int(sys.argv[port_idx])
        
        print(f"Starting Risk Management Dashboard API on port {port}...")
        api = RiskDashboardAPI(analyzer, port=port)
        api.run(debug=False)
    else:
        # Run CLI mode
        print("Running in CLI mode. Use --api flag to start API server.")
        analyzer.print_summary()
        
        # Export full report
        output_file = Path(__file__).parent / "risk_analysis_report.json"
        analyzer.export_report(str(output_file))
    
    return analyzer


if __name__ == "__main__":
    main()
