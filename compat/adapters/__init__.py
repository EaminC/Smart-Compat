#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package Manager Adapter Module
Contains adapter implementations for various package managers
"""

from .base import PackageManagerAdapter
from .pip_adapter import PipAdapter
from .npm_adapter import NpmAdapter

__all__ = [
    "PackageManagerAdapter",
    "PipAdapter", 
    "NpmAdapter",
] 