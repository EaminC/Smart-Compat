#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Type Definitions Module
Contains all data classes, enum classes and type definitions
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PackageManager(Enum):
    """Package manager types"""
    PIP = "pip"
    NPM = "npm" 
    YARN = "yarn"
    MAVEN = "maven"
    GRADLE = "gradle"
    CONDA = "conda"


class ConflictType(Enum):
    """Conflict type enumeration"""
    VERSION_CONFLICT = "Version Conflict"
    DEPENDENCY_CONFLICT = "Dependency Conflict"
    NAME_CONFLICT = "Name Conflict"
    PEER_DEPENDENCY_CONFLICT = "Peer Dependency Conflict"
    PACKAGE_NOT_FOUND = "Package Not Found"
    NO_CONFLICT = "No Conflict"


@dataclass
class PackageInfo:
    """Universal package information data class"""
    name: str
    version: str
    dependencies: Dict[str, str]  # name: version_constraint
    dev_dependencies: Dict[str, str] = None
    peer_dependencies: Dict[str, str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None


@dataclass
class ConflictResult:
    """Conflict detection result"""
    conflict_type: ConflictType
    message: str
    severity: str = "medium"  # low, medium, high, critical
    details: Dict = None 