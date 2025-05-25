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

from compat.core.detector import PackageConflictDetector
from compat.core.advanced_detector import AdvancedConflictDetector
from compat.core.hypothetical_detector import HypotheticalConflictDetector
from compat.core.types import ConflictType, ConflictResult
from compat.core.enhanced_detector import EnhancedConflictDetector
from compat.core.requirements_analyzer import RequirementsCompatibilityAnalyzer


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
        "basic": "📦 Basic Mode: Basic conflict detection",
        "advanced": "🔬 Advanced Mode: Advanced conflict detection",
        "hypothetical": "🔮 Hypothetical Mode: Hypothetical compatibility detection",
        "enhanced": "🚀 Enhanced Mode: Pip-integrated enhanced conflict detection"
    }
    
    if mode != "basic":
        print(mode_displays.get(mode, mode))
        print("=" * 50)
    
    # Display basic results
    print(f"{severity_icon} Conflict Type: {result.conflict_type.value}")
    print(f"Severity: {result.severity}")
    print(f"Result: {result.message}")
    
    # Display advanced conflict details
    if verbose and result.details and "advanced_conflicts" in result.details:
        advanced_conflicts = result.details["advanced_conflicts"]
        
        print(f"\n🔍 Advanced Conflict Analysis:")
        for i, conflict in enumerate(advanced_conflicts, 1):
            conflict_type = conflict.get('type', 'unknown')
            
            if conflict_type in ['cuda_version_conflict', 'cudnn_version_conflict']:
                print(f"   {i}. 🖥️ System Dependency: {conflict['reason']}")
                if conflict_type == 'cuda_version_conflict':
                    print(f"      • {conflict['package1']}: CUDA {conflict['cuda1']}")
                    print(f"      • {conflict['package2']}: CUDA {conflict['cuda2']}")
                else:
                    print(f"      • {conflict['package1']}: cuDNN {conflict['cudnn1']}")
                    print(f"      • {conflict['package2']}: cuDNN {conflict['cudnn2']}")
            
            elif conflict_type == 'transitive_dependency_conflict':
                print(f"   {i}. 🔗 Version Compatibility: {conflict['reason']}")
                print(f"      • Affected packages: {conflict['package1']}, {conflict['package2']}")
    
    # Display dependency conflict details
    if verbose and result.details and "conflicts" in result.details:
        conflicts = result.details["conflicts"]
        if conflicts:
            print(f"\n🔗 Dependency Conflicts:")
            for i, conflict in enumerate(conflicts, 1):
                print(f"   {i}. {conflict}")
    
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
    
    # Display version constraint explanations
    if verbose and result.details and "constraint_analysis" in result.details:
        constraint_analysis = result.details["constraint_analysis"]
        constraint_details = constraint_analysis.get('constraint_details', {})
        
        if constraint_details.get('pkg1_explanation'):
            pkg1_explain = constraint_details['pkg1_explanation']
            if pkg1_explain.get('valid'):
                print(f"\n📋 Version Constraints:")
                print(f"   Package 1: {pkg1_explain.get('human_readable', 'N/A')}")
        
        if constraint_details.get('pkg2_explanation'):
            pkg2_explain = constraint_details['pkg2_explanation']
            if pkg2_explain.get('valid'):
                if not constraint_details.get('pkg1_explanation'):
                    print(f"\n📋 Version Constraints:")
                print(f"   Package 2: {pkg2_explain.get('human_readable', 'N/A')}")
    
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
    
    # Display version suggestions
    if result.details and "version_check" in result.details:
        version_check = result.details["version_check"]
        
        # Display similar versions
        if version_check.get('similar_versions'):
            print(f"\n🎯 Similar versions:")
            for v in version_check['similar_versions'][:5]:
                print(f"   • {v}")
        
        # Display latest version
        if version_check.get('latest_version'):
            print(f"\n🆕 Latest version: {version_check['latest_version']}")
        
        # Display other available versions (if sufficient)
        if version_check.get('recent_versions'):
            recent = version_check['recent_versions']
            # Filter out already displayed versions
            similar = version_check.get('similar_versions', [])
            latest = version_check.get('latest_version', '')
            
            unique_recent = [v for v in recent if v not in similar and v != latest]
            
            if unique_recent:
                print(f"\n📋 Recent versions:")
                for v in unique_recent[:5]:
                    print(f"   • {v}")
    
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


def cmd_basic(args):
    """Basic conflict detection command"""
    detector = PackageConflictDetector(enable_suggestions=not args.no_suggestions)
    result = detector.detect_conflicts(args.package1, args.package2)
    format_conflict_result(result, verbose=args.verbose, mode="basic")
    return result


def cmd_advanced(args):
    """Advanced conflict detection command"""
    detector = AdvancedConflictDetector(enable_suggestions=not args.no_suggestions)
    result = detector.detect_advanced_conflicts(args.package1, args.package2)
    format_conflict_result(result, verbose=args.verbose, mode="advanced")
    return result


def cmd_hypothetical(args):
    """Hypothetical conflict detection command"""
    detector = HypotheticalConflictDetector(
        enable_suggestions=not args.no_suggestions,
        hypothetical_mode=True
    )
    result = detector.detect_hypothetical_conflicts(args.package1, args.package2)
    format_conflict_result(result, verbose=args.verbose, mode="hypothetical")
    return result


def cmd_enhanced(args):
    """Enhanced conflict detection command (pip integration)"""
    detector = EnhancedConflictDetector(
        enable_suggestions=not args.no_suggestions,
        use_pip_resolver=not args.disable_pip
    )
    result = detector.detect_enhanced_conflicts(args.package1, args.package2)
    format_conflict_result(result, verbose=args.verbose, mode="enhanced")
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


def cmd_test(args):
    """Run test suite"""
    print("🧪 Running Package Conflict Detection Tests")
    print("=" * 50)
    
    # Import test module
    try:
        from tests.test_suite import run_all_tests
        run_all_tests(verbose=args.verbose)
        return None
    except ImportError:
        print("❌ Test suite not found. Please run tests manually.")
        return None


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Package Conflict Detection Tool - Advanced Python package conflict detection",
        epilog="Use 'compat-cli.py <command> --help' for more information on a command.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # basic command
    basic_parser = subparsers.add_parser('basic', help='Basic conflict detection')
    basic_parser.add_argument('package1', help='First package specification')
    basic_parser.add_argument('package2', help='Second package specification')
    basic_parser.add_argument('--no-suggestions', action='store_true', help='Disable package name suggestions')
    basic_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    basic_parser.set_defaults(func=cmd_basic)
    
    # advanced command
    advanced_parser = subparsers.add_parser('advanced', help='Advanced conflict detection (includes system-level dependency analysis)')
    advanced_parser.add_argument('package1', help='First package specification')
    advanced_parser.add_argument('package2', help='Second package specification')
    advanced_parser.add_argument('--no-suggestions', action='store_true', help='Disable package name suggestions')
    advanced_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    advanced_parser.set_defaults(func=cmd_advanced)
    
    # hypothetical command (default)
    hypo_parser = subparsers.add_parser('check', help='Hypothetical compatibility detection (recommended, default mode)')
    hypo_parser.add_argument('package1', help='First package specification')
    hypo_parser.add_argument('package2', help='Second package specification')
    hypo_parser.add_argument('--no-suggestions', action='store_true', help='Disable package name suggestions')
    hypo_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    hypo_parser.set_defaults(func=cmd_hypothetical)
    
    # enhanced command (recommended)
    enhanced_parser = subparsers.add_parser('enhanced', help='Enhanced conflict detection (pip integration, recommended)')
    enhanced_parser.add_argument('package1', help='First package specification')
    enhanced_parser.add_argument('package2', help='Second package specification')
    enhanced_parser.add_argument('--no-suggestions', action='store_true', help='Disable package name suggestions')
    enhanced_parser.add_argument('--disable-pip', action='store_true', help='Disable pip resolver')
    enhanced_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    enhanced_parser.set_defaults(func=cmd_enhanced)
    
    # requirements command
    req_parser = subparsers.add_parser('requirements', help='Analyze compatibility between two requirements.txt files')
    req_parser.add_argument('file1', help='First requirements.txt file path')
    req_parser.add_argument('file2', help='Second requirements.txt file path')
    req_parser.add_argument('--no-suggestions', action='store_true', help='Disable package name suggestions')
    req_parser.add_argument('--output', '-o', help='Save report to output file')
    req_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    req_parser.set_defaults(func=cmd_requirements)
    
    # test command
    test_parser = subparsers.add_parser('test', help='Run test suite')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    test_parser.set_defaults(func=cmd_test)
    
    # If no subcommand, default to check
    if len(sys.argv) >= 3 and not sys.argv[1].startswith('-') and sys.argv[1] not in ['basic', 'advanced', 'check', 'test', 'enhanced', 'requirements']:
        # User directly entered package names, use default check mode
        sys.argv.insert(1, 'check')
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    try:
        result = args.func(args)
        
        # Set exit code based on result
        if result is None:  # test command
            sys.exit(0)
        elif result.conflict_type == ConflictType.NO_CONFLICT:
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
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 