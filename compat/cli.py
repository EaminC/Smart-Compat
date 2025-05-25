#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command Line Interface Module
"""

import json
import argparse
from typing import Optional

from .core.universal_detector import UniversalPackageConflictDetector
from .core.detector import PackageConflictDetector
from .core.types import PackageManager


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Package Conflict Detection Tool - Detect conflicts between two packages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s requests urllib3                    # Detect Python packages
  %(prog)s -m npm react vue                    # Detect npm packages
  %(prog)s -v requests urllib3                 # Show detailed information
  %(prog)s --json requests urllib3             # JSON format output
  %(prog)s --no-suggestions reqests urllib3    # Disable package name suggestions
        """
    )
    
    parser.add_argument('package1', help='First package name')
    parser.add_argument('package2', help='Second package name')
    
    parser.add_argument(
        '--manager', '-m',
        choices=['pip', 'npm', 'yarn'],
        help='Specify package manager (default: auto detect)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--no-suggestions',
        action='store_true',
        help='Disable package name suggestions for non-existent packages'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.1.0'
    )
    
    return parser


def format_output(result, verbose: bool = False, json_format: bool = False) -> str:
    """Format output results"""
    if json_format:
        output = {
            "conflict_type": result.conflict_type.value,
            "message": result.message,
            "severity": result.severity,
            "details": result.details
        }
        return json.dumps(output, ensure_ascii=False, indent=2)
    
    else:
        # Show different icons based on severity
        severity_icons = {
            "info": "ℹ️",
            "low": "ℹ️",
            "warning": "⚠️",
            "medium": "⚠️",
            "high": "❌",
            "critical": "🚨"
        }
        
        # Special handling for package not found
        if result.conflict_type.value == "Package Not Found":
            if result.severity == "info":
                icon = "🔍"  # Search icon when suggestions are available
            else:
                icon = "❓"  # Question mark when no suggestions
        else:
            icon = severity_icons.get(result.severity, "ℹ️")
        
        output_lines = [
            f"{icon} Conflict Type: {result.conflict_type.value}",
            f"Severity: {result.severity}",
            f"Result: {result.message}"
        ]
        
        if verbose and result.details:
            output_lines.append("\nDetailed Information:")
            
            # Show version check information
            if "version_check" in result.details:
                version_info = result.details["version_check"]
                output_lines.append("\n📋 Version Information:")
                
                if not version_info.get('version_exists', True):
                    output_lines.append("  ❌ Requested version does not exist")
                
                if version_info.get('suggested_versions'):
                    output_lines.append("  🔍 Available versions:")
                    for v in version_info['suggested_versions']:
                        output_lines.append(f"     • {v}")
                
                if version_info.get('latest_version'):
                    output_lines.append(f"  🆕 Latest version: {version_info['latest_version']}")
            
            # Show suggestions if available
            if "suggestions" in result.details:
                suggestions = result.details["suggestions"]
                if any(suggestions.values()):
                    output_lines.append("\n📝 Package Suggestions:")
                    
                    if suggestions.get('typo_corrections'):
                        output_lines.append("  🔤 Possible typo corrections:")
                        for correction in suggestions['typo_corrections']:
                            output_lines.append(f"     • {correction}")
                    
                    if suggestions.get('similar_packages'):
                        output_lines.append("  📦 Similar package names:")
                        for pkg in suggestions['similar_packages']:
                            output_lines.append(f"     • {pkg['name']} (similarity: {pkg['similarity']})")
                    
                    if suggestions.get('pypi_search'):
                        output_lines.append("  🔍 PyPI search results:")
                        for pkg in suggestions['pypi_search']:
                            summary = pkg.get('summary', 'No description')
                            if len(summary) > 50:
                                summary = summary[:47] + "..."
                            output_lines.append(f"     • {pkg['name']} - {summary}")
            
            if "conflicts" in result.details:
                output_lines.append("Dependency Conflicts:")
                for conflict in result.details["conflicts"]:
                    output_lines.append(f"  - {conflict}")
            
            if "peer_conflicts" in result.details:
                output_lines.append("Peer Dependency Conflicts:")
                for conflict in result.details["peer_conflicts"]:
                    output_lines.append(f"  - {conflict}")
            
            if "pkg1" in result.details:
                pkg1 = result.details["pkg1"]
                output_lines.append(f"\nPackage 1 Info: {pkg1['name']} v{pkg1['version']}")
                if pkg1.get('dependencies'):
                    deps = pkg1['dependencies']
                    if isinstance(deps, dict):
                        deps_str = ', '.join([f"{k}({v})" for k, v in deps.items()])
                    else:
                        deps_str = ', '.join(deps)
                    output_lines.append(f"  Dependencies: {deps_str}")
            
            if "pkg2" in result.details:
                pkg2 = result.details["pkg2"]
                output_lines.append(f"\nPackage 2 Info: {pkg2['name']} v{pkg2['version']}")
                if pkg2.get('dependencies'):
                    deps = pkg2['dependencies']
                    if isinstance(deps, dict):
                        deps_str = ', '.join([f"{k}({v})" for k, v in deps.items()])
                    else:
                        deps_str = ', '.join(deps)
                    output_lines.append(f"  Dependencies: {deps_str}")
        
        return '\n'.join(output_lines)


def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Determine if suggestions should be enabled
        enable_suggestions = not args.no_suggestions
        
        # Create detector
        if args.manager:
            detector = UniversalPackageConflictDetector()
            pm = PackageManager(args.manager)
            if args.verbose:
                print(f"Using specified package manager: {pm.value}")
        else:
            # Use pip detector for better suggestion support
            detector = PackageConflictDetector(enable_suggestions=enable_suggestions)
            if args.verbose:
                print(f"Auto-detected package manager: pip")
                if enable_suggestions:
                    print("📝 Package name suggestions: enabled")
                else:
                    print("📝 Package name suggestions: disabled")
        
        # Detect conflicts
        if hasattr(detector, 'detect_conflicts'):
            if isinstance(detector, PackageConflictDetector):
                result = detector.detect_conflicts(args.package1, args.package2)
            else:
                pm = PackageManager(args.manager) if args.manager else detector.detect_package_manager()
                result = detector.detect_conflicts(args.package1, args.package2, pm)
        else:
            raise AttributeError("Detector does not have detect_conflicts method")
        
        # Output results
        output = format_output(result, args.verbose, args.json)
        print(output)
        
    except KeyboardInterrupt:
        print("\nDetection interrupted by user")
        return 1
    except Exception as e:
        print(f"Error occurred during detection: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main()) 