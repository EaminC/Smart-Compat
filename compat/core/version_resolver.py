#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Version Constraint Resolver
支持完整pip版本约束语法的解析器
"""

import re
from typing import List, Optional, Tuple, Union
from packaging import version
from packaging.specifiers import SpecifierSet, InvalidSpecifier


class VersionConstraintResolver:
    """高级版本约束解析器"""
    
    def __init__(self):
        # 支持的版本操作符（按长度排序，避免误匹配）
        self.operators = ['~=', '>=', '<=', '!=', '==', '>', '<']
    
    def parse_constraint(self, constraint_str: str) -> dict:
        """解析版本约束字符串"""
        try:
            # 使用packaging库解析
            spec_set = SpecifierSet(constraint_str)
            
            return {
                'valid': True,
                'spec_set': spec_set,
                'raw': constraint_str,
                'operators': [spec.operator for spec in spec_set],
                'versions': [spec.version for spec in spec_set]
            }
        except InvalidSpecifier as e:
            return {
                'valid': False,
                'error': str(e),
                'raw': constraint_str
            }
    
    def check_version_satisfies_constraint(self, version_str: str, constraint_str: str) -> dict:
        """检查版本是否满足约束"""
        try:
            ver = version.parse(version_str)
            constraint = self.parse_constraint(constraint_str)
            
            if not constraint['valid']:
                return {
                    'satisfies': False,
                    'error': constraint['error']
                }
            
            spec_set = constraint['spec_set']
            satisfies = ver in spec_set
            
            return {
                'satisfies': satisfies,
                'version': version_str,
                'constraint': constraint_str,
                'parsed_version': str(ver),
                'details': constraint
            }
            
        except Exception as e:
            return {
                'satisfies': False,
                'error': f"Version parsing error: {e}"
            }
    
    def find_compatible_versions(self, available_versions: List[str], constraint_str: str) -> dict:
        """从可用版本中找到满足约束的版本"""
        try:
            constraint = self.parse_constraint(constraint_str)
            
            if not constraint['valid']:
                return {
                    'compatible_versions': [],
                    'error': constraint['error']
                }
            
            spec_set = constraint['spec_set']
            compatible = []
            
            for ver_str in available_versions:
                try:
                    ver = version.parse(ver_str)
                    if ver in spec_set:
                        compatible.append({
                            'version': ver_str,
                            'parsed': str(ver),
                            'satisfies': True
                        })
                except Exception:
                    # 跳过无法解析的版本
                    continue
            
            # 按版本号排序
            compatible.sort(key=lambda x: version.parse(x['version']), reverse=True)
            
            return {
                'compatible_versions': compatible,
                'constraint': constraint_str,
                'total_available': len(available_versions),
                'total_compatible': len(compatible)
            }
            
        except Exception as e:
            return {
                'compatible_versions': [],
                'error': f"Constraint resolution error: {e}"
            }
    
    def check_constraints_compatibility(self, constraint1: str, constraint2: str) -> dict:
        """检查两个约束是否兼容（是否有交集）"""
        try:
            spec1 = SpecifierSet(constraint1)
            spec2 = SpecifierSet(constraint2)
            
            # 创建一个测试版本范围来检查交集
            # 这里使用一种近似方法：生成一些测试版本，看是否有同时满足两个约束的
            test_versions = self._generate_test_versions()
            
            compatible_versions = []
            for ver_str in test_versions:
                try:
                    ver = version.parse(ver_str)
                    if ver in spec1 and ver in spec2:
                        compatible_versions.append(ver_str)
                except Exception:
                    continue
            
            has_intersection = len(compatible_versions) > 0
            
            return {
                'compatible': has_intersection,
                'constraint1': constraint1,
                'constraint2': constraint2,
                'common_versions': compatible_versions[:10],  # 只返回前10个
                'intersection_exists': has_intersection
            }
            
        except Exception as e:
            return {
                'compatible': False,
                'error': f"Compatibility check error: {e}"
            }
    
    def _generate_test_versions(self) -> List[str]:
        """生成测试版本列表"""
        test_versions = []
        
        # 生成常见的版本号模式
        for major in range(0, 10):
            for minor in range(0, 20):
                for patch in range(0, 10):
                    test_versions.append(f"{major}.{minor}.{patch}")
        
        # 添加一些预发布版本
        for major in range(1, 5):
            for minor in range(0, 5):
                test_versions.extend([
                    f"{major}.{minor}.0rc1",
                    f"{major}.{minor}.0a1",
                    f"{major}.{minor}.0b1"
                ])
        
        return test_versions
    
    def resolve_constraints_intersection(self, constraints: List[str]) -> dict:
        """解析多个约束的交集"""
        try:
            if not constraints:
                return {'valid': False, 'error': 'No constraints provided'}
            
            # 合并所有约束
            combined_spec = SpecifierSet(','.join(constraints))
            
            # 生成测试版本并找到满足所有约束的版本
            test_versions = self._generate_test_versions()
            compatible = []
            
            for ver_str in test_versions:
                try:
                    ver = version.parse(ver_str)
                    if ver in combined_spec:
                        compatible.append(ver_str)
                except Exception:
                    continue
            
            # 排序
            compatible.sort(key=lambda x: version.parse(x), reverse=True)
            
            return {
                'valid': True,
                'combined_constraint': str(combined_spec),
                'compatible_versions': compatible[:20],  # 前20个
                'has_solution': len(compatible) > 0,
                'input_constraints': constraints
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Constraint intersection error: {e}",
                'input_constraints': constraints
            }
    
    def explain_constraint(self, constraint_str: str) -> dict:
        """解释版本约束的含义"""
        try:
            spec_set = SpecifierSet(constraint_str)
            explanations = []
            
            for spec in spec_set:
                op = spec.operator
                ver = spec.version
                
                if op == '==':
                    explanations.append(f"Exactly version {ver}")
                elif op == '>=':
                    explanations.append(f"Version {ver} or higher")
                elif op == '<=':
                    explanations.append(f"Version {ver} or lower")
                elif op == '>':
                    explanations.append(f"Higher than version {ver}")
                elif op == '<':
                    explanations.append(f"Lower than version {ver}")
                elif op == '!=':
                    explanations.append(f"Not version {ver}")
                elif op == '~=':
                    explanations.append(f"Compatible with {ver} (allows patch-level changes)")
                else:
                    explanations.append(f"Operator {op} with version {ver}")
            
            return {
                'valid': True,
                'constraint': constraint_str,
                'explanations': explanations,
                'human_readable': ' AND '.join(explanations)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Cannot explain constraint: {e}"
            } 