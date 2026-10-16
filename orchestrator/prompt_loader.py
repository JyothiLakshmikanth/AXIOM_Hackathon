"""
AXIOM Prompt Loader — Dynamic prompt assembly for 9-node architecture.
Loads specialized prompts from JSON files, merges sections, and caches to minimize file I/O.
Supports prompt inheritance via __imports__ and stage-based section selection.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger("axiom.orchestrator.prompt_loader")

# Module-level cache to avoid repeated file reads
_PROMPT_CACHE: Dict[str, Dict[str, Any]] = {}
_IMPORTS_CACHE: Dict[str, Dict[str, Any]] = {}


def load_prompt(master_id: str, node_name: str) -> str:
    """
    Load full specialized prompt for a given node from JSON files.

    Assembles prompt by loading sections for the node's stage from the master prompt file.
    Includes __imports__ sections from axiom_prompts_common.json if specified.

    Args:
        master_id: Master identifier (e.g., "axiom_pm", "axiom_eng")
        node_name: Node name (e.g., "reason_node", "execute_action_node", "observe_node")

    Returns:
        Complete prompt string assembled from JSON sections, ready for LLM input

    Raises:
        ValueError: If master prompt file not found
        KeyError: If node_name not found in stage_to_sections mapping
    """
    logger.debug(f"Loading prompt for master={master_id}, node={node_name}")

    try:
        # Load master prompt file
        master_data = _load_json_file(master_id)

        # Get stage_to_sections mapping
        stage_mapping = master_data.get("__structure__", {}).get("stage_to_sections", {})

        if node_name not in stage_mapping:
            logger.warning(f"Node {node_name} not found in stage_to_sections. Available: {list(stage_mapping.keys())}")
            raise KeyError(f"Node '{node_name}' not found in stage mapping for {master_id}")

        # Get sections for this node
        section_names = stage_mapping[node_name]
        logger.debug(f"Node {node_name} requires sections: {section_names}")

        # Load sections from master file
        sections = load_stage_sections(master_id, node_name)

        # Check if we need to include __imports__
        imports_config = master_data.get("__imports__", {})
        if imports_config and imports_config.get("sections"):
            import_sections = _load_imports_from_common(master_id)
            sections.extend(import_sections)
            logger.debug(f"Included {len(import_sections)} imported sections")

        # Merge all sections into single prompt string
        prompt = merge_sections(sections)

        logger.info(f"Successfully loaded prompt for {master_id}/{node_name} ({len(prompt)} chars)")
        return prompt

    except Exception as e:
        logger.error(f"Failed to load prompt for {master_id}/{node_name}: {e}")
        raise


def load_stage_sections(master_id: str, node_name: str) -> List[Dict[str, Any]]:
    """
    Load all section dictionaries required for a given node's stage.

    Retrieves sections from the master prompt file based on __structure__.stage_to_sections mapping.
    Returns list of section objects (each with 'type', 'title', 'content' fields).

    Args:
        master_id: Master identifier (e.g., "axiom_pm", "axiom_eng")
        node_name: Node name (e.g., "reason_node", "execute_action_node")

    Returns:
        List of section dictionaries from the master file

    Raises:
        KeyError: If node or sections not found
    """
    logger.debug(f"Loading stage sections for {master_id}/{node_name}")

    try:
        master_data = _load_json_file(master_id)
        stage_mapping = master_data.get("__structure__", {}).get("stage_to_sections", {})

        if node_name not in stage_mapping:
            raise KeyError(f"Node '{node_name}' not in stage_to_sections")

        section_names = stage_mapping[node_name]
        sections = []

        for section_name in section_names:
            if section_name in master_data:
                sections.append(master_data[section_name])
                logger.debug(f"Loaded section: {section_name}")
            else:
                logger.warning(f"Section '{section_name}' not found in {master_id}")

        return sections

    except Exception as e:
        logger.error(f"Failed to load stage sections: {e}")
        raise


def merge_sections(sections: List[Dict[str, Any]]) -> str:
    """
    Merge multiple section objects into a single coherent prompt string.

    Extracts 'content' array from each section, joins with formatting, and concatenates.
    Preserves section structure with titles for readability.

    Args:
        sections: List of section dictionaries, each with 'title' and 'content' keys

    Returns:
        Single concatenated prompt string with sections properly separated
    """
    logger.debug(f"Merging {len(sections)} sections")

    merged = []

    for section in sections:
        section_title = section.get("title", "")
        content_lines = section.get("content", [])

        if section_title:
            merged.append(f"\n## {section_title}\n")

        if isinstance(content_lines, list):
            merged.extend(content_lines)
        else:
            merged.append(str(content_lines))

        merged.append("")  # blank line between sections

    result = "\n".join(merged).strip()
    logger.debug(f"Merged prompt: {len(result)} characters")
    return result


def load_imports_from_common(master_id: str) -> Dict[str, Any]:
    """
    Load __imports__ configuration from the master prompt file.

    Returns the __imports__ dictionary which specifies which sections should be
    loaded from axiom_prompts_common.json (source file and list of section names).

    Args:
        master_id: Master identifier (e.g., "axiom_pm", "axiom_eng")

    Returns:
        Dictionary with 'source', 'sections', and 'note' keys from __imports__
    """
    logger.debug(f"Loading imports config for {master_id}")

    try:
        master_data = _load_json_file(master_id)
        imports = master_data.get("__imports__", {})

        if not imports:
            logger.debug(f"No __imports__ found for {master_id}")
            return {}

        logger.debug(f"Found imports: {imports.get('sections', [])}")
        return imports

    except Exception as e:
        logger.error(f"Failed to load imports config: {e}")
        return {}


def _load_imports_from_common(master_id: str) -> List[Dict[str, Any]]:
    """
    Internal helper to load and return actual section objects from axiom_prompts_common.json.

    Reads the __imports__ configuration and loads the specified sections from the
    common prompts file, caching results to avoid repeated file reads.

    Args:
        master_id: Master identifier (cached for optimization)

    Returns:
        List of section dictionaries from axiom_prompts_common.json
    """
    cache_key = f"imports_{master_id}"

    if cache_key in _IMPORTS_CACHE:
        logger.debug(f"Using cached imports for {master_id}")
        return _IMPORTS_CACHE[cache_key]

    try:
        # Get imports config
        imports_config = load_imports_from_common(master_id)
        section_names = imports_config.get("sections", [])

        if not section_names:
            return []

        # Load common file
        common_data = _load_json_file("axiom_prompts_common")
        sections = []

        for section_name in section_names:
            if section_name in common_data:
                sections.append(common_data[section_name])
                logger.debug(f"Loaded imported section: {section_name}")
            else:
                logger.warning(f"Imported section '{section_name}' not found in axiom_prompts_common.json")

        # Cache result
        _IMPORTS_CACHE[cache_key] = sections
        logger.debug(f"Cached {len(sections)} imported sections for {master_id}")
        return sections

    except Exception as e:
        logger.error(f"Failed to load imported sections: {e}")
        return []


def _load_json_file(file_key: str) -> Dict[str, Any]:
    """
    Internal helper to load JSON prompt file with caching.

    Looks for prompts/{file_key}_master_v3.json or prompts/{file_key}.json.
    Returns empty dict on error after logging.

    Args:
        file_key: Key for file lookup (e.g., "axiom_pm", "axiom_prompts_common")

    Returns:
        Parsed JSON dictionary, or empty dict if load fails
    """
    if file_key in _PROMPT_CACHE:
        logger.debug(f"Using cached prompt data for {file_key}")
        return _PROMPT_CACHE[file_key]

    # Determine file path
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")

    # Try master file first
    file_paths = [
        os.path.join(prompts_dir, f"{file_key}_master_v3.json"),
        os.path.join(prompts_dir, f"{file_key}.json"),
    ]

    file_path = None
    for candidate in file_paths:
        if os.path.exists(candidate):
            file_path = candidate
            break

    if not file_path:
        logger.error(f"Prompt file not found for {file_key}. Tried: {file_paths}")
        return {}

    try:
        logger.debug(f"Loading prompt file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        _PROMPT_CACHE[file_key] = data
        logger.info(f"Loaded and cached prompt data from {file_path}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
        return {}
    except IOError as e:
        logger.error(f"IO error reading {file_path}: {e}")
        return {}


def clear_cache() -> None:
    """
    Clear all cached prompt data. Useful for testing or dynamic prompt updates.

    Clears both _PROMPT_CACHE and _IMPORTS_CACHE, forcing subsequent loads
    from disk.
    """
    global _PROMPT_CACHE, _IMPORTS_CACHE
    _PROMPT_CACHE.clear()
    _IMPORTS_CACHE.clear()
    logger.info("Cleared all cached prompt data")
