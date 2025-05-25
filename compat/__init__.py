#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compat - Package Conflict Detection Tool
A powerful tool for detecting conflicts between two packages in different package managers.
"""

__version__ = "1.0.0"
__author__ = "Compat Team"
__description__ = "Package Conflict Detection Tool"

from .core.detector import PackageConflictDetector
from .core.universal_detector import UniversalPackageConflictDetector
from .core.types import ConflictType, PackageManager, ConflictResult, PackageInfo

__all__ = [
    "PackageConflictDetector",
    "UniversalPackageConflictDetector", 
    "ConflictType",
    "PackageManager",
    "ConflictResult",
    "PackageInfo",
] 