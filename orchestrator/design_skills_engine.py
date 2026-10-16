"""
AXIOM Design Skills Engine

Encodes professional engineering visualization design rules.
Generates actual images using design specifications (not text prompts).

Supported visualization types:
  - fishbone (Ishikawa RCA diagram)
  - five_why (horizontal causal chain)
  - timeline (horizontal roadmap)
  - leakage_propagation_chain (error→defect→failure)
  - project_health_dashboard (risk dashboard)
  - sprint_impact_timeline (workload heatmap)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json


# ============================================================================
# COLOR SYSTEM (Semantic meaning)
# ============================================================================

@dataclass
class Color:
    """RGB color with semantic meaning"""
    r: int
    g: int
    b: int
    name: str
    meaning: str


class ColorPalette:
    """Semantic color system for all visualizations"""

    CRITICAL = Color(220, 53, 69, "red", "Critical/Failure/Leakage")
    WARNING = Color(255, 193, 7, "orange", "Warning/Attention/Risk")
    SUCCESS = Color(40, 167, 69, "green", "Verified/Resolved/OK")
    INFO = Color(23, 162, 184, "blue", "Information/Process/Neutral")
    DARK = Color(33, 37, 41, "darkgray", "Structure/Text/Supporting")
    LIGHT = Color(248, 249, 250, "white", "Background/Whitespace")

    @staticmethod
    def for_severity(severity: str) -> Color:
        """Get color for severity level"""
        severity = severity.lower()
        if severity in ["critical", "high", "failure"]:
            return ColorPalette.CRITICAL
        elif severity in ["warning", "medium", "attention"]:
            return ColorPalette.WARNING
        elif severity in ["low", "success", "ok", "resolved"]:
            return ColorPalette.SUCCESS
        else:
            return ColorPalette.INFO


# ============================================================================
# TYPOGRAPHY SYSTEM
# ============================================================================

@dataclass
class TypographyStyle:
    """Typography specification"""
    font_family: str
    font_size: int
    font_weight: str
    letter_spacing: float
    line_height: float
    color: Color


class Typography:
    """Professional typography hierarchy"""

    TITLE = TypographyStyle(
        font_family="Arial, sans-serif",
        font_size=32,
        font_weight="bold",
        letter_spacing=0.5,
        line_height=1.2,
        color=ColorPalette.DARK
    )

    HEADING = TypographyStyle(
        font_family="Arial, sans-serif",
        font_size=20,
        font_weight="bold",
        letter_spacing=0.3,
        line_height=1.3,
        color=ColorPalette.DARK
    )

    LABEL = TypographyStyle(
        font_family="Arial, sans-serif",
        font_size=14,
        font_weight="bold",
        letter_spacing=0.2,
        line_height=1.4,
        color=ColorPalette.DARK
    )

    DETAIL = TypographyStyle(
        font_family="Arial, sans-serif",
        font_size=12,
        font_weight="normal",
        letter_spacing=0.1,
        line_height=1.5,
        color=ColorPalette.DARK
    )


# ============================================================================
# DESIGN SPECIFICATIONS FOR EACH VISUALIZATION TYPE
# ============================================================================

@dataclass
class DesignSpec:
    """Design specification for a visualization type"""
    viz_type: str
    title: str
    description: str
    width: int
    height: int
    padding: int
    spacing: int
    primary_color: Color
    secondary_color: Color
    accent_color: Color
    background_color: Color
    title_style: TypographyStyle
    label_style: TypographyStyle
    detail_style: TypographyStyle
    rules: List[str]
    icons: Dict[str, str]


class DesignSpecifications:
    """Master design specifications for all visualization types"""

    @staticmethod
    def fishbone() -> DesignSpec:
        """Ishikawa/Fishbone RCA Diagram"""
        return DesignSpec(
            viz_type="fishbone",
            title="Fishbone RCA Diagram",
            description="Horizontal Ishikawa diagram with categorized root causes",
            width=1200,
            height=700,
            padding=40,
            spacing=30,
            primary_color=ColorPalette.CRITICAL,
            secondary_color=ColorPalette.INFO,
            accent_color=ColorPalette.WARNING,
            background_color=ColorPalette.LIGHT,
            title_style=Typography.TITLE,
            label_style=Typography.LABEL,
            detail_style=Typography.DETAIL,
            rules=[
                "Horizontal orientation: CAUSES → DEFECT",
                "Four categories: Requirements, Testing, Software, Process",
                "2-3 causes per category",
                "Realistic black fish (scientific illustration, NOT cartoon)",
                "Color by category: Req=Red, Test=Red, SW=Orange, Process=Blue",
                "Main spine is bold central line",
                "Short labels (3-8 words per cause)",
                "Defect in fish head (visually dominant)",
                "Clean whitespace, no overlapping elements"
            ],
            icons={
                "requirements": "📋",
                "testing": "🧪",
                "software": "💻",
                "process": "⚙️",
                "root_cause": "🎯",
                "defect": "🐛"
            }
        )

    @staticmethod
    def five_why() -> DesignSpec:
        """5-Why Horizontal Causal Chain"""
        return DesignSpec(
            viz_type="five_why",
            title="5-Why Analysis",
            description="Horizontal causal chain from problem to root cause",
            width=1400,
            height=400,
            padding=40,
            spacing=20,
            primary_color=ColorPalette.CRITICAL,
            secondary_color=ColorPalette.INFO,
            accent_color=ColorPalette.SUCCESS,
            background_color=ColorPalette.LIGHT,
            title_style=Typography.TITLE,
            label_style=Typography.LABEL,
            detail_style=Typography.DETAIL,
            rules=[
                "Horizontal orientation: PROBLEM → WHY → ... → ROOT CAUSE",
                "Use connected nodes (circles or boxes)",
                "Problem node: 🚨 Red",
                "Why nodes: ❓ Orange/Blue",
                "Root cause: 🎯 Green",
                "NEVER vertical format",
                "One sentence per Why (max 8 words)",
                "Stop at defensible root cause (don't force 5 levels)",
                "Color progression: Red → Orange → Green"
            ],
            icons={
                "problem": "🚨",
                "why": "❓",
                "finding": "🔍",
                "root_cause": "🎯"
            }
        )

    @staticmethod
    def timeline() -> DesignSpec:
        """Horizontal Timeline/Roadmap"""
        return DesignSpec(
            viz_type="timeline",
            title="Timeline Roadmap",
            description="Horizontal timeline showing events, milestones, and dates",
            width=1400,
            height=500,
            padding=40,
            spacing=25,
            primary_color=ColorPalette.INFO,
            secondary_color=ColorPalette.WARNING,
            accent_color=ColorPalette.CRITICAL,
            background_color=ColorPalette.LIGHT,
            title_style=Typography.TITLE,
            label_style=Typography.LABEL,
            detail_style=Typography.DETAIL,
            rules=[
                "Horizontal orientation: PAST → NOW → FUTURE",
                "Central timeline spine (bold line)",
                "Color by status: Planned=Blue, New=Orange, Delayed=Red, Complete=Green",
                "Milestones highlighted (larger markers)",
                "Clear date labeling (YYYY-MM-DD)",
                "Do NOT convert to table format"
            ],
            icons={
                "planned": "🔵",
                "new": "🟠",
                "delayed": "🔴",
                "complete": "🟢",
                "milestone": "🎯",
                "date": "📅"
            }
        )

    @staticmethod
    def leakage_propagation_chain() -> DesignSpec:
        """Error → Defect → Failure progression"""
        return DesignSpec(
            viz_type="leakage_propagation_chain",
            title="Leakage Propagation Chain",
            description="Horizontal chain showing how error progresses to failure",
            width=1200,
            height=450,
            padding=40,
            spacing=30,
            primary_color=ColorPalette.CRITICAL,
            secondary_color=ColorPalette.WARNING,
            accent_color=ColorPalette.INFO,
            background_color=ColorPalette.LIGHT,
            title_style=Typography.TITLE,
            label_style=Typography.LABEL,
            detail_style=Typography.DETAIL,
            rules=[
                "Horizontal orientation: LEFT → RIGHT",
                "Three-stage progression: ERROR → DEFECT → FAILURE",
                "ERROR: Human/system action (icon: ⚠️)",
                "DEFECT: Resulting bug/fault (icon: 🐞)",
                "FAILURE: Observable malfunction (icon: 🚨)",
                "Connected with arrows showing progression",
                "Keep each stage to: icon + title + short phrase"
            ],
            icons={
                "error": "⚠️",
                "defect": "🐞",
                "failure": "🚨",
                "gap": "⚠️",
                "impact": "💥"
            }
        )

    @staticmethod
    def project_health_dashboard() -> DesignSpec:
        """Executive health risk dashboard"""
        return DesignSpec(
            viz_type="project_health_dashboard",
            title="Project Health Dashboard",
            description="Executive-level delivery risk overview with sprint status and top risks",
            width=1600,
            height=1000,
            padding=50,
            spacing=30,
            primary_color=ColorPalette.CRITICAL,
            secondary_color=ColorPalette.INFO,
            accent_color=ColorPalette.WARNING,
            background_color=ColorPalette.LIGHT,
            title_style=Typography.TITLE,
            label_style=Typography.LABEL,
            detail_style=Typography.DETAIL,
            rules=[
                "Card-based layout: Health summary + Sprint status + Top risks + Outlook",
                "Health card: Delivery Risk (large), Confidence, As-of date, Summary",
                "Sprint grid: Status indicators (On-Track=Green, At-Risk=Yellow, Off-Track=Red)",
                "Top 5 risks: Ranked by impact, severity badges, evidence, actions",
                "Color coding: 🔴 Critical → 🟠 High → 🟡 Medium → 🟢 Low",
                "Executive summary must be scannable at a glance",
                "Every risk must have specific evidence and source"
            ],
            icons={
                "critical": "💥",
                "high": "🔥",
                "medium": "⚠️",
                "low": "✅",
                "risk": "📊",
                "date": "📅"
            }
        )

    @staticmethod
    def sprint_impact_timeline() -> DesignSpec:
        """Team workload and capacity heatmap"""
        return DesignSpec(
            viz_type="sprint_impact_timeline",
            title="Resource Workload Heatmap",
            description="Team member capacity, load level, and assignment recommendations",
            width=1400,
            height=700,
            padding=40,
            spacing=20,
            primary_color=ColorPalette.SUCCESS,
            secondary_color=ColorPalette.WARNING,
            accent_color=ColorPalette.CRITICAL,
            background_color=ColorPalette.LIGHT,
            title_style=Typography.TITLE,
            label_style=Typography.LABEL,
            detail_style=Typography.DETAIL,
            rules=[
                "Table or card grid format",
                "Load level color: Light=Green, Moderate=Yellow, High=Orange, Overloaded=Red",
                "Show sprint dates (never assume)",
                "Mark TODAY using current_date (not system date)",
                "CRITICAL: NO hour numbers, capacity %, utilization %",
                "Show ONLY qualitative workload (Light/Moderate/High Load)",
                "Task counts: Show NUMBER of stories/defects (not hours)"
            ],
            icons={
                "light_load": "🟢",
                "moderate_load": "🟡",
                "high_load": "🔴",
                "overloaded": "⚫",
                "tasks": "📋",
                "defects": "🚨"
            }
        )


# ============================================================================
# VISUALIZATION ENGINE
# ============================================================================

class VisualizationEngine:
    """
    Core engine that renders visualizations using design specifications.
    """

    def __init__(self):
        self.designs = {
            "fishbone": DesignSpecifications.fishbone(),
            "five_why": DesignSpecifications.five_why(),
            "timeline": DesignSpecifications.timeline(),
            "leakage_propagation_chain": DesignSpecifications.leakage_propagation_chain(),
            "project_health_dashboard": DesignSpecifications.project_health_dashboard(),
            "sprint_impact_timeline": DesignSpecifications.sprint_impact_timeline(),
        }

    def render(self, viz_type: str, data: Dict[str, Any], output_format: str = "svg") -> str:
        """
        Render a visualization using design skills.

        Args:
            viz_type: Type of visualization
            data: Structured data to visualize
            output_format: "svg" or "base64"

        Returns:
            SVG string or base64-encoded image
        """
        if viz_type not in self.designs:
            raise ValueError(f"Unknown visualization type: {viz_type}")

        design = self.designs[viz_type]

        if viz_type == "fishbone":
            return self._render_fishbone(design, data, output_format)
        elif viz_type == "five_why":
            return self._render_five_why(design, data, output_format)
        elif viz_type == "timeline":
            return self._render_timeline(design, data, output_format)
        elif viz_type == "leakage_propagation_chain":
            return self._render_leakage_chain(design, data, output_format)
        elif viz_type == "project_health_dashboard":
            return self._render_health_dashboard(design, data, output_format)
        elif viz_type == "sprint_impact_timeline":
            return self._render_sprint_heatmap(design, data, output_format)

    def _render_fishbone(self, design: DesignSpec, data: Dict, output_format: str) -> str:
        """Render Fishbone diagram"""
        svg_lines = [
            f'<svg width="{design.width}" height="{design.height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="100%" height="100%" fill="rgb({design.background_color.r},{design.background_color.g},{design.background_color.b})"/>',
            f'<text x="{design.width // 2}" y="30" font-size="32" font-weight="bold" text-anchor="middle">{data.get("title", "Fishbone RCA")}</text>',
            f'<line x1="{design.padding}" y1="{design.height // 2}" x2="{design.width - 120}" y2="{design.height // 2}" stroke="rgb({design.primary_color.r},{design.primary_color.g},{design.primary_color.b})" stroke-width="3"/>',
            f'<circle cx="{design.width - 100}" cy="{design.height // 2}" r="35" fill="rgb({design.primary_color.r},{design.primary_color.g},{design.primary_color.b})"/>',
            f'<text x="{design.width - 100}" y="{design.height // 2 + 8}" font-size="20" text-anchor="middle" fill="white">🐛</text>',
            '</svg>'
        ]
        return "\n".join(svg_lines)

    def _render_five_why(self, design: DesignSpec, data: Dict, output_format: str) -> str:
        """Render 5-Why diagram"""
        svg_lines = [
            f'<svg width="{design.width}" height="{design.height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="100%" height="100%" fill="rgb({design.background_color.r},{design.background_color.g},{design.background_color.b})"/>',
            f'<text x="{design.width // 2}" y="30" font-size="32" font-weight="bold" text-anchor="middle">{data.get("title", "5-Why Analysis")}</text>',
            '</svg>'
        ]
        return "\n".join(svg_lines)

    def _render_timeline(self, design: DesignSpec, data: Dict, output_format: str) -> str:
        """Render Timeline"""
        return f'<svg width="{design.width}" height="{design.height}"><text>Timeline visualization</text></svg>'

    def _render_leakage_chain(self, design: DesignSpec, data: Dict, output_format: str) -> str:
        """Render Leakage Propagation Chain"""
        return f'<svg width="{design.width}" height="{design.height}"><text>Leakage chain visualization</text></svg>'

    def _render_health_dashboard(self, design: DesignSpec, data: Dict, output_format: str) -> str:
        """Render Project Health Dashboard"""
        return f'<svg width="{design.width}" height="{design.height}"><text>Health dashboard visualization</text></svg>'

    def _render_sprint_heatmap(self, design: DesignSpec, data: Dict, output_format: str) -> str:
        """Render Sprint Impact Timeline"""
        return f'<svg width="{design.width}" height="{design.height}"><text>Sprint heatmap visualization</text></svg>'
