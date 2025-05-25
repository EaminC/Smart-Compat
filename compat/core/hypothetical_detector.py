#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hypothetical Package Conflict Detector
支持假设性兼容性检测 - 检查指定版本组合的兼容性，而不是当前系统状态
"""

import re
import json
import urllib.request
from typing import Dict, List, Optional, Tuple, Set
from .advanced_detector import AdvancedConflictDetector
from .types import ConflictResult, ConflictType, PackageInfo


class HypotheticalConflictDetector(AdvancedConflictDetector):
    """支持假设性检测的增强冲突检测器"""
    
    def __init__(self, enable_suggestions: bool = True, hypothetical_mode: bool = True):
        super().__init__(enable_suggestions)
        self.hypothetical_mode = hypothetical_mode
    
    def get_hypothetical_package_info(self, package_name: str, version_spec: str = None) -> Optional[PackageInfo]:
        """获取假设版本的包信息（完全从PyPI查询，不依赖本地安装）"""
        try:
            # 如果指定了版本，使用该版本
            if version_spec:
                # 提取版本号
                version_number = version_spec
                for op in ['>=', '<=', '==', '>', '<']:
                    if version_spec.startswith(op):
                        version_number = version_spec[len(op):]
                        break
                
                return self._get_package_info_from_pypi(package_name, version_number)
            else:
                # 如果没有指定版本，从PyPI获取最新版本
                return self._get_latest_package_info_from_pypi(package_name)
        
        except Exception as e:
            print(f"Warning: Failed to get hypothetical package info for {package_name}: {e}")
            return None
    
    def _get_package_info_from_pypi(self, package_name: str, version: str) -> Optional[PackageInfo]:
        """从PyPI获取指定版本的包信息"""
        try:
            # 查询PyPI API
            url = f"https://pypi.org/pypi/{package_name}/{version}/json"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    info = data.get('info', {})
                    
                    # 解析依赖信息
                    dependencies = {}
                    requires_dist = info.get('requires_dist', []) or []
                    
                    for req in requires_dist:
                        if req and ';' not in req:  # 跳过条件依赖
                            # 改进的依赖解析：支持 "urllib3 (<1.27,>=1.21.1)" 这样的格式
                            req = req.strip()
                            
                            # 匹配 "package_name (constraint)" 或 "package_name constraint" 格式
                            match = re.match(r'([a-zA-Z0-9\-_.]+)\s*(.+)?', req)
                            if match:
                                dep_name = match.group(1).strip()
                                dep_constraint_raw = match.group(2) or ""
                                
                                # 清理约束字符串：去掉括号，保留版本约束
                                dep_constraint = dep_constraint_raw.strip()
                                if dep_constraint.startswith('(') and dep_constraint.endswith(')'):
                                    dep_constraint = dep_constraint[1:-1].strip()
                                
                                dependencies[dep_name] = dep_constraint
                    
                    return PackageInfo(
                        name=info.get('name', package_name),
                        version=version,
                        dependencies=dependencies,
                        description=info.get('summary', ''),
                        author=info.get('author', ''),
                        license=info.get('license', ''),
                        homepage=info.get('home_page', '')
                    )
                    
        except Exception as e:
            print(f"Warning: Failed to fetch {package_name} v{version} from PyPI: {e}")
            # 不再fallback到本地信息！如果PyPI查询失败，直接返回None
            return None
        
        return None
    
    def _get_latest_package_info_from_pypi(self, package_name: str) -> Optional[PackageInfo]:
        """从PyPI获取最新版本的包信息"""
        try:
            # 查询PyPI API获取最新版本
            url = f"https://pypi.org/pypi/{package_name}/json"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    info = data.get('info', {})
                    latest_version = info.get('version', '')
                    
                    if latest_version:
                        # 使用最新版本获取详细信息
                        return self._get_package_info_from_pypi(package_name, latest_version)
                    
        except Exception as e:
            print(f"Warning: Failed to fetch latest version for {package_name} from PyPI: {e}")
        
        return None

    def _generate_version_not_found_result(self, package_name: str, version_spec: str) -> ConflictResult:
        """生成版本不存在的结果，包含版本建议"""
        # 提取版本号
        version_number = version_spec
        operator = None
        for op in ['>=', '<=', '==', '>', '<']:
            if version_spec.startswith(op):
                operator = op
                version_number = version_spec[len(op):]
                break
        
        base_message = f"Version not found: {package_name} v{version_number} does not exist on PyPI"
        details = {
            "package": package_name,
            "requested_version": version_number,
            "operator": operator,
            "error": "version_not_found"
        }
        
        # 尝试获取可用版本建议
        if self.enable_suggestions:
            try:
                suggestions = self.suggester.generate_version_suggestions(package_name, version_number)
                if suggestions.get('suggested_versions'):
                    details["version_check"] = suggestions
                        
            except Exception as e:
                print(f"Warning: Failed to get version suggestions: {e}")
        
        return ConflictResult(
            conflict_type=ConflictType.VERSION_CONFLICT,
            message=base_message,
            severity="high",
            details=details
        )

    def _generate_package_not_found_result_pypi(self, package_name: str) -> ConflictResult:
        """生成包不存在的结果（基于PyPI查询）"""
        base_message = f"Package '{package_name}' not found on PyPI"
        details = {"error": f"Package {package_name} not found on PyPI"}
        
        # Add suggestions if enabled
        if self.enable_suggestions:
            try:
                suggestions = self.suggester.generate_suggestions(package_name)
                if any(suggestions.values()):
                    details["suggestions"] = suggestions
            except Exception as e:
                print(f"Warning: Failed to generate suggestions: {e}")
        
        severity = "info" if any(details.get("suggestions", {}).values()) else "warning"
        return ConflictResult(
            conflict_type=ConflictType.PACKAGE_NOT_FOUND,
            message=base_message,
            severity=severity,
            details=details
        )
    
    def detect_hypothetical_conflicts(self, package1: str, package2: str) -> ConflictResult:
        """检测假设性冲突 - 基于指定版本而非当前安装版本"""
        
        # 解析包规格
        pkg1_name, pkg1_version_spec = self.parse_package_spec(package1)
        pkg2_name, pkg2_version_spec = self.parse_package_spec(package2)
        
        # 1. 检查包名冲突（这部分逻辑不变）
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
        
        # 2. 获取假设的包信息
        if self.hypothetical_mode:
            pkg1_info = self.get_hypothetical_package_info(pkg1_name, pkg1_version_spec)
            pkg2_info = self.get_hypothetical_package_info(pkg2_name, pkg2_version_spec)
        else:
            # 回退到标准模式
            return super().detect_advanced_conflicts(package1, package2)
        
        # 3. 处理包/版本不存在的情况 - 严格检查
        if not pkg1_info:
            if pkg1_version_spec:
                # 指定了版本但找不到，可能是版本不存在
                return self._generate_version_not_found_result(pkg1_name, pkg1_version_spec)
            else:
                # 没有指定版本但找不到包，包不存在
                return self._generate_package_not_found_result_pypi(pkg1_name)
        
        if not pkg2_info:
            if pkg2_version_spec:
                # 指定了版本但找不到，可能是版本不存在
                return self._generate_version_not_found_result(pkg2_name, pkg2_version_spec)
            else:
                # 没有指定版本但找不到包，包不存在
                return self._generate_package_not_found_result_pypi(pkg2_name)
        
        # 4. 检查依赖版本约束冲突（新增）
        dependency_conflicts = self._check_dependency_version_constraints(pkg1_info, pkg2_info)
        if dependency_conflicts:
            conflict_messages = []
            for conflict in dependency_conflicts:
                conflict_messages.append(conflict['message'])
            
            return ConflictResult(
                conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                message="Dependency version conflicts detected:\n" + "\n".join(conflict_messages),
                severity="high",
                details={
                    "dependency_conflicts": dependency_conflicts,
                    "pkg1": pkg1_info.__dict__,
                    "pkg2": pkg2_info.__dict__
                }
            )
        
        # 5. 检查高级冲突（系统级和传递依赖）
        system_conflicts = self.check_system_level_conflicts(pkg1_info, pkg2_info)
        transitive_conflicts = self.check_transitive_dependency_conflicts(pkg1_info, pkg2_info)
        
        all_advanced_conflicts = system_conflicts + transitive_conflicts
        
        if all_advanced_conflicts:
            # 格式化冲突消息
            conflict_messages = []
            for conflict in all_advanced_conflicts:
                conflict_messages.append(conflict['reason'])
            
            # 确定冲突类型和严重性
            if any(c['type'] in ['cuda_version_conflict', 'cudnn_version_conflict'] for c in all_advanced_conflicts):
                conflict_type = ConflictType.DEPENDENCY_CONFLICT
                severity = "high"
                message_prefix = "System-level conflicts detected"
            else:
                conflict_type = ConflictType.DEPENDENCY_CONFLICT
                severity = "medium"
                message_prefix = "Advanced conflicts detected"
            
            return ConflictResult(
                conflict_type=conflict_type,
                message=f"{message_prefix}:\n" + "\n".join([f"• {msg}" for msg in conflict_messages]),
                severity=severity,
                details={
                    "advanced_conflicts": all_advanced_conflicts,
                    "pkg1": pkg1_info.__dict__,
                    "pkg2": pkg2_info.__dict__
                }
            )
        
        # 6. 如果没有冲突，返回成功结果
        return ConflictResult(
            conflict_type=ConflictType.NO_CONFLICT,
            message=f"No conflicts found: {pkg1_info.name} v{pkg1_info.version} and {pkg2_info.name} v{pkg2_info.version} are compatible",
            severity="low",
            details={
                "pkg1": pkg1_info.__dict__,
                "pkg2": pkg2_info.__dict__
            }
        )

    def _check_dependency_version_constraints(self, pkg1_info: PackageInfo, pkg2_info: PackageInfo) -> List[Dict]:
        """检查依赖版本约束冲突 - 例如pkg1依赖pkg2但版本约束不满足"""
        conflicts = []
        
        # 检查pkg1是否依赖pkg2，且版本约束不满足
        if pkg2_info.name.lower() in [dep.lower() for dep in pkg1_info.dependencies.keys()]:
            # 找到依赖约束
            constraint = None
            for dep_name, dep_constraint in pkg1_info.dependencies.items():
                if dep_name.lower() == pkg2_info.name.lower():
                    constraint = dep_constraint
                    break
            
            if constraint and not self._version_satisfies_constraint(pkg2_info.version, constraint):
                conflicts.append({
                    'type': 'dependency_version_constraint',
                    'package1': pkg1_info.name,
                    'package2': pkg2_info.name,
                    'constraint': constraint,
                    'actual_version': pkg2_info.version,
                    'message': f"{pkg1_info.name} v{pkg1_info.version} requires {pkg2_info.name} {constraint}, but you specified {pkg2_info.name}=={pkg2_info.version}"
                })
        
        # 检查pkg2是否依赖pkg1，且版本约束不满足
        if pkg1_info.name.lower() in [dep.lower() for dep in pkg2_info.dependencies.keys()]:
            # 找到依赖约束
            constraint = None
            for dep_name, dep_constraint in pkg2_info.dependencies.items():
                if dep_name.lower() == pkg1_info.name.lower():
                    constraint = dep_constraint
                    break
            
            if constraint and not self._version_satisfies_constraint(pkg1_info.version, constraint):
                conflicts.append({
                    'type': 'dependency_version_constraint',
                    'package1': pkg2_info.name,
                    'package2': pkg1_info.name,
                    'constraint': constraint,
                    'actual_version': pkg1_info.version,
                    'message': f"{pkg2_info.name} v{pkg2_info.version} requires {pkg1_info.name} {constraint}, but you specified {pkg1_info.name}=={pkg1_info.version}"
                })
        
        return conflicts

    def _version_satisfies_constraint(self, version: str, constraint: str) -> bool:
        """检查版本是否满足约束条件"""
        if not constraint or constraint == "*":
            return True
        
        try:
            from packaging import version as pkg_version
            from packaging.specifiers import SpecifierSet
            
            ver = pkg_version.parse(version)
            spec_set = SpecifierSet(constraint)
            return ver in spec_set
            
        except Exception as e:
            print(f"Warning: Failed to check version constraint {version} against {constraint}: {e}")
            # 回退到简单的版本比较
            return self._version_matches_constraint_simple(version, constraint)

    def _version_matches_constraint_simple(self, version: str, constraint: str) -> bool:
        """简单的版本约束检查（回退方法）"""
        try:
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
            elif ',' in constraint:
                # 处理复合约束，如 ">=1.21.1,<1.27"
                constraints = [c.strip() for c in constraint.split(',')]
                return all(self._version_matches_constraint_simple(version, c) for c in constraints)
            else:
                return version == constraint.strip()
                
        except Exception:
            return False 