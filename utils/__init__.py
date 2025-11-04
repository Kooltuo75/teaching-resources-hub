"""
Utility functions for the Teaching Resources application.
This module will contain helper functions for various features.
"""

def format_grade_level(grade):
    """
    Format grade level for display.

    Args:
        grade: Grade level (can be number or string)

    Returns:
        Formatted grade level string
    """
    if isinstance(grade, int):
        if grade == 0:
            return "Kindergarten"
        elif grade <= 12:
            return f"Grade {grade}"
    return str(grade)
