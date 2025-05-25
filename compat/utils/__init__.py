"""
Utility modules for package conflict detection
"""

from .suggestions import PackageNameSuggester
from .pip_resolver import PipDependencyResolver
from .version_resolver import VersionConstraintResolver

__all__ = [
    "PackageNameSuggester",
    "PipDependencyResolver",
    "VersionConstraintResolver",
]
