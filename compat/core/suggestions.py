#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package name suggestion module
Provides intelligent suggestions for misspelled or non-existent package names
"""

import re
import json
import urllib.request
import urllib.parse
import difflib
from typing import List, Dict, Optional, Tuple
from collections import Counter


class PackageNameSuggester:
    """Package name suggestion engine"""
    
    def __init__(self):
        self.common_packages_cache = {}
        self.pypi_cache = {}
        
        # Common package typos mapping
        self.common_typos = {
            'reqests': 'requests',
            'beautifulsoup': 'beautifulsoup4',
            'bs4': 'beautifulsoup4',
            'pillow': 'Pillow',
            'PIL': 'Pillow',
            'sklearn': 'scikit-learn',
            'cv2': 'opencv-python',
            'opencv': 'opencv-python',
            'matplotlib': 'matplotlib',
            'tensorflow': 'tensorflow',
            'tf': 'tensorflow',
            'torch': 'torch',
            'pytorch': 'torch',
            'numpy': 'numpy',
            'np': 'numpy',
            'pandas': 'pandas',
            'pd': 'pandas',
            'scipy': 'scipy',
            'flask': 'Flask',
            'django': 'Django',
            'fastapi': 'fastapi',
            'sqlalchemy': 'SQLAlchemy',
            'pymongo': 'pymongo',
            'redis': 'redis',
            'celery': 'celery',
            'gunicorn': 'gunicorn',
            'uwsgi': 'uWSGI'
        }
        
        # Popular packages for similarity comparison
        self.popular_packages = [
            'requests', 'urllib3', 'certifi', 'numpy', 'pandas', 'matplotlib',
            'scipy', 'pillow', 'opencv-python', 'tensorflow', 'torch',
            'scikit-learn', 'beautifulsoup4', 'lxml', 'flask', 'django',
            'fastapi', 'sqlalchemy', 'pymongo', 'redis', 'celery',
            'gunicorn', 'pytest', 'setuptools', 'wheel', 'pip'
        ]
    
    def calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two strings using multiple algorithms"""
        word1, word2 = word1.lower(), word2.lower()
        
        # 1. Levenshtein distance-based similarity
        import difflib
        seq_similarity = difflib.SequenceMatcher(None, word1, word2).ratio()
        
        # 2. Common substring similarity
        common_length = len(self._longest_common_substring(word1, word2))
        max_length = max(len(word1), len(word2))
        substring_similarity = common_length / max_length if max_length > 0 else 0
        
        # 3. Character frequency similarity
        char_freq_similarity = self._character_frequency_similarity(word1, word2)
        
        # Weighted combination
        final_similarity = (
            seq_similarity * 0.5 +
            substring_similarity * 0.3 +
            char_freq_similarity * 0.2
        )
        
        return final_similarity
    
    def _longest_common_substring(self, str1: str, str2: str) -> str:
        """Find longest common substring"""
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        longest = 0
        ending_pos_i = 0
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                    if dp[i][j] > longest:
                        longest = dp[i][j]
                        ending_pos_i = i
                else:
                    dp[i][j] = 0
        
        return str1[ending_pos_i - longest: ending_pos_i]
    
    def _character_frequency_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity based on character frequency"""
        counter1 = Counter(str1)
        counter2 = Counter(str2)
        
        all_chars = set(counter1.keys()) | set(counter2.keys())
        
        if not all_chars:
            return 1.0
        
        similarity_sum = 0
        for char in all_chars:
            freq1 = counter1.get(char, 0)
            freq2 = counter2.get(char, 0)
            max_freq = max(freq1, freq2)
            min_freq = min(freq1, freq2)
            similarity_sum += min_freq / max_freq if max_freq > 0 else 0
        
        return similarity_sum / len(all_chars)
    
    def check_typo_corrections(self, package_name: str) -> List[str]:
        """Check for common typo corrections"""
        package_lower = package_name.lower()
        suggestions = []
        
        # Exact match in typo dictionary
        if package_lower in self.common_typos:
            suggestions.append(self.common_typos[package_lower])
        
        # Fuzzy match in typo dictionary
        for typo, correction in self.common_typos.items():
            if self.calculate_similarity(package_lower, typo) > 0.8:
                suggestions.append(correction)
        
        return list(set(suggestions))
    
    def find_similar_local_packages(self, package_name: str, threshold: float = 0.6) -> List[Tuple[str, float]]:
        """Find similar packages from popular package list"""
        similarities = []
        
        for popular_pkg in self.popular_packages:
            similarity = self.calculate_similarity(package_name, popular_pkg)
            if similarity >= threshold:
                similarities.append((popular_pkg, similarity))
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:5]  # Return top 5 matches
    
    def search_pypi_packages(self, package_name: str, max_results: int = 5) -> List[Dict]:
        """Search PyPI for similar package names"""
        try:
            # Check cache first
            cache_key = f"{package_name}_{max_results}"
            if cache_key in self.pypi_cache:
                return self.pypi_cache[cache_key]
            
            # PyPI simple API search
            query = urllib.parse.quote(package_name)
            url = f"https://pypi.org/simple/"
            
            # Alternative: use PyPI JSON API for search
            search_url = f"https://pypi.org/pypi/{query}/json"
            
            try:
                # First try exact match
                with urllib.request.urlopen(search_url, timeout=3) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        result = [{
                            'name': data['info']['name'],
                            'summary': data['info']['summary'],
                            'version': data['info']['version']
                        }]
                        self.pypi_cache[cache_key] = result
                        return result
            except:
                pass
            
            # If exact match fails, try search approach
            # Use a simple search by checking package names
            suggestions = self._search_pypi_simple(package_name, max_results)
            self.pypi_cache[cache_key] = suggestions
            return suggestions
            
        except Exception as e:
            print(f"Warning: PyPI search failed: {e}")
            return []
    
    def _search_pypi_simple(self, package_name: str, max_results: int) -> List[Dict]:
        """Simplified PyPI search using popular packages and similarity"""
        # For now, we'll use local similarity search as PyPI search API is complex
        # In a real implementation, you might want to use PyPI's search API or maintain a local index
        
        similar_packages = self.find_similar_local_packages(package_name, threshold=0.4)
        
        results = []
        for pkg_name, similarity in similar_packages[:max_results]:
            results.append({
                'name': pkg_name,
                'summary': f'Popular Python package (similarity: {similarity:.2f})',
                'version': 'latest'
            })
        
        return results
    
    def generate_suggestions(self, package_name: str) -> Dict[str, List]:
        """Generate comprehensive suggestions for a package name"""
        suggestions = {
            'typo_corrections': [],
            'similar_packages': [],
            'pypi_search': []
        }
        
        # 1. Check typo corrections
        typo_corrections = self.check_typo_corrections(package_name)
        suggestions['typo_corrections'] = typo_corrections
        
        # 2. Find similar local packages
        similar_packages = self.find_similar_local_packages(package_name)
        suggestions['similar_packages'] = [
            {'name': name, 'similarity': round(score, 3)} 
            for name, score in similar_packages
        ]
        
        # 3. Search PyPI (with timeout and error handling)
        try:
            pypi_results = self.search_pypi_packages(package_name)
            suggestions['pypi_search'] = pypi_results
        except Exception as e:
            print(f"PyPI search failed: {e}")
            suggestions['pypi_search'] = []
        
        return suggestions
    
    def format_suggestions_text(self, package_name: str, suggestions: Dict[str, List]) -> str:
        """Format suggestions as human-readable text"""
        lines = []
        
        if suggestions['typo_corrections']:
            lines.append("🔤 Possible typo corrections:")
            for correction in suggestions['typo_corrections']:
                lines.append(f"   • {correction}")
        
        if suggestions['similar_packages']:
            lines.append("📦 Similar package names:")
            for pkg in suggestions['similar_packages']:
                lines.append(f"   • {pkg['name']} (similarity: {pkg['similarity']})")
        
        if suggestions['pypi_search']:
            lines.append("🔍 PyPI search results:")
            for pkg in suggestions['pypi_search']:
                summary = pkg.get('summary', 'No description')
                if len(summary) > 50:
                    summary = summary[:47] + "..."
                lines.append(f"   • {pkg['name']} - {summary}")
        
        if not any(suggestions.values()):
            lines.append("💡 No suggestions found. Please check the package name.")
        
        return "\n".join(lines)
    
    def check_version_exists(self, package_name: str, version: str) -> Dict[str, any]:
        """Check if a specific version exists on PyPI and get available versions"""
        try:
            # Check cache first
            cache_key = f"versions_{package_name}"
            if cache_key in self.pypi_cache:
                available_versions = self.pypi_cache[cache_key]
                latest_version = self.pypi_cache.get(f"latest_{package_name}")
            else:
                # Query PyPI for available versions
                search_url = f"https://pypi.org/pypi/{package_name}/json"
                with urllib.request.urlopen(search_url, timeout=5) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        available_versions = list(data.get('releases', {}).keys())
                        
                        # Get the actual latest version from PyPI info
                        latest_version = data.get('info', {}).get('version', '')
                        
                        # Cache the results
                        self.pypi_cache[cache_key] = available_versions
                        self.pypi_cache[f"latest_{package_name}"] = latest_version
                    else:
                        return {
                            'exists': False,
                            'available_versions': [],
                            'suggested_versions': [],
                            'error': f"Failed to query PyPI for {package_name}"
                        }
            
            # Check if the specific version exists
            version_exists = version in available_versions
            
            # Generate version suggestions if the version doesn't exist
            suggested_versions = []
            if not version_exists and available_versions:
                # Find similar versions (close to requested version)
                similar_versions = self._find_similar_versions(version, available_versions)
                
                # Also add some recent versions (properly sorted)
                recent_versions = self._get_recent_versions(available_versions, latest_version)
                
                # Combine similar and recent versions
                suggested_versions = self._combine_version_suggestions(similar_versions, recent_versions)
            
            return {
                'exists': version_exists,
                'available_versions': available_versions,
                'suggested_versions': suggested_versions,
                'latest_version': latest_version,
                'similar_versions': self._find_similar_versions(version, available_versions) if not version_exists else [],
                'recent_versions': self._get_recent_versions(available_versions, latest_version) if not version_exists else []
            }
            
        except Exception as e:
            return {
                'exists': False,
                'available_versions': [],
                'suggested_versions': [],
                'error': f"Version check failed: {e}"
            }
    
    def _parse_version_tuple(self, version_str: str) -> tuple:
        """Parse version string into comparable tuple"""
        try:
            # Remove any non-numeric suffixes (like 'rc1', 'a1', etc.)
            clean_version = re.sub(r'[^0-9\.].*', '', version_str)
            parts = clean_version.split('.')
            
            # Convert to integers, pad with zeros if needed
            version_tuple = []
            for part in parts[:4]:  # Take at most 4 parts
                try:
                    version_tuple.append(int(part))
                except ValueError:
                    version_tuple.append(0)
            
            # Pad to at least 3 parts for comparison
            while len(version_tuple) < 3:
                version_tuple.append(0)
                
            return tuple(version_tuple)
        except:
            return (0, 0, 0)
    
    def _get_recent_versions(self, available_versions: List[str], latest_version: str) -> List[str]:
        """Get recent versions, properly sorted"""
        try:
            # Parse and sort versions
            version_tuples = []
            for v in available_versions:
                if v.strip():  # Skip empty versions
                    version_tuples.append((v, self._parse_version_tuple(v)))
            
            # Sort by version tuple in descending order
            version_tuples.sort(key=lambda x: x[1], reverse=True)
            
            # Get top 5 recent versions
            recent_versions = [v[0] for v in version_tuples[:5]]
            
            # Ensure latest_version is first if it exists
            if latest_version and latest_version in available_versions:
                if latest_version in recent_versions:
                    recent_versions.remove(latest_version)
                recent_versions.insert(0, latest_version)
            
            return recent_versions[:5]
            
        except Exception as e:
            print(f"Warning: Failed to sort versions: {e}")
            # Fallback: return latest_version plus some others
            result = []
            if latest_version and latest_version in available_versions:
                result.append(latest_version)
            
            # Add a few more from the end of the list
            for v in available_versions[-4:]:
                if v not in result:
                    result.append(v)
            
            return result[:5]
    
    def _find_similar_versions(self, target_version: str, available_versions: List[str]) -> List[str]:
        """Find versions similar to target version (e.g., 2.1.099 -> 2.1.0, 2.1.1)"""
        similarities = []
        target_tuple = self._parse_version_tuple(target_version)
        
        for version in available_versions:
            version_tuple = self._parse_version_tuple(version)
            
            # Calculate similarity based on version components
            similarity = 0.0
            
            # Major version match is most important
            if target_tuple[0] == version_tuple[0]:
                similarity += 0.5
                
                # Minor version match
                if len(target_tuple) > 1 and len(version_tuple) > 1 and target_tuple[1] == version_tuple[1]:
                    similarity += 0.3
                    
                    # Patch version proximity
                    if len(target_tuple) > 2 and len(version_tuple) > 2:
                        patch_diff = abs(target_tuple[2] - version_tuple[2])
                        if patch_diff == 0:
                            similarity += 0.2
                        elif patch_diff <= 5:
                            similarity += 0.1
            
            # Also consider string similarity for exact matches
            string_sim = self.calculate_similarity(target_version, version)
            similarity = max(similarity, string_sim)
            
            if similarity > 0.3:
                similarities.append((version, similarity))
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [v for v, s in similarities[:5]]
    
    def _combine_version_suggestions(self, similar_versions: List[str], recent_versions: List[str]) -> List[str]:
        """Combine similar and recent versions into a good suggestion list"""
        suggestions = []
        
        # Add most similar versions first
        suggestions.extend(similar_versions[:3])
        
        # Add recent versions, avoiding duplicates
        for v in recent_versions:
            if v not in suggestions:
                suggestions.append(v)
            if len(suggestions) >= 8:  # Limit total suggestions
                break
        
        return suggestions[:8]  # Return at most 8 suggestions
    
    def generate_version_suggestions(self, package_name: str, version: str) -> Dict[str, any]:
        """Generate suggestions for version-specific issues"""
        suggestions = {
            'version_exists': False,
            'suggested_versions': [],
            'latest_version': None,
            'error': None
        }
        
        try:
            version_info = self.check_version_exists(package_name, version)
            # Map the 'exists' key to 'version_exists'
            suggestions['version_exists'] = version_info.get('exists', False)
            suggestions['suggested_versions'] = version_info.get('suggested_versions', [])
            suggestions['latest_version'] = version_info.get('latest_version', None)
            suggestions['error'] = version_info.get('error', None)
            
            # Keep the original data for detailed output
            suggestions.update(version_info)
            
        except Exception as e:
            suggestions['error'] = f"Failed to check version: {e}"
        
        return suggestions


def get_package_suggestions(package_name: str) -> Dict[str, List]:
    """Convenience function to get package suggestions"""
    suggester = PackageNameSuggester()
    return suggester.generate_suggestions(package_name) 