#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Package Conflict Detection CLI
Unified command-line tool for package conflict detection
"""

import argparse
import sys
import os

# Add path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compat.detectors.basic import PackageConflictDetector
from compat.detectors.hypothetical import HypotheticalConflictDetector
from compat.core.types import ConflictType, ConflictResult
from compat.detectors.enhanced import EnhancedConflictDetector
from compat.analyzers.requirements_analyzer import RequirementsCompatibilityAnalyzer


def format_conflict_result(result, verbose=False, mode="basic"):
    """Format conflict detection results"""
    
    # Select icon based on conflict type and severity
    if result.conflict_type == ConflictType.NO_CONFLICT:
        severity_icon = "✅"
    elif result.conflict_type == ConflictType.PACKAGE_NOT_FOUND:
        severity_icon = "🔍" if result.severity == "info" else "❓"
    elif result.severity == "high":
        severity_icon = "❌"
    elif result.severity == "medium":
        severity_icon = "⚠️"
    else:
        severity_icon = "ℹ️"
    
    # Display mode information
    mode_displays = {
        "check": "🔮 Hypothetical Mode: Hypothetical compatibility detection",
        "enhanced": "🚀 Enhanced Mode: Pip-integrated enhanced conflict detection"
    }
    
    if mode in mode_displays:
        print(mode_displays[mode])
        print("=" * 50)
    
    # Display basic results
    print(f"{severity_icon} Conflict Type: {result.conflict_type.value}")
    print(f"Severity: {result.severity}")
    print(f"Result: {result.message}")
    
    # Display enhanced detection details
    if verbose and result.details and result.details.get('enhanced_detection'):
        detection_methods = result.details.get('detection_methods', [])
        if detection_methods:
            print(f"\n🔧 Detection Methods Used:")
            method_names = {
                'hypothetical': 'PyPI-based hypothetical analysis',
                'system_level': 'System-level dependency analysis',
                'transitive': 'Transitive dependency analysis',
                'pip_simulation': 'Pip dependency resolver simulation',
                'version_constraint_analysis': 'Advanced version constraint analysis'
            }
            for method in detection_methods:
                method_display = method_names.get(method, method)
                print(f"   • {method_display}")
        
        # Display pip confirmation
        if result.details.get('pip_confirmation'):
            print(f"\n✅ {result.details['pip_confirmation']}")
    
    # Display package information
    if verbose and result.details:
        if 'pkg1' in result.details and 'pkg2' in result.details:
            pkg1 = result.details['pkg1']
            pkg2 = result.details['pkg2']
            
            print(f"\n📦 Package Information:")
            print(f"   • {pkg1['name']} v{pkg1['version']}")
            if pkg1.get('description'):
                print(f"     └─ {pkg1['description']}")
            
            print(f"   • {pkg2['name']} v{pkg2['version']}")
            if pkg2.get('description'):
                print(f"     └─ {pkg2['description']}")
    
    # Display package name suggestions
    if result.details and "suggestions" in result.details:
        suggestions = result.details["suggestions"]
        if any(suggestions.values()):
            print(f"\n💡 Suggestions:")
            
            if suggestions.get('typo_corrections'):
                print("   🔤 Possible typo corrections:")
                for correction in suggestions['typo_corrections']:
                    print(f"      • {correction}")
            
            if suggestions.get('similar_packages'):
                print("   📦 Similar package names:")
                for pkg in suggestions['similar_packages'][:3]:
                    print(f"      • {pkg['name']} (similarity: {pkg['similarity']})")
    
    # Display version suggestions for version conflicts
    if result.details and "version_check" in result.details:
        version_info = result.details["version_check"]
        if version_info.get('suggested_versions'):
            print(f"\n🎯 Similar versions:")
            for version in version_info['suggested_versions'][:5]:
                print(f"   • {version}")
        
        if version_info.get('latest_version'):
            print(f"\n🆕 Latest version: {version_info['latest_version']}")
        
        if version_info.get('recent_versions'):
            print(f"\n📋 Recent versions:")
            for version in version_info['recent_versions'][:4]:
                print(f"   • {version}")


def cmd_simple(args):
    """Simple mode - only returns yes/no"""
    # Use the same detector as check mode to ensure consistency
    detector = HypotheticalConflictDetector(
        enable_suggestions=False,
        hypothetical_mode=True
    )
    result = detector.detect_hypothetical_conflicts(args.package1, args.package2)
    
    if result.conflict_type == ConflictType.NO_CONFLICT:
        print("YES")
        return result
    else:
        print("NO")
        return result


def cmd_enhanced(args):
    """Enhanced conflict detection command"""
    detector = EnhancedConflictDetector(
        enable_suggestions=not args.no_suggestions,
        use_pip_resolver=not args.disable_pip
    )
    result = detector.detect_enhanced_conflicts(args.package1, args.package2)
    format_conflict_result(result, verbose=args.verbose, mode="enhanced")
    return result


def cmd_check(args):
    """Hypothetical conflict detection command"""
    detector = HypotheticalConflictDetector(
        enable_suggestions=not args.no_suggestions,
        hypothetical_mode=True
    )
    result = detector.detect_hypothetical_conflicts(args.package1, args.package2)
    format_conflict_result(result, verbose=args.verbose, mode="check")
    return result


def cmd_requirements(args):
    """Requirements.txt compatibility analysis command"""
    analyzer = RequirementsCompatibilityAnalyzer(enable_suggestions=not args.no_suggestions)
    
    try:
        result = analyzer.analyze_compatibility(args.file1, args.file2)
        
        if args.output:
            # Save report to file
            report = analyzer.generate_compatibility_report(result, args.file1, args.file2)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Compatibility report saved to: {args.output}")
        else:
            # Print report to console
            report = analyzer.generate_compatibility_report(result, args.file1, args.file2)
            print(report)
        
        # Return appropriate exit code
        if result.conflicts:
            return ConflictResult(
                conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                message=f"Found {len(result.conflicts)} compatibility issues",
                severity="high"
            )
        else:
            return ConflictResult(
                conflict_type=ConflictType.NO_CONFLICT,
                message="Requirements files are compatible",
                severity="low"
            )
    
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return ConflictResult(
            conflict_type=ConflictType.PACKAGE_NOT_FOUND,
            message=str(e),
            severity="high"
        )
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return ConflictResult(
            conflict_type=ConflictType.DEPENDENCY_CONFLICT,
            message=str(e),
            severity="high"
        )


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Package Conflict Detection Tool - Simplified Python package conflict detection",
        epilog="Use 'compat-cli.py <command> --help' for more information on a command.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument('--version', action='version', version='%(prog)s 2.0.0')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # requirements command
    req_parser = subparsers.add_parser('requirements', help='Analyze compatibility between two requirements.txt files')
    req_parser.add_argument('file1', help='First requirements.txt file path')
    req_parser.add_argument('file2', help='Second requirements.txt file path')
    req_parser.add_argument('--no-suggestions', action='store_true', help='Disable package name suggestions')
    req_parser.add_argument('--output', '-o', help='Save report to output file')
    req_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    req_parser.set_defaults(func=cmd_requirements)
    
    # enhanced command (recommended)
    enhanced_parser = subparsers.add_parser('enhanced', help='Enhanced conflict detection (pip integration, recommended)')
    enhanced_parser.add_argument('package1', help='First package specification')
    enhanced_parser.add_argument('package2', help='Second package specification')
    enhanced_parser.add_argument('--no-suggestions', action='store_true', help='Disable package name suggestions')
    enhanced_parser.add_argument('--disable-pip', action='store_true', help='Disable pip resolver')
    enhanced_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    enhanced_parser.set_defaults(func=cmd_enhanced)
    
    # check command (default)
    check_parser = subparsers.add_parser('check', help='Hypothetical compatibility detection (default mode)')
    check_parser.add_argument('package1', help='First package specification')
    check_parser.add_argument('package2', help='Second package specification')
    check_parser.add_argument('--no-suggestions', action='store_true', help='Disable package name suggestions')
    check_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    check_parser.set_defaults(func=cmd_check)
    
    # simple command (minimal output)
    simple_parser = subparsers.add_parser('simple', help='Simple yes/no compatibility check')
    simple_parser.add_argument('package1', help='First package specification')
    simple_parser.add_argument('package2', help='Second package specification')
    simple_parser.set_defaults(func=cmd_simple)
    
    # If no subcommand, default to check
    if len(sys.argv) >= 3 and not sys.argv[1].startswith('-') and sys.argv[1] not in ['requirements', 'enhanced', 'check', 'simple']:
        # User directly entered package names, use default check mode
        sys.argv.insert(1, 'check')
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    try:
        result = args.func(args)
        
        # Set exit code based on result
        if result.conflict_type == ConflictType.NO_CONFLICT:
            sys.exit(0)
        elif result.severity in ["high", "critical"]:
            sys.exit(2)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 