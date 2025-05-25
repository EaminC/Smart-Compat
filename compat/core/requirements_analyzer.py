#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Requirements.txt Compatibility Analyzer
Analyzes compatibility between multiple requirements.txt files
"""

import re
import os
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from .types import ConflictResult, ConflictType
from .hypothetical_detector import HypotheticalConflictDetector


@dataclass
class RequirementSpec:
    """Individual requirement specification"""
    name: str
    version_spec: str
    line_number: int
    raw_line: str
    file_path: str


@dataclass
class RequirementsAnalysisResult:
    """Results of requirements.txt analysis"""
    total_packages: int
    unique_packages: int
    conflicts: List[ConflictResult]
    compatible_packages: List[str]
    file1_only: List[str]
    file2_only: List[str]
    version_mismatches: List[Dict]
    dependency_conflicts: List[Dict]


class RequirementsCompatibilityAnalyzer:
    """Analyzer for requirements.txt file compatibility"""
    
    def __init__(self, enable_suggestions: bool = True):
        self.enable_suggestions = enable_suggestions
        self.detector = HypotheticalConflictDetector(
            enable_suggestions=enable_suggestions,
            hypothetical_mode=True
        )
    
    def parse_requirements_file(self, file_path: str) -> List[RequirementSpec]:
        """Parse a requirements.txt file into requirement specifications"""
        requirements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Skip git URLs, URLs, and editable installs for now
                if any(line.startswith(prefix) for prefix in ['-e', 'git+', 'http://', 'https://', 'file://']):
                    continue
                
                # Parse package specification
                requirement = self._parse_requirement_line(line, line_num, file_path)
                if requirement:
                    requirements.append(requirement)
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Requirements file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error parsing requirements file {file_path}: {e}")
        
        return requirements
    
    def _parse_requirement_line(self, line: str, line_num: int, file_path: str) -> Optional[RequirementSpec]:
        """Parse a single requirement line"""
        # Remove inline comments
        if '#' in line:
            line = line.split('#')[0].strip()
        
        if not line:
            return None
        
        # Handle various requirement formats
        # Examples: package==1.0.0, package>=1.0.0, package~=1.0.0, package
        
        # Match package[extras] (optional) with version constraints
        pattern = r'^([a-zA-Z0-9\-_.]+)(?:\[[^\]]+\])?\s*([><=!~]+.*)?$'
        match = re.match(pattern, line)
        
        if match:
            package_name = match.group(1).strip()
            version_spec = match.group(2).strip() if match.group(2) else ""
            
            return RequirementSpec(
                name=package_name,
                version_spec=version_spec,
                line_number=line_num,
                raw_line=line,
                file_path=file_path
            )
        
        return None
    
    def analyze_compatibility(self, file1_path: str, file2_path: str) -> RequirementsAnalysisResult:
        """Analyze compatibility between two requirements.txt files"""
        
        # Parse both files
        reqs1 = self.parse_requirements_file(file1_path)
        reqs2 = self.parse_requirements_file(file2_path)
        
        # Create package dictionaries for easier lookup
        packages1 = {req.name.lower(): req for req in reqs1}
        packages2 = {req.name.lower(): req for req in reqs2}
        
        # Find package overlaps and differences
        all_packages = set(packages1.keys()) | set(packages2.keys())
        common_packages = set(packages1.keys()) & set(packages2.keys())
        file1_only = set(packages1.keys()) - set(packages2.keys())
        file2_only = set(packages2.keys()) - set(packages1.keys())
        
        conflicts = []
        compatible_packages = []
        version_mismatches = []
        dependency_conflicts = []
        
        # Analyze common packages for conflicts
        for package_name in common_packages:
            req1 = packages1[package_name]
            req2 = packages2[package_name]
            
            # Check direct version conflicts
            if req1.version_spec and req2.version_spec:
                if req1.version_spec != req2.version_spec:
                    # Check if the version constraints are actually incompatible
                    is_compatible = self._check_version_constraint_compatibility(
                        req1.version_spec, req2.version_spec
                    )
                    
                    if not is_compatible:
                        # Create a synthetic conflict result for truly incompatible constraints
                        conflicts.append(ConflictResult(
                            conflict_type=ConflictType.VERSION_CONFLICT,
                            message=f"Incompatible version constraints for {package_name}: {req1.version_spec} vs {req2.version_spec}",
                            severity="high"
                        ))
                        version_mismatches.append({
                            'package': package_name,
                            'file1_spec': req1.version_spec,
                            'file2_spec': req2.version_spec,
                            'file1_line': req1.line_number,
                            'file2_line': req2.line_number,
                            'conflict_type': 'Version Constraint Incompatibility'
                        })
                    else:
                        compatible_packages.append(package_name)
                else:
                    compatible_packages.append(package_name)
            else:
                # One or both don't have version specs - generally compatible
                compatible_packages.append(package_name)
        
        # Check for cross-package dependency conflicts
        dependency_conflicts = self._check_cross_dependencies(reqs1, reqs2)
        
        return RequirementsAnalysisResult(
            total_packages=len(all_packages),
            unique_packages=len(all_packages),
            conflicts=conflicts,
            compatible_packages=compatible_packages,
            file1_only=list(file1_only),
            file2_only=list(file2_only),
            version_mismatches=version_mismatches,
            dependency_conflicts=dependency_conflicts
        )
    
    def _check_cross_dependencies(self, reqs1: List[RequirementSpec], reqs2: List[RequirementSpec]) -> List[Dict]:
        """Check for dependency conflicts between packages from different files"""
        dependency_conflicts = []
        
        # Sample a few key packages for dependency analysis to avoid too many API calls
        sample_size = min(5, len(reqs1), len(reqs2))
        
        for i, req1 in enumerate(reqs1[:sample_size]):
            for j, req2 in enumerate(reqs2[:sample_size]):
                if req1.name.lower() != req2.name.lower():
                    # Check if these two packages have dependency conflicts
                    package1_full = f"{req1.name}{req1.version_spec}" if req1.version_spec else req1.name
                    package2_full = f"{req2.name}{req2.version_spec}" if req2.version_spec else req2.name
                    
                    try:
                        conflict_result = self.detector.detect_hypothetical_conflicts(
                            package1_full, package2_full
                        )
                        
                        if conflict_result.conflict_type == ConflictType.DEPENDENCY_CONFLICT:
                            dependency_conflicts.append({
                                'package1': req1.name,
                                'package2': req2.name,
                                'file1': req1.file_path,
                                'file2': req2.file_path,
                                'conflict_reason': conflict_result.message
                            })
                    except Exception as e:
                        # Skip on errors to avoid breaking the entire analysis
                        continue
        
        return dependency_conflicts
    
    def _check_version_constraint_compatibility(self, constraint1: str, constraint2: str) -> bool:
        """Check if two version constraints are compatible"""
        try:
            from packaging.specifiers import SpecifierSet
            from packaging.version import Version
            
            spec1 = SpecifierSet(constraint1)
            spec2 = SpecifierSet(constraint2)
            
            # Generate some test versions to see if there's any overlap
            test_versions = []
            
            # Try to extract some version numbers from the constraints to test
            import re
            
            # Extract version numbers from constraints
            version_pattern = r'(\d+(?:\.\d+)*(?:\.\d+)*)'
            versions_in_constraints = []
            
            for match in re.finditer(version_pattern, constraint1 + " " + constraint2):
                try:
                    v = Version(match.group(1))
                    versions_in_constraints.append(v)
                except:
                    continue
            
            # Add some common version patterns to test
            base_versions = ['1.0.0', '1.1.0', '1.2.0', '1.3.0', '1.4.0', '1.5.0', 
                           '2.0.0', '2.1.0', '2.2.0', '3.0.0']
            
            for v_str in base_versions:
                try:
                    versions_in_constraints.append(Version(v_str))
                except:
                    continue
            
            # Test if any version satisfies both constraints
            for version in versions_in_constraints:
                if version in spec1 and version in spec2:
                    return True
            
            # If no overlap found, constraints are incompatible
            return False
            
        except Exception:
            # If we can't parse constraints, assume they're incompatible if different
            return constraint1 == constraint2
    
    def generate_compatibility_report(self, result: RequirementsAnalysisResult, 
                                    file1_path: str, file2_path: str) -> str:
        """Generate a human-readable compatibility report"""
        
        file1_name = os.path.basename(file1_path)
        file2_name = os.path.basename(file2_path)
        
        report = []
        report.append("=" * 60)
        report.append("📋 Requirements.txt Compatibility Analysis Report")
        report.append("=" * 60)
        report.append(f"File 1: {file1_name}")
        report.append(f"File 2: {file2_name}")
        report.append("")
        
        # Summary
        report.append("📊 Summary:")
        report.append(f"   • Total unique packages: {result.total_packages}")
        report.append(f"   • Compatible packages: {len(result.compatible_packages)}")
        report.append(f"   • Version conflicts: {len(result.version_mismatches)}")
        report.append(f"   • Dependency conflicts: {len(result.dependency_conflicts)}")
        report.append(f"   • Only in {file1_name}: {len(result.file1_only)}")
        report.append(f"   • Only in {file2_name}: {len(result.file2_only)}")
        report.append("")
        
        # Overall compatibility status
        if result.conflicts:
            report.append("❌ Overall Status: INCOMPATIBLE")
            report.append(f"   Found {len(result.conflicts)} critical conflicts")
        else:
            report.append("✅ Overall Status: COMPATIBLE")
            report.append("   No critical conflicts detected")
        report.append("")
        
        # Version mismatches
        if result.version_mismatches:
            report.append("⚠️ Version Conflicts:")
            for mismatch in result.version_mismatches:
                report.append(f"   • {mismatch['package']}:")
                report.append(f"     - {file1_name}: {mismatch['file1_spec']} (line {mismatch['file1_line']})")
                report.append(f"     - {file2_name}: {mismatch['file2_spec']} (line {mismatch['file2_line']})")
                report.append(f"     - Conflict type: {mismatch['conflict_type']}")
            report.append("")
        
        # Dependency conflicts
        if result.dependency_conflicts:
            report.append("🔗 Dependency Conflicts:")
            for conflict in result.dependency_conflicts:
                report.append(f"   • {conflict['package1']} ↔ {conflict['package2']}")
                report.append(f"     Reason: {conflict['conflict_reason']}")
            report.append("")
        
        # Package differences
        if result.file1_only:
            report.append(f"📦 Only in {file1_name}:")
            for pkg in sorted(result.file1_only):
                report.append(f"   • {pkg}")
            report.append("")
        
        if result.file2_only:
            report.append(f"📦 Only in {file2_name}:")
            for pkg in sorted(result.file2_only):
                report.append(f"   • {pkg}")
            report.append("")
        
        # Compatible packages
        if result.compatible_packages:
            report.append("✅ Compatible packages:")
            for pkg in sorted(result.compatible_packages):
                report.append(f"   • {pkg}")
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report) 