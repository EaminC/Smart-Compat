#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal package conflict detector
Supports multiple package managers
"""

import re
import os
from typing import Dict, List, Tuple, Optional

from .types import PackageManager, ConflictType, ConflictResult, PackageInfo
from ..adapters import PipAdapter, NpmAdapter


class UniversalPackageConflictDetector:
    """Universal package conflict detector"""
    
    def __init__(self):
        self.adapters = {
            PackageManager.PIP: PipAdapter(),
            PackageManager.NPM: NpmAdapter(),
        }
        self.version_pattern = re.compile(r'^(\d+)\.(\d+)\.(\d+).*$')
    
    def detect_package_manager(self, package_name: str = None, project_path: str = ".") -> Optional[PackageManager]:
        """Automatically detect the package manager used by the project"""
        
        # Check project files
        if os.path.exists(os.path.join(project_path, "package.json")):
            return PackageManager.NPM
        elif os.path.exists(os.path.join(project_path, "requirements.txt")) or \
             os.path.exists(os.path.join(project_path, "setup.py")) or \
             os.path.exists(os.path.join(project_path, "pyproject.toml")):
            return PackageManager.PIP
        elif os.path.exists(os.path.join(project_path, "pom.xml")):
            return PackageManager.MAVEN
        elif os.path.exists(os.path.join(project_path, "build.gradle")):
            return PackageManager.GRADLE
        
        # Default check pip
        return PackageManager.PIP
    
    def get_available_package_managers(self) -> List[PackageManager]:
        """Get list of available package managers"""
        available = []
        for pm, adapter in self.adapters.items():
            if adapter.is_available():
                available.append(pm)
        return available
    
    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version number"""
        # Clean version string
        version = re.sub(r'[^\d\.].*', '', version)  # Remove non-digit and non-dot characters
        
        match = self.version_pattern.match(version)
        if match:
            return tuple(map(int, match.groups()))
        
        # Try parsing incomplete version numbers
        parts = version.split('.')
        if len(parts) >= 2:
            try:
                major = int(parts[0])
                minor = int(parts[1])
                patch = int(parts[2]) if len(parts) > 2 else 0
                return (major, minor, patch)
            except ValueError:
                pass
        
        raise ValueError(f"Cannot parse version number: {version}")
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """Compare version numbers"""
        try:
            v1 = self.parse_version(version1)
            v2 = self.parse_version(version2)
            
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
        except ValueError:
            return 0
    
    def check_version_compatibility(self, required_version: str, actual_version: str) -> bool:
        """Check version compatibility"""
        if not required_version or required_version == "*":
            return True
        
        # Handle npm-style version constraints
        if required_version.startswith("^"):
            # Compatible version, major version must be the same
            req_version = required_version[1:]
            try:
                req_parts = self.parse_version(req_version)
                actual_parts = self.parse_version(actual_version)
                return req_parts[0] == actual_parts[0] and actual_parts >= req_parts
            except ValueError:
                return False
        
        elif required_version.startswith("~"):
            # Reasonably close version
            req_version = required_version[1:]
            try:
                req_parts = self.parse_version(req_version)
                actual_parts = self.parse_version(actual_version)
                return (req_parts[0] == actual_parts[0] and 
                       req_parts[1] == actual_parts[1] and
                       actual_parts[2] >= req_parts[2])
            except ValueError:
                return False
        
        elif required_version.startswith(">="):
            req_version = required_version[2:]
            return self.compare_versions(actual_version, req_version) >= 0
        
        elif required_version.startswith("<="):
            req_version = required_version[2:]
            return self.compare_versions(actual_version, req_version) <= 0
        
        elif required_version.startswith(">"):
            req_version = required_version[1:]
            return self.compare_versions(actual_version, req_version) > 0
        
        elif required_version.startswith("<"):
            req_version = required_version[1:]
            return self.compare_versions(actual_version, req_version) < 0
        
        elif required_version.startswith("=="):
            req_version = required_version[2:]
            return self.compare_versions(actual_version, req_version) == 0
        
        else:
            # Exact match
            return self.compare_versions(actual_version, required_version) == 0
    
    def detect_conflicts(self, package1: str, package2: str, 
                        package_manager: PackageManager = None) -> ConflictResult:
        """Detect package conflicts"""
        
        if not package_manager:
            package_manager = self.detect_package_manager()
        
        if package_manager not in self.adapters:
            return ConflictResult(
                conflict_type=ConflictType.NO_CONFLICT,
                message=f"Unsupported package manager: {package_manager.value}",
                severity="low"
            )
        
        adapter = self.adapters[package_manager]
        
        # Parse package specifications (support version specs like "package==1.0.0")
        pkg1_name, pkg1_version_spec = self._parse_package_spec(package1)
        pkg2_name, pkg2_version_spec = self._parse_package_spec(package2)
        
        # Check name conflicts
        if pkg1_name.lower() == pkg2_name.lower():
            if pkg1_version_spec and pkg2_version_spec:
                if pkg1_version_spec != pkg2_version_spec:
                    return ConflictResult(
                        conflict_type=ConflictType.VERSION_CONFLICT,
                        message=f"Version conflict: {package1} conflicts with {package2}",
                        severity="high",
                        details={
                            "package": pkg1_name,
                            "version1": pkg1_version_spec,
                            "version2": pkg2_version_spec
                        }
                    )
                else:
                    return ConflictResult(
                        conflict_type=ConflictType.NO_CONFLICT,
                        message=f"Same package with same version: {package1}",
                        severity="low",
                        details={"package": pkg1_name, "version": pkg1_version_spec}
                    )
            else:
                return ConflictResult(
                    conflict_type=ConflictType.NAME_CONFLICT,
                    message=f"Name conflict: {pkg1_name} appears in both specifications",
                    severity="high",
                    details={"packages": [package1, package2]}
                )
        
        # Get package information
        pkg1_info = adapter.get_package_info(pkg1_name)
        pkg2_info = adapter.get_package_info(pkg2_name)
        
        # Check version compatibility if specified
        if pkg1_info and pkg1_version_spec:
            if not self._check_version_match(pkg1_info.version, pkg1_version_spec):
                return ConflictResult(
                    conflict_type=ConflictType.VERSION_CONFLICT,
                    message=f"Version mismatch: {pkg1_name} v{pkg1_info.version} doesn't satisfy {pkg1_version_spec}",
                    severity="medium",
                    details={"package": pkg1_name, "installed": pkg1_info.version, "required": pkg1_version_spec}
                )
        
        if pkg2_info and pkg2_version_spec:
            if not self._check_version_match(pkg2_info.version, pkg2_version_spec):
                return ConflictResult(
                    conflict_type=ConflictType.VERSION_CONFLICT,
                    message=f"Version mismatch: {pkg2_name} v{pkg2_info.version} doesn't satisfy {pkg2_version_spec}",
                    severity="medium",
                    details={"package": pkg2_name, "installed": pkg2_info.version, "required": pkg2_version_spec}
                )
        
        if not pkg1_info:
            return ConflictResult(
                conflict_type=ConflictType.PACKAGE_NOT_FOUND,
                message=f"Cannot find package: {pkg1_name}",
                severity="warning",
                details={"error": f"Package {pkg1_name} not found"}
            )
        
        if not pkg2_info:
            return ConflictResult(
                conflict_type=ConflictType.PACKAGE_NOT_FOUND,
                message=f"Cannot find package: {pkg2_name}",
                severity="warning",
                details={"error": f"Package {pkg2_name} not found"}
            )
        
        # Check dependency conflicts
        conflicts = self._check_dependency_conflicts(pkg1_info, pkg2_info)
        
        if conflicts:
            severity = "high" if len(conflicts) > 3 else "medium"
            return ConflictResult(
                conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                message=f"Dependency conflicts: {pkg1_name} and {pkg2_name} have {len(conflicts)} dependency conflicts",
                severity=severity,
                details={
                    "conflicts": conflicts,
                    "pkg1": pkg1_info.__dict__,
                    "pkg2": pkg2_info.__dict__
                }
            )
        
        # Check peer dependency conflicts (mainly for npm)
        if pkg1_info.peer_dependencies or pkg2_info.peer_dependencies:
            peer_conflicts = self._check_peer_dependency_conflicts(pkg1_info, pkg2_info)
            if peer_conflicts:
                return ConflictResult(
                    conflict_type=ConflictType.PEER_DEPENDENCY_CONFLICT,
                    message=f"Peer dependency conflicts: {pkg1_name} and {pkg2_name} have peer dependency conflicts",
                    severity="medium",
                    details={
                        "peer_conflicts": peer_conflicts,
                        "pkg1": pkg1_info.__dict__,
                        "pkg2": pkg2_info.__dict__
                    }
                )
        
        return ConflictResult(
            conflict_type=ConflictType.NO_CONFLICT,
            message=f"No conflicts found: {pkg1_name} v{pkg1_info.version} and {pkg2_name} v{pkg2_info.version} can coexist",
            severity="low",
            details={
                "pkg1": pkg1_info.__dict__,
                "pkg2": pkg2_info.__dict__
            }
        )
    
    def _parse_package_spec(self, package_spec: str) -> Tuple[str, Optional[str]]:
        """Parse package specification into name and version"""
        if '==' in package_spec:
            name, version = package_spec.split('==', 1)
            return name.strip(), version.strip()
        elif '>=' in package_spec:
            name, version = package_spec.split('>=', 1)
            return name.strip(), f">={version.strip()}"
        elif '<=' in package_spec:
            name, version = package_spec.split('<=', 1)
            return name.strip(), f"<={version.strip()}"
        elif '>' in package_spec:
            name, version = package_spec.split('>', 1)
            return name.strip(), f">{version.strip()}"
        elif '<' in package_spec:
            name, version = package_spec.split('<', 1)
            return name.strip(), f"<{version.strip()}"
        else:
            return package_spec.strip(), None
    
    def _check_version_match(self, installed_version: str, required_spec: str) -> bool:
        """Check if installed version matches the required specification"""
        if not required_spec or required_spec == "*":
            return True
        
        try:
            if required_spec.startswith(">="):
                req_version = required_spec[2:]
                return self.compare_versions(installed_version, req_version) >= 0
            elif required_spec.startswith("<="):
                req_version = required_spec[2:]
                return self.compare_versions(installed_version, req_version) <= 0
            elif required_spec.startswith(">"):
                req_version = required_spec[1:]
                return self.compare_versions(installed_version, req_version) > 0
            elif required_spec.startswith("<"):
                req_version = required_spec[1:]
                return self.compare_versions(installed_version, req_version) < 0
            else:
                # Exact match for == or plain version
                req_version = required_spec.replace("==", "")
                return self.compare_versions(installed_version, req_version) == 0
        except Exception:
            return False
    
    def _check_dependency_conflicts(self, pkg1: PackageInfo, pkg2: PackageInfo) -> List[str]:
        """Check dependency conflicts"""
        conflicts = []
        
        # Get all dependencies (including dev dependencies)
        all_deps1 = dict(pkg1.dependencies)
        if pkg1.dev_dependencies:
            all_deps1.update(pkg1.dev_dependencies)
        
        all_deps2 = dict(pkg2.dependencies)
        if pkg2.dev_dependencies:
            all_deps2.update(pkg2.dev_dependencies)
        
        # Find common dependencies
        common_deps = set(all_deps1.keys()) & set(all_deps2.keys())
        
        for dep_name in common_deps:
            constraint1 = all_deps1[dep_name]
            constraint2 = all_deps2[dep_name]
            
            if constraint1 != constraint2:
                # Further check version compatibility
                if not self._are_constraints_compatible(constraint1, constraint2):
                    conflicts.append(
                        f"Dependency {dep_name}: {pkg1.name} requires {constraint1}, "
                        f"{pkg2.name} requires {constraint2}"
                    )
        
        return conflicts
    
    def _check_peer_dependency_conflicts(self, pkg1: PackageInfo, pkg2: PackageInfo) -> List[str]:
        """Check peer dependency conflicts"""
        conflicts = []
        
        if not pkg1.peer_dependencies and not pkg2.peer_dependencies:
            return conflicts
        
        peer_deps1 = pkg1.peer_dependencies or {}
        peer_deps2 = pkg2.peer_dependencies or {}
        
        # Check if peer dependencies conflict with each other's dependencies
        for peer_name, peer_constraint in peer_deps1.items():
            if peer_name in pkg2.dependencies:
                pkg2_constraint = pkg2.dependencies[peer_name]
                if not self._are_constraints_compatible(peer_constraint, pkg2_constraint):
                    conflicts.append(
                        f"Peer dependency conflict: {pkg1.name}'s peer dependency {peer_name}({peer_constraint}) "
                        f"is incompatible with {pkg2.name}'s dependency version {pkg2_constraint}"
                    )
        
        for peer_name, peer_constraint in peer_deps2.items():
            if peer_name in pkg1.dependencies:
                pkg1_constraint = pkg1.dependencies[peer_name]
                if not self._are_constraints_compatible(peer_constraint, pkg1_constraint):
                    conflicts.append(
                        f"Peer dependency conflict: {pkg2.name}'s peer dependency {peer_name}({peer_constraint}) "
                        f"is incompatible with {pkg1.name}'s dependency version {pkg1_constraint}"
                    )
        
        return conflicts
    
    def _are_constraints_compatible(self, constraint1: str, constraint2: str) -> bool:
        """Check if two version constraints are compatible"""
        # Simplified compatibility check
        if constraint1 == constraint2 or constraint1 == "*" or constraint2 == "*":
            return True
        
        # Here we can implement more complex version constraint compatibility check logic
        # For example, checking range overlaps etc.
        return False 