#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Package Conflict Detector
Core functionality for detecting package conflicts
"""

import re
import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Tuple, Set

from ..utils.suggestions import PackageNameSuggester
from ..core.types import ConflictResult, ConflictType, PackageInfo


class PackageConflictDetector:
    """Python pip package conflict detector"""
    
    def __init__(self, enable_suggestions: bool = True):
        self.version_pattern = re.compile(r'^(\d+)\.(\d+)\.(\d+).*$')
        self.enable_suggestions = enable_suggestions
        if enable_suggestions:
            self.suggester = PackageNameSuggester()
    
    def parse_package_spec(self, package_spec: str) -> Tuple[str, Optional[str]]:
        """Parse package specification into name and version"""
        if '==' in package_spec:
            name, version = package_spec.split('==', 1)
            return name.strip(), f"=={version.strip()}"
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
    
    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version number to tuple format"""
        # Clean version string
        version = re.sub(r'[^\d\.].*', '', version)
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
        """
        Compare two version numbers
        Return value: -1 (version1 < version2), 0 (equal), 1 (version1 > version2)
        """
        try:
            v1 = self.parse_version(version1)
            v2 = self.parse_version(version2)
            
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
        except ValueError as e:
            print(f"Version comparison error: {e}")
            return 0
    
    def check_version_compatibility(self, installed_version: str, required_spec: str) -> bool:
        """Check if installed version satisfies the required specification"""
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
            elif required_spec.startswith("=="):
                req_version = required_spec[2:]
                return self.compare_versions(installed_version, req_version) == 0
            else:
                # Exact match
                return self.compare_versions(installed_version, required_spec) == 0
        except Exception:
            return False
    
    def get_package_info_from_pip(self, package_name: str, version_spec: str = None) -> Optional[PackageInfo]:
        """Get package information from pip"""
        try:
            # Use pip show command to get package information
            result = subprocess.run(
                ['pip', 'show', package_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            info = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            dependencies = {}
            if 'Requires' in info and info['Requires']:
                for dep in info['Requires'].split(','):
                    dep = dep.strip()
                    if '==' in dep:
                        name, version = dep.split('==', 1)
                        dependencies[name] = f"=={version}"
                    else:
                        dependencies[dep] = "*"
            
            package_info = PackageInfo(
                name=info.get('Name', package_name),
                version=info.get('Version', ''),
                dependencies=dependencies,
                author=info.get('Author', ''),
                description=info.get('Summary', ''),
                license=info.get('License', ''),
                homepage=info.get('Home-page', '')
            )
            
            return package_info
            
        except subprocess.CalledProcessError:
            return None
    
    def check_package_version_compatibility(self, package_info: PackageInfo, version_spec: str) -> bool:
        """Check if package version satisfies the version specification"""
        if not version_spec:
            return True
        
        return self.check_version_compatibility(package_info.version, version_spec)
    
    def check_dependency_conflicts(self, pkg1: PackageInfo, pkg2: PackageInfo) -> List[str]:
        """Check dependency conflicts"""
        conflicts = []
        
        # Check if there are same dependencies but different versions
        deps1 = {dep.split('==')[0] if '==' in dep else dep: dep for dep in pkg1.dependencies}
        deps2 = {dep.split('==')[0] if '==' in dep else dep: dep for dep in pkg2.dependencies}
        
        common_deps = set(deps1.keys()) & set(deps2.keys())
        
        for dep in common_deps:
            dep1_full = deps1[dep]
            dep2_full = deps2[dep]
            
            if dep1_full != dep2_full:
                conflicts.append(f"Dependency {dep}: {pkg1.name} requires {dep1_full}, {pkg2.name} requires {dep2_full}")
        
        return conflicts
    
    def _generate_package_not_found_result(self, package_name: str, version_spec: str = None) -> ConflictResult:
        """Generate enhanced result for package not found with suggestions"""
        base_message = f"Cannot find package: {package_name}"
        details = {"error": f"Package {package_name} not found"}
        
        # Add suggestions if enabled
        if self.enable_suggestions:
            try:
                suggestions = self.suggester.generate_suggestions(package_name)
                if any(suggestions.values()):
                    suggestions_text = self.suggester.format_suggestions_text(package_name, suggestions)
                    base_message += f"\n\n{suggestions_text}"
                    details["suggestions"] = suggestions
            except Exception as e:
                print(f"Warning: Failed to generate suggestions: {e}")
        
        if version_spec:
            # For version-specific cases, we need to check if it's a version issue or package issue
            # Try to get package info without version constraint first
            try:
                result = subprocess.run(
                    ['pip', 'show', package_name],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Package exists, so it's a version mismatch
                lines = result.stdout.strip().split('\n')
                installed_version = None
                for line in lines:
                    if line.startswith('Version:'):
                        installed_version = line.split(':', 1)[1].strip()
                        break
                
                if installed_version:
                    return self._generate_version_mismatch_result(package_name, installed_version, version_spec)
                
            except subprocess.CalledProcessError:
                # Package doesn't exist at all
                pass
            
            return ConflictResult(
                conflict_type=ConflictType.PACKAGE_NOT_FOUND,
                message=f"Package not found: {package_name} (required version: {version_spec})",
                severity="warning",
                details=details
            )
        else:
            # Use the new PACKAGE_NOT_FOUND type instead of NO_CONFLICT
            severity = "info" if any(details.get("suggestions", {}).values()) else "warning"
            return ConflictResult(
                conflict_type=ConflictType.PACKAGE_NOT_FOUND,
                message=base_message,
                severity=severity,
                details=details
            )
    
    def _generate_version_mismatch_result(self, package_name: str, installed_version: str, required_spec: str) -> ConflictResult:
        """Generate enhanced result for version mismatch with version existence check"""
        base_message = f"Version mismatch: {package_name} v{installed_version} doesn't satisfy {required_spec}"
        details = {
            "package": package_name,
            "installed_version": installed_version,
            "required": required_spec
        }
        
        # Extract the version number from the spec
        version_number = required_spec
        operator = None
        
        # Check for version operators
        for op in ['>=', '<=', '==', '>', '<']:
            if required_spec.startswith(op):
                operator = op
                version_number = required_spec[len(op):]
                break
        
        # Check if the required version exists (only for exact version specs)
        if self.enable_suggestions and operator == '==':
            try:
                version_info = self.suggester.generate_version_suggestions(package_name, version_number)
                
                if not version_info.get('version_exists', True):
                    base_message = f"Version not found: {package_name} v{version_number} does not exist"
                    
                    if version_info.get('suggested_versions'):
                        suggestions_text = f"\n\n📋 Available versions:\n"
                        for v in version_info['suggested_versions']:
                            suggestions_text += f"   • {v}\n"
                        
                        if version_info.get('latest_version'):
                            suggestions_text += f"\n🆕 Latest version: {version_info['latest_version']}"
                        
                        base_message += suggestions_text
                    
                    details["version_check"] = version_info
                    return ConflictResult(
                        conflict_type=ConflictType.VERSION_CONFLICT,
                        message=base_message,
                        severity="high",  # Higher severity for non-existent versions
                        details=details
                    )
                
            except Exception as e:
                print(f"Warning: Failed to check version existence: {e}")
        
        return ConflictResult(
            conflict_type=ConflictType.VERSION_CONFLICT,
            message=base_message,
            severity="medium",
            details=details
        )
    
    def detect_conflicts(self, package1: str, package2: str) -> ConflictResult:
        """
        Detect conflicts between two packages
        
        Args:
            package1: First package name or package specification (e.g., "requests==2.28.0")
            package2: Second package name or package specification
            
        Returns:
            ConflictResult: Conflict detection result
        """
        
        # Parse package specifications
        pkg1_name, pkg1_version_spec = self.parse_package_spec(package1)
        pkg2_name, pkg2_version_spec = self.parse_package_spec(package2)
        
        # 1. Check name conflicts
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
        
        # 2. Get package information
        pkg1_info = self.get_package_info_from_pip(pkg1_name)
        pkg2_info = self.get_package_info_from_pip(pkg2_name)
        
        # Handle package not found cases
        if not pkg1_info:
            return self._generate_package_not_found_result(pkg1_name, pkg1_version_spec)
        
        if not pkg2_info:
            return self._generate_package_not_found_result(pkg2_name, pkg2_version_spec)
        
        # Check version compatibility for packages that exist
        if pkg1_version_spec and not self.check_package_version_compatibility(pkg1_info, pkg1_version_spec):
            return self._generate_version_mismatch_result(pkg1_name, pkg1_info.version, pkg1_version_spec)
        
        if pkg2_version_spec and not self.check_package_version_compatibility(pkg2_info, pkg2_version_spec):
            return self._generate_version_mismatch_result(pkg2_name, pkg2_info.version, pkg2_version_spec)
        
        # 3. Check dependency conflicts
        dependency_conflicts = self.check_dependency_conflicts(pkg1_info, pkg2_info)
        
        if dependency_conflicts:
            severity = "high" if len(dependency_conflicts) > 3 else "medium"
            return ConflictResult(
                conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                message=f"Dependency conflicts: {pkg1_name} and {pkg2_name} have {len(dependency_conflicts)} dependency conflicts",
                severity=severity,
                details={
                    "conflicts": dependency_conflicts,
                    "pkg1": pkg1_info.__dict__,
                    "pkg2": pkg2_info.__dict__
                }
            )
        
        # 4. If no conflicts found
        return ConflictResult(
            conflict_type=ConflictType.NO_CONFLICT,
            message=f"No conflicts found: {pkg1_name} v{pkg1_info.version} and {pkg2_name} v{pkg2_info.version} can coexist",
            severity="low",
            details={
                "pkg1": pkg1_info.__dict__,
                "pkg2": pkg2_info.__dict__
            }
        )
    
    def analyze_package_ecosystem(self, packages: List[str]) -> Dict:
        """Analyze conflicts in the entire package ecosystem"""
        results = {}
        
        for i, pkg1 in enumerate(packages):
            for pkg2 in packages[i+1:]:
                conflict_result = self.detect_conflicts(pkg1, pkg2)
                key = f"{pkg1} vs {pkg2}"
                results[key] = {
                    "conflict_type": conflict_result.conflict_type.value,
                    "message": conflict_result.message,
                    "severity": conflict_result.severity,
                    "has_conflict": conflict_result.conflict_type != ConflictType.NO_CONFLICT
                }
        
        return results 