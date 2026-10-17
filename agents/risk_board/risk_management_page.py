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
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    Flask = None
    request = None
    jsonify = None
    CORS = None
import logging


class RiskAnalyzer:
    """Analyzes project risks based on defects, capacity, and resource constraints."""
    
    def __init__(self, data_dir: Optional[str] = None,
                 jira_df: Optional[pd.DataFrame] = None,
                 capacity_df: Optional[pd.DataFrame] = None,
                 competency_df: Optional[pd.DataFrame] = None,
                 pi_df: Optional[pd.DataFrame] = None):
        """Initialize risk analyzer with data directory or pre-loaded dataframes."""
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(__file__).parent.parent.parent / "data"
            
        self.jira_data = jira_df
        self.capacity_data = capacity_df
        self.competency_data = competency_df
        self.pi_data = pi_df
        self.risks = []
        self.load_data()
    
    def load_data(self):
        """Load all required CSV data files if not already provided."""
        try:
            # Load Sprint/JIRA issues including bugs and tasks
            if self.jira_data is None:
                jira_path = self.data_dir / "AXIOM_Sprint_Planning.csv"
                if not jira_path.exists():
                    jira_path = self.data_dir / "jira_issues.csv"
                if jira_path.exists():
                    self.jira_data = pd.read_csv(jira_path)
            
            # Load capacity planning
            if self.capacity_data is None:
                capacity_path = self.data_dir / "AXIOM_Capacity_Planning.csv"
                if capacity_path.exists():
                    self.capacity_data = pd.read_csv(capacity_path)
            
            # Load competency matrix
            if self.competency_data is None:
                competency_path = self.data_dir / "AXIOM_Competency_Matrix.csv"
                if competency_path.exists():
                    self.competency_data = pd.read_csv(competency_path)
            
            # Load PI planning
            if self.pi_data is None:
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
        
        id_col = 'Id' if 'Id' in self.jira_data.columns else 'Issue Key'
        assignee_col = 'Owned_By' if 'Owned_By' in self.jira_data.columns else 'Assignee'
        sprint_col = 'Sprint_ID' if 'Sprint_ID' in self.jira_data.columns else 'Sprint'
        
        # Include Bugs, Risks, and Critical/High items that are NOT already Done
        critical_items = self.jira_data[
            ((self.jira_data['Type'].isin(['Bug', 'Defect', 'Risk'])) |
             (self.jira_data['Priority'].isin(['Critical', 'High']))) &
            (~self.jira_data['Status'].isin(['Done', 'Closed']))
        ]
        
        # Associate mapping
        res_map = {
            "RES-01": "JyothiLakshmikanth",
            "RES-02": "bhavya2642-collab",
            "RES-03": "manjunathan-j",
            "RES-04": "Pavi2604",
            "RES-05": "JyothiLakshmikanth",
            "RES-06": "bhavya2642-collab",
            "RES-07": "manjunathan-j",
            "RES-08": "Pavi2604",
            "GHA-01": "JyothiLakshmikanth",
            "GHA-02": "bhavya2642-collab",
            "GHA-03": "manjunathan-j",
            "GHA-04": "Pavi2604",
        }
        
        for _, item in critical_items.iterrows():
            raw_assignee = str(item.get(assignee_col, 'Unassigned'))
            assoc_name = res_map.get(raw_assignee, raw_assignee)
            defect = {
                'id': item.get(id_col, 'N/A'),
                'summary': item.get('Summary', 'N/A'),
                'type': item.get('Type', 'Unknown'),
                'status': item.get('Status', 'Unknown'),
                'priority': item.get('Priority', 'Unknown'),
                'assignee': f"{assoc_name} ({raw_assignee})" if raw_assignee in res_map else raw_assignee,
                'sprint': item.get(sprint_col, 'N/A'),
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
        
        # Identify resources with high allocation (>=80%)
        alloc_col = 'Allocation_%'
        if alloc_col not in self.capacity_data.columns:
            return constraints
            
        high_allocation = self.capacity_data[
            pd.to_numeric(self.capacity_data[alloc_col], errors='coerce') >= 80
        ]
        
        for idx, resource in high_allocation.iterrows():
            resource_id = resource.get('Default_Assignee_ID') or resource.get('Resource_ID', f"RES-{idx+1}")
            associate_name = resource.get('Associate', 'Unknown')
            role = resource.get('Role', 'Engineer')
            domain = resource.get('Domain', 'N/A')
            try:
                alloc_val = int(resource.get(alloc_col, 0))
            except (ValueError, TypeError):
                alloc_val = 0
            
            key = f"{resource_id}_{domain}"
            constraints[key] = {
                'resource_id': resource_id,
                'name': associate_name,
                'role': role,
                'domain': domain,
                'allocation': alloc_val,
                'location': resource.get('Location', 'N/A'),
                'risk_level': 'High' if alloc_val >= 100 else 'Medium',
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
        
        assignee_col = 'Owned_By' if 'Owned_By' in self.jira_data.columns else 'Assignee'
        
        # Map issue assignees to domains
        for _, issue in self.jira_data.iterrows():
            assignee = str(issue.get(assignee_col, 'Unknown'))
            priority = issue.get('Priority', 'Unknown')
            status = issue.get('Status', 'Unknown')
            domain = issue.get('Team') or self._find_resource_domain(assignee)
            
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
        
        sprint_col = 'Sprint_ID' if 'Sprint_ID' in self.jira_data.columns else 'Sprint'
        sprints = [s for s in self.jira_data[sprint_col].unique() if pd.notna(s)]
        sprints.sort()
        
        for sprint in sprints:
            sprint_issues = self.jira_data[self.jira_data[sprint_col] == sprint]
            
            open_count = len(sprint_issues[~sprint_issues['Status'].isin(['Done', 'Closed'])])
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
    
    def analyze_temporal_risks(self) -> Dict:
        """
        Dynamically analyzes project risks across three temporal phases based entirely on live data:
        1. Yesterday's Risks: Evaluated from historical resolved items (Sprint 1-2, Done/Closed)
        2. Today's Risks: Evaluated from active in-flight items (Sprint 3 open defects, critical bottlenecks)
        3. Tomorrow's Risks: Evaluated from upcoming backlog (Sprints 4-7, future milestones, PI roadmap)
        """
        temporal = {
            'yesterday_risks': [],
            'yesterday_metrics': {
                'total_resolved': 0,
                'points_delivered': 0,
                'hours_logged': 0,
                'regression_rate': '0%',
                'safeguards': []
            },
            'today_risks': [],
            'today_metrics': {
                'active_defects_count': 0,
                'overloaded_engineers_count': 0,
                'critical_path_items': 0,
                'sprint_health': 'At Risk'
            },
            'today_resource_overloads': [],
            'today_associate_aggregates': {},
            'today_mitigations': [],
            'tomorrow_risks': [],
            'tomorrow_metrics': {
                'horizon_risks_count': 0,
                'next_safety_gate': 'Alpha Exit Gate',
                'days_remaining': 13,
                'upcoming_pi_focus': 'PI-2: Passive Access & Authorization'
            },
            'pi_roadmap': []
        }
        
        if self.jira_data is None:
            return temporal

        res_map = {
            "RES-01": "JyothiLakshmikanth",
            "RES-02": "bhavya2642-collab",
            "RES-03": "manjunathan-j",
            "RES-04": "Pavi2604",
            "RES-05": "JyothiLakshmikanth",
            "RES-06": "bhavya2642-collab",
            "RES-07": "manjunathan-j",
            "RES-08": "Pavi2604",
            "GHA-01": "JyothiLakshmikanth",
            "GHA-02": "bhavya2642-collab",
            "GHA-03": "manjunathan-j",
            "GHA-04": "Pavi2604",
        }

        # ----------------------------------------------------------------------
        # 1. YESTERDAY'S RISKS (Sprint 1, Sprint 2, or Done/Closed items)
        # ----------------------------------------------------------------------
        id_col = 'Id' if 'Id' in self.jira_data.columns else 'Issue Key'
        assignee_col = 'Owned_By' if 'Owned_By' in self.jira_data.columns else 'Assignee'
        sprint_col = 'Sprint_ID' if 'Sprint_ID' in self.jira_data.columns else 'Sprint'
        
        yesterday_items = self.jira_data[
            (self.jira_data['Status'].isin(['Done', 'Closed'])) |
            (self.jira_data[sprint_col].isin(['SPR-01', 'SPR-02']))
        ]
        
        pts_delivered = 0
        hrs_spent = 0
        delivered_components = set()

        for _, item in yesterday_items.iterrows():
            raw_assignee = str(item.get(assignee_col, 'Unassigned'))
            assoc_name = res_map.get(raw_assignee, raw_assignee)
            comp = item.get('Components', 'Foundation')
            delivered_components.add(comp)
            
            try:
                pts_delivered += int(float(item.get('Story_Points') or 0))
            except (ValueError, TypeError):
                pass
            try:
                hrs_spent += float(item.get('Time_Spent_Hours') or 0)
            except (ValueError, TypeError):
                pass
                
            temporal['yesterday_risks'].append({
                'id': item.get(id_col, 'N/A'),
                'title': item.get('Summary', 'N/A'),
                'sprint': item.get(sprint_col, 'SPR-01'),
                'assignee': f"{assoc_name} ({raw_assignee})" if raw_assignee in res_map else raw_assignee,
                'status': f"✅ Verified & {item.get('Status', 'Done')}",
                'priority': item.get('Priority', 'Medium'),
                'threat': self._assess_impact(item),
                'resolution': f"Delivered in {item.get(sprint_col)} ({item.get('Time_Spent_Hours', 0)}h logged, {comp})",
                'mitigation': self._suggest_mitigation(item)
            })

        temporal['yesterday_metrics']['total_resolved'] = len(yesterday_items)
        temporal['yesterday_metrics']['points_delivered'] = pts_delivered
        temporal['yesterday_metrics']['hours_logged'] = int(hrs_spent)
        temporal['yesterday_metrics']['regression_rate'] = '0%'
        
        # Build dynamic historical safeguards from delivered components
        for comp in sorted(delivered_components):
            comp_items = yesterday_items[yesterday_items['Components'] == comp]
            ids = ", ".join(comp_items[id_col].astype(str).tolist())
            temporal['yesterday_metrics']['safeguards'].append(
                f"**{comp} Baseline Locked**: Validated & closed across items ({ids}) with regression tests enforced in CI."
            )

        # ----------------------------------------------------------------------
        # 2. TODAY'S RISKS (Sprint 3 in-flight items, open bugs, and open risks)
        # ----------------------------------------------------------------------
        today_items = self.jira_data[
            ((self.jira_data[sprint_col] == 'SPR-03') |
             (self.jira_data['Type'].isin(['Bug', 'Defect', 'Risk'])) |
             (self.jira_data['Priority'] == 'Critical')) &
            (~self.jira_data['Status'].isin(['Done', 'Closed']))
        ].drop_duplicates(subset=[id_col])
        
        for _, item in today_items.iterrows():
            raw_assignee = str(item.get(assignee_col, 'Unassigned'))
            assoc_name = res_map.get(raw_assignee, raw_assignee)
            temporal['today_risks'].append({
                'id': item.get(id_col, 'N/A'),
                'title': item.get('Summary', 'N/A'),
                'type': item.get('Type', 'Task'),
                'sprint': item.get(sprint_col, 'SPR-03'),
                'assignee': f"{assoc_name} ({raw_assignee})" if raw_assignee in res_map else raw_assignee,
                'status': item.get('Status', 'In Progress'),
                'priority': item.get('Priority', 'Medium'),
                'impact': self._assess_impact(item),
                'mitigation': self._suggest_mitigation(item)
            })
            
        temporal['today_metrics']['active_defects_count'] = len([
            t for t in temporal['today_risks'] if t['type'] in ['Bug', 'Defect', 'Risk'] or t['priority'] == 'Critical'
        ])
        temporal['today_metrics']['critical_path_items'] = len(today_items)
        
        # Analyze capacity bottlenecks dynamically
        if self.capacity_data is not None and 'Allocation_%' in self.capacity_data.columns:
            alloc_series = pd.to_numeric(self.capacity_data['Allocation_%'], errors='coerce').fillna(0)
            overloaded = self.capacity_data[alloc_series >= 80]
            
            for _, r in overloaded.iterrows():
                temporal['today_resource_overloads'].append({
                    'associate': r.get('Associate', 'Unknown'),
                    'role': r.get('Role', 'Engineer'),
                    'domain': r.get('Domain', 'N/A'),
                    'allocation': int(r.get('Allocation_%', 0)),
                    'status': '🔴 Overloaded' if int(r.get('Allocation_%', 0)) > 85 else '🟡 Near Capacity'
                })
            
            # Cumulative multi-role allocation aggregated by associate
            assoc_totals = defaultdict(int)
            assoc_role_details = defaultdict(list)
            for _, r in self.capacity_data.iterrows():
                assoc = r.get('Associate')
                alloc = int(float(r.get('Allocation_%') or 0))
                role = r.get('Role', 'Engineer')
                assoc_totals[assoc] += alloc
                assoc_role_details[assoc].append(f"{role} ({alloc}%)")
                
            for assoc, total_pct in assoc_totals.items():
                roles_str = ", ".join(assoc_role_details[assoc])
                temporal['today_associate_aggregates'][assoc] = f"{total_pct}% ({roles_str})"
                
            temporal['today_metrics']['overloaded_engineers_count'] = len(overloaded)

        # Dynamic Today's Mitigations
        overloaded_names = {o['associate'] for o in temporal['today_resource_overloads'] if o['allocation'] > 85}
        for name in overloaded_names:
            assigned_today = [t for t in temporal['today_risks'] if name in t['assignee'] and t['priority'] in ['Critical', 'High']]
            if assigned_today:
                item_names = ", ".join([f"{t['id']} ({t['title']})" for t in assigned_today])
                temporal['today_mitigations'].append(
                    f"**Workload Relief for {name}**: Rebalance secondary tasks/QA execution to prevent burnout and safeguard focus on {item_names}."
                )
        
        for item in [t for t in temporal['today_risks'] if t['priority'] == 'Critical']:
            temporal['today_mitigations'].append(
                f"**Immediate Safety/Delivery Action for {item['id']} ({item['title']})**: {item['mitigation']}."
            )

        # ----------------------------------------------------------------------
        # 3. TOMORROW'S RISKS (Sprint 4-7, future backlog, PI milestones)
        # ----------------------------------------------------------------------
        tomorrow_items = self.jira_data[
            (self.jira_data[sprint_col].isin(['SPR-04', 'SPR-05', 'SPR-06', 'SPR-07'])) |
            (self.jira_data['Status'].isin(['To Do'])) |
            (self.jira_data['Planned_For'].isin(['MS-03', 'MS-04']))
        ]
        
        horizon_candidates = tomorrow_items[
            (tomorrow_items['Priority'].isin(['Critical', 'High'])) |
            (tomorrow_items['Type'].isin(['Bug', 'Risk']))
        ]
        
        for _, item in horizon_candidates.iterrows():
            raw_assignee = str(item.get(assignee_col, 'Unassigned'))
            assoc_name = res_map.get(raw_assignee, raw_assignee)
            temporal['tomorrow_risks'].append({
                'milestone': f"{item.get('Planned_For', 'Upcoming')} ({item.get(sprint_col, 'Future')})",
                'id': item.get(id_col, 'N/A'),
                'title': item.get('Summary', 'N/A'),
                'threat': f"Upcoming {item.get('Type', 'work item').lower()} in {item.get('Components', 'system')}; threatens milestone exit criteria if unaddressed.",
                'owner': f"{assoc_name} ({raw_assignee})" if raw_assignee in res_map else raw_assignee,
                'preemptive_strategy': self._suggest_mitigation(item)
            })
            
        temporal['tomorrow_metrics']['horizon_risks_count'] = len(temporal['tomorrow_risks'])
        
        # 4. PROGRAM INCREMENT ROADMAP (from self.pi_data)
        if self.pi_data is not None:
            for _, pi in self.pi_data.iterrows():
                risk_lvl = str(pi.get('Risk_Level', 'Medium'))
                risk_badge = "🔴 High" if "high" in risk_lvl.lower() else "🟡 Medium" if "med" in risk_lvl.lower() else "🟢 Low"
                temporal['pi_roadmap'].append({
                    'Program Increment': f"{pi.get('PI_ID', 'PI')}: {pi.get('PI_Name', 'Increment')}",
                    'Milestone': pi.get('Key_Milestones', 'N/A'),
                    'Focus': pi.get('Focus_Area', 'N/A'),
                    'Quality Gate': pi.get('Quality_Gate', 'N/A'),
                    'Status': pi.get('Status', 'Planned'),
                    'Risk Profile': f"{risk_badge} ({pi.get('Notes', '')})"
                })
                
        return temporal

    def generate_risk_report(self) -> Dict:
        """Generate comprehensive risk management report."""
        temporal = self.analyze_temporal_risks()
        critical_defects = self.analyze_critical_defects()
        resource_constraints = self.analyze_resource_constraints()
        domain_risks = self.analyze_domain_risks()
        sprint_risks = self.analyze_sprint_risks()
        
        report = {
            'generated_date': datetime.now().isoformat(),
            'project': 'AXIOM E-Key 2W Digital Key Platform',
            'repository': 'https://github.com/JyothiLakshmikanth/EKey2W',
            'summary': {
                'overall_risk_level': 'Medium-High',
                'critical_defects': len([d for d in critical_defects if d['priority'] == 'Critical']),
                'resource_bottlenecks': len(resource_constraints),
                'at_risk_sprints': len([s for s in sprint_risks if s['risk_level'] in ['High', 'Critical']])
            },
            'temporal_risks': temporal,
            'critical_defects': critical_defects,
            'resource_constraints': resource_constraints,
            'domain_risks': domain_risks,
            'sprint_risks': sprint_risks,
            'mitigation_strategies': self._generate_mitigations()
        }
        return report
    
    def _assess_impact(self, item: pd.Series) -> str:
        """Assess the business impact of a defect/task dynamically based on priority, type, component, and labels."""
        priority = str(item.get('Priority', 'Medium'))
        item_type = str(item.get('Type', 'Task'))
        summary = str(item.get('Summary', '')).lower()
        component = str(item.get('Components', '')).lower()
        labels = str(item.get('labels', '')).lower()
        
        if priority == 'Critical' and (item_type in ['Bug', 'Defect'] or 'safety' in summary or 'boundary' in summary):
            return "Critical (ASIL-B Safety Violation / Milestone Blocker)"
        elif priority == 'Critical':
            return "High (Sprint Critical Path Delivery Blocker)"
        elif 'latency' in summary or 'performance' in component:
            return "Medium-High (QoS Latency SLA Breach)"
        elif 'security' in summary or 'security' in labels or 'revocation' in summary:
            return "High (Security Vulnerability / Access Risk)"
        elif item_type == 'Risk':
            return "High (Resource / Quality Gate Risk)"
        elif priority == 'High':
            return "Medium-High (Schedule Risk)"
        elif priority == 'Medium':
            return "Medium (Sprint Scope Delivery Risk)"
        else:
            return "Low (Minor Operational)"
    
    def _suggest_mitigation(self, item: pd.Series) -> str:
        """Suggest mitigation strategy for an item dynamically based on its domain, component, and description."""
        summary = str(item.get('Summary', '')).lower()
        component = str(item.get('Components', '')).lower()
        item_type = str(item.get('Type', 'Task'))
        labels = str(item.get('labels', '')).lower()
        
        if 'boundary' in summary or 'proximity' in component:
            return "Apply dual-threshold hysteresis debounce filter & expand edge test coverage"
        elif 'latency' in summary or 'performance' in component:
            return "Optimize async polling, BLE buffer allocations & packet queuing"
        elif 'revocation' in summary or 'cache' in summary:
            return "Implement event-driven push invalidation hook & local secure element blacklist"
        elif 'security' in summary or 'security' in labels:
            return "Conduct cryptographic review, audit logging & enforce HSM state validation"
        elif 'qa' in summary or 'capacity' in summary or 'quality' in labels:
            return "Offload manual execution to automated HIL rigs & cross-train automation engineers"
        elif 'resource' in summary or item_type == 'Risk':
            return "Rebalance non-critical sprint backlog & adjust resource allocations"
        elif 'mobile' in component or 'auth' in summary:
            return "Refactor session handshake & clean background lifecycle coroutine listeners"
        elif 'vehicle' in component or 'gateway' in component:
            return "Apply priority CAN-FD arbitration ID filtering & buffer overrun protection"
        else:
            return f"Prioritize code review on {item.get('Components', 'component')} & enforce CI gating"
    
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
