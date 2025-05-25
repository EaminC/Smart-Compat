#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compat - Package Conflict Detection Tool
A simplified tool for detecting conflicts between Python packages.
"""

__version__ = "2.0.0"
__author__ = "Compat Team"
__description__ = "Simplified Package Conflict Detection Tool"

from .detectors.basic import PackageConflictDetector
from .detectors.hypothetical import HypotheticalConflictDetector
from .detectors.enhanced import EnhancedConflictDetector
from .analyzers.requirements_analyzer import RequirementsCompatibilityAnalyzer
from .core.types import ConflictType, ConflictResult, PackageInfo

__all__ = [
    "PackageConflictDetector",
    "HypotheticalConflictDetector",
    "EnhancedConflictDetector", 
    "RequirementsCompatibilityAnalyzer",
    "ConflictType",
    "ConflictResult",
    "PackageInfo",
] 