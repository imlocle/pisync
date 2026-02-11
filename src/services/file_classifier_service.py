"""
File classification service (DEPRECATED).

This module is deprecated and will be removed in a future version.
The application now trusts the folder structure instead of using heuristics.

Files under Movies/ are movies.
Files under TV_shows/ are TV shows.
"""

import os
from typing import Set
import warnings


class FileClassifierService:
    """
    DEPRECATED: File classification based on folder structure.
    
    This service is no longer needed with the simplified path mapping approach.
    Classification is now based solely on the folder structure:
    - Files under Movies/ -> movie
    - Files under TV_shows/ -> tv
    
    This class is kept for backward compatibility but will be removed in v2.0.
    """
    
    def __init__(self):
        warnings.warn(
            "FileClassifierService is deprecated and will be removed in v2.0. "
            "Use folder structure for classification instead.",
            DeprecationWarning,
            stacklevel=2
        )
    
    def classify_file(self, file_path: str, file_exts: Set[str]) -> str:
        """
        Classify a file as movie or TV show based on path.
        
        DEPRECATED: Use folder structure instead.
        
        Args:
            file_path: Path to file
            file_exts: Set of valid media extensions (unused)
            
        Returns:
            "movie" or "tv"
        """
        # Simple path-based classification
        path_lower = file_path.lower()
        
        if "tv_shows" in path_lower or "tv shows" in path_lower:
            return "tv"
        elif "movies" in path_lower:
            return "movie"
        
        # Default to movie
        return "movie"
    
    def classify_folder(self, folder_path: str) -> str:
        """
        Classify a folder as movie or TV show based on path.
        
        DEPRECATED: Use folder structure instead.
        
        Args:
            folder_path: Path to folder
            
        Returns:
            "movie" or "tv"
        """
        # Simple path-based classification
        path_lower = folder_path.lower()
        
        if "tv_shows" in path_lower or "tv shows" in path_lower:
            return "tv"
        elif "movies" in path_lower:
            return "movie"
        
        # Default to movie
        return "movie"
