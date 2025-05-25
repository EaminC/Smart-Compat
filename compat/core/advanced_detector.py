#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Package Conflict Detector
Enhanced version that can detect:
1. Transitive dependency version conflicts
2. System-level dependency conflicts (CUDA, etc.)
3. Runtime environment incompatibilities
"""

import re
import json
import urllib.request
from typing import Dict, List, Optional, Tuple, Set
from .detector import PackageConflictDetector
from .types import ConflictResult, ConflictType, PackageInfo


class AdvancedConflictDetector(PackageConflictDetector):
    """Enhanced conflict detector with advanced conflict detection capabilities"""
    
    def __init__(self, enable_suggestions: bool = True):
        super().__init__(enable_suggestions)
        
        # Known system-level dependency conflicts
        self.system_conflicts = {
            'cuda_conflicts': {
                ('tensorflow', '2.8'): {'cuda_version': '11.2', 'cudnn_version': '8.1'},
                ('tensorflow', '2.9'): {'cuda_version': '11.2', 'cudnn_version': '8.1'},
                ('tensorflow', '2.10'): {'cuda_version': '11.2', 'cudnn_version': '8.1'},
                ('tensorflow', '2.11'): {'cuda_version': '11.2', 'cudnn_version': '8.1'},
                ('tensorflow', '2.12'): {'cuda_version': '11.8', 'cudnn_version': '8.6'},
                ('tensorflow', '2.13'): {'cuda_version': '11.8', 'cudnn_version': '8.6'},
                ('tensorflow', '2.14'): {'cuda_version': '11.8', 'cudnn_version': '8.7'},
                ('tensorflow', '2.15'): {'cuda_version': '12.2', 'cudnn_version': '8.9'},
                ('tensorflow', '2.16'): {'cuda_version': '12.3', 'cudnn_version': '8.9'},
                ('tensorflow', '2.17'): {'cuda_version': '12.3', 'cudnn_version': '8.9'},
                ('tensorflow', '2.18'): {'cuda_version': '12.3', 'cudnn_version': '8.9'},
                ('torch', '1.12'): {'cuda_version': '11.3', 'cudnn_version': '8.3'},
                ('torch', '1.13'): {'cuda_version': '11.6', 'cudnn_version': '8.3'},
                ('torch', '2.0'): {'cuda_version': '11.7', 'cudnn_version': '8.5'},
                ('torch', '2.1'): {'cuda_version': '11.8', 'cudnn_version': '8.7'},
                ('torch', '2.2'): {'cuda_version': '11.8', 'cudnn_version': '8.7'},
                ('torch', '2.3'): {'cuda_version': '11.8', 'cudnn_version': '8.7'},
                ('torch', '2.4'): {'cuda_version': '12.1', 'cudnn_version': '8.9'},
                ('torch', '2.5'): {'cuda_version': '12.1', 'cudnn_version': '8.9'},
                ('torch', '2.6'): {'cuda_version': '12.4', 'cudnn_version': '9.1'},
            }
        }
        
        # Known problematic version combinations
        self.known_incompatibilities = {
            ('numpy', 'scipy'): [
                {'numpy_version': '<1.23.0', 'scipy_version': '>=1.9.0', 'reason': 'SciPy 1.9.0+ requires NumPy >= 1.23.0'},
                {'numpy_version': '<1.21.0', 'scipy_version': '>=1.8.0', 'reason': 'SciPy 1.8.0+ requires NumPy >= 1.21.0'},
            ],
            ('pandas', 'numpy'): [
                {'pandas_version': '>=2.0.0', 'numpy_version': '<1.21.0', 'reason': 'Pandas 2.0+ requires NumPy >= 1.21.0'},
            ],
            ('scikit-learn', 'numpy'): [
                {'sklearn_version': '>=1.2.0', 'numpy_version': '<1.21.0', 'reason': 'Scikit-learn 1.2+ requires NumPy >= 1.21.0'},
            ]
        }
    
    def extract_major_minor_version(self, version: str) -> str:
        """Extract major.minor version from full version string"""
        match = re.match(r'(\d+\.\d+)', version)
        return match.group(1) if match else version
    
    def check_system_level_conflicts(self, pkg1_info: PackageInfo, pkg2_info: PackageInfo) -> List[Dict]:
        """Check for system-level conflicts like CUDA version mismatches"""
        conflicts = []
        
        # Check CUDA conflicts
        pkg1_cuda = self._get_cuda_requirements(pkg1_info.name, pkg1_info.version)
        pkg2_cuda = self._get_cuda_requirements(pkg2_info.name, pkg2_info.version)
        
        if pkg1_cuda and pkg2_cuda:
            if pkg1_cuda['cuda_version'] != pkg2_cuda['cuda_version']:
                conflicts.append({
                    'type': 'cuda_version_conflict',
                    'package1': pkg1_info.name,
                    'package2': pkg2_info.name,
                    'cuda1': pkg1_cuda['cuda_version'],
                    'cuda2': pkg2_cuda['cuda_version'],
                    'reason': f"{pkg1_info.name} requires CUDA {pkg1_cuda['cuda_version']}, but {pkg2_info.name} requires CUDA {pkg2_cuda['cuda_version']}"
                })
            
            if pkg1_cuda['cudnn_version'] != pkg2_cuda['cudnn_version']:
                conflicts.append({
                    'type': 'cudnn_version_conflict',
                    'package1': pkg1_info.name,
                    'package2': pkg2_info.name,
                    'cudnn1': pkg1_cuda['cudnn_version'],
                    'cudnn2': pkg2_cuda['cudnn_version'],
                    'reason': f"{pkg1_info.name} requires cuDNN {pkg1_cuda['cudnn_version']}, but {pkg2_info.name} requires cuDNN {pkg2_cuda['cudnn_version']}"
                })
        
        return conflicts
    
    def _get_cuda_requirements(self, package_name: str, version: str) -> Optional[Dict]:
        """Get CUDA requirements for a package version"""
        major_minor = self.extract_major_minor_version(version)
        
        for (pkg, ver), requirements in self.system_conflicts['cuda_conflicts'].items():
            if pkg.lower() == package_name.lower() and ver == major_minor:
                return requirements
        
        return None
    
    def check_transitive_dependency_conflicts(self, pkg1_info: PackageInfo, pkg2_info: PackageInfo) -> List[Dict]:
        """Check for transitive dependency version conflicts"""
        conflicts = []
        
        # Check known incompatibilities
        for (pkg_a, pkg_b), incompatibilities in self.known_incompatibilities.items():
            pkg1_matches_a = pkg1_info.name.lower() == pkg_a.lower()
            pkg2_matches_b = pkg2_info.name.lower() == pkg_b.lower()
            pkg1_matches_b = pkg1_info.name.lower() == pkg_b.lower()
            pkg2_matches_a = pkg2_info.name.lower() == pkg_a.lower()
            
            if (pkg1_matches_a and pkg2_matches_b) or (pkg1_matches_b and pkg2_matches_a):
                for incompatibility in incompatibilities:
                    if self._check_version_incompatibility(pkg1_info, pkg2_info, incompatibility, pkg_a, pkg_b):
                        conflicts.append({
                            'type': 'transitive_dependency_conflict',
                            'package1': pkg1_info.name,
                            'package2': pkg2_info.name,
                            'reason': incompatibility['reason'],
                            'incompatibility': incompatibility
                        })
        
        return conflicts
    
    def _check_version_incompatibility(self, pkg1_info: PackageInfo, pkg2_info: PackageInfo, 
                                     incompatibility: Dict, pkg_a: str, pkg_b: str) -> bool:
        """Check if two packages match a known incompatibility pattern"""
        try:
            # Determine which package corresponds to which role
            if pkg1_info.name.lower() == pkg_a.lower():
                pkg_a_info, pkg_b_info = pkg1_info, pkg2_info
                pkg_a_constraint = incompatibility.get(f'{pkg_a}_version', '')
                pkg_b_constraint = incompatibility.get(f'{pkg_b}_version', '')
            else:
                pkg_a_info, pkg_b_info = pkg2_info, pkg1_info
                pkg_a_constraint = incompatibility.get(f'{pkg_a}_version', '')
                pkg_b_constraint = incompatibility.get(f'{pkg_b}_version', '')
            
            # Check if versions match the problematic pattern
            a_matches = self._version_matches_constraint(pkg_a_info.version, pkg_a_constraint)
            b_matches = self._version_matches_constraint(pkg_b_info.version, pkg_b_constraint)
            
            return a_matches and b_matches
            
        except Exception as e:
            print(f"Warning: Error checking incompatibility: {e}")
            return False
    
    def _version_matches_constraint(self, version: str, constraint: str) -> bool:
        """Check if a version matches a constraint like '>=1.23.0' or '<1.21.0'"""
        if not constraint:
            return True
            
        try:
            # Parse constraint
            constraint = constraint.strip()
            
            if constraint.startswith('>='):
                min_version = constraint[2:].strip()
                return self.compare_versions(version, min_version) >= 0
            elif constraint.startswith('<='):
                max_version = constraint[2:].strip()
                return self.compare_versions(version, max_version) <= 0
            elif constraint.startswith('>'):
                min_version = constraint[1:].strip()
                return self.compare_versions(version, min_version) > 0
            elif constraint.startswith('<'):
                max_version = constraint[1:].strip()
                return self.compare_versions(version, max_version) < 0
            elif constraint.startswith('=='):
                exact_version = constraint[2:].strip()
                return version == exact_version
            else:
                # Assume exact match
                return version == constraint
                
        except Exception:
            return False
    
    def detect_advanced_conflicts(self, package1: str, package2: str) -> ConflictResult:
        """Enhanced conflict detection with advanced capabilities"""
        
        # First run standard conflict detection
        standard_result = super().detect_conflicts(package1, package2)
        
        # If standard detection found conflicts, return as is
        if standard_result.conflict_type != ConflictType.NO_CONFLICT:
            return standard_result
        
        # Parse package specifications for advanced analysis
        pkg1_name, pkg1_version_spec = self.parse_package_spec(package1)
        pkg2_name, pkg2_version_spec = self.parse_package_spec(package2)
        
        # Get package information
        pkg1_info = self.get_package_info_from_pip(pkg1_name)
        pkg2_info = self.get_package_info_from_pip(pkg2_name)
        
        if not pkg1_info or not pkg2_info:
            return standard_result  # Let standard detector handle missing packages
        
        # Check for advanced conflicts
        system_conflicts = self.check_system_level_conflicts(pkg1_info, pkg2_info)
        transitive_conflicts = self.check_transitive_dependency_conflicts(pkg1_info, pkg2_info)
        
        all_advanced_conflicts = system_conflicts + transitive_conflicts
        
        if all_advanced_conflicts:
            # Format conflict messages
            conflict_messages = []
            for conflict in all_advanced_conflicts:
                conflict_messages.append(conflict['reason'])
            
            # Determine conflict type and severity
            if any(c['type'] in ['cuda_version_conflict', 'cudnn_version_conflict'] for c in all_advanced_conflicts):
                conflict_type = ConflictType.DEPENDENCY_CONFLICT
                severity = "high"
                message_prefix = "System-level conflicts detected"
            else:
                conflict_type = ConflictType.DEPENDENCY_CONFLICT
                severity = "high"
                message_prefix = "Dependency version conflicts detected"
            
            full_message = f"{message_prefix}:\n" + "\n".join(f"• {msg}" for msg in conflict_messages)
            
            return ConflictResult(
                conflict_type=conflict_type,
                message=full_message,
                severity=severity,
                details={
                    "advanced_conflicts": all_advanced_conflicts,
                    "pkg1": pkg1_info.__dict__,
                    "pkg2": pkg2_info.__dict__
                }
            )
        
        return standard_result 