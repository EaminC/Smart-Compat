#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package manager adapter abstract base class
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..core.types import PackageInfo


class PackageManagerAdapter(ABC):
    """Package manager adapter abstract base class"""
    
    @abstractmethod
    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get package information"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if package manager is available"""
        pass
    
    @abstractmethod
    def parse_version_constraint(self, constraint: str) -> str:
        """Parse version constraint"""
        pass 