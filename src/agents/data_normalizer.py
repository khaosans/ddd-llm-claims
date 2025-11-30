"""
Data Normalizer - Automatic data cleaning and type conversion

Handles common LLM output data issues:
- Comma-separated numbers
- Date format variations
- Type mismatches
- Missing fields with defaults
- Enum case sensitivity
- Whitespace issues
- String to number conversions
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional, Type, Union
from enum import Enum
import typing


class DataNormalizer:
    """
    Automatically normalizes and fixes data before Pydantic validation.
    
    This provides resilience by handling common data format issues
    that LLMs might produce, allowing the system to work reliably
    even with imperfect LLM outputs.
    """
    
    # Common date formats to try
    DATE_FORMATS = [
        "%Y-%m-%dT%H:%M:%S",  # ISO format with time
        "%Y-%m-%dT%H:%M:%S.%f",  # ISO with microseconds
        "%Y-%m-%d %H:%M:%S",  # Space-separated
        "%Y-%m-%d",  # Date only
        "%m/%d/%Y",  # US format
        "%d/%m/%Y",  # European format
        "%B %d, %Y",  # "January 15, 2024"
        "%b %d, %Y",  # "Jan 15, 2024"
        "%Y-%m-%dT%H:%M:%SZ",  # ISO with Z
        "%Y-%m-%dT%H:%M:%S%z",  # ISO with timezone
    ]
    
    @classmethod
    def normalize_data(cls, data: Dict[str, Any], schema: Type) -> Dict[str, Any]:
        """
        Normalize data dictionary to match expected schema types.
        
        Args:
            data: Raw data dictionary from LLM
            schema: Pydantic model class
            
        Returns:
            Normalized data dictionary
        """
        if not isinstance(data, dict):
            return data
        
        from pydantic import BaseModel
        
        if not issubclass(schema, BaseModel):
            return data
        
        normalized = {}
        schema_fields = schema.model_fields if hasattr(schema, 'model_fields') else {}
        
        for field_name, field_info in schema_fields.items():
            value = data.get(field_name)
            
            # Get field type
            field_type = cls._get_field_type(field_info)
            
            # Normalize based on type
            if value is not None:
                normalized_value = cls._normalize_value(value, field_type, field_name, schema)
                normalized[field_name] = normalized_value
            elif hasattr(field_info, 'default') and field_info.default is not None:
                # Use default if available
                default = field_info.default
                if callable(default):
                    normalized[field_name] = default()
                else:
                    normalized[field_name] = default
            elif hasattr(field_info, 'default_factory') and field_info.default_factory:
                # Use default factory
                normalized[field_name] = field_info.default_factory()
        
        return normalized
    
    @classmethod
    def _get_field_type(cls, field_info: Any) -> Optional[Type]:
        """Extract the actual type from Pydantic field info."""
        if not hasattr(field_info, 'annotation'):
            return None
        
        annotation = field_info.annotation
        
        # Handle Optional[Type] and Union types
        if hasattr(typing, 'get_origin') and typing.get_origin(annotation):
            origin = typing.get_origin(annotation)
            args = typing.get_args(annotation)
            
            # For Optional[Type], get the non-None type
            if origin is Union or (hasattr(typing, 'Union') and origin == typing.Union):
                # Filter out None type
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    return non_none_types[0]
            
            return annotation
        
        # Handle old-style Union (Python < 3.10)
        if hasattr(annotation, '__origin__'):
            if annotation.__origin__ is Union:
                args = getattr(annotation, '__args__', [])
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    return non_none_types[0]
        
        return annotation
    
    @classmethod
    def _normalize_value(cls, value: Any, field_type: Optional[Type], field_name: str, schema: Type) -> Any:
        """Normalize a single value based on expected type."""
        
        # If already correct type, return as-is
        if field_type and isinstance(value, field_type):
            return value
        
        # Handle Decimal/numeric types
        if field_type in (Decimal, float, int):
            return cls._normalize_numeric(value, field_type)
        
        # Handle datetime
        if field_type == datetime:
            return cls._normalize_datetime(value)
        
        # Handle Enum types
        if field_type and isinstance(field_type, type) and issubclass(field_type, Enum):
            return cls._normalize_enum(value, field_type)
        
        # Handle string - clean whitespace
        if field_type == str and isinstance(value, str):
            return value.strip()
        
        # Handle list types
        if field_type and hasattr(typing, 'get_origin'):
            origin = typing.get_origin(field_type)
            if origin is list or (hasattr(typing, 'List') and origin == typing.List):
                return cls._normalize_list(value, field_type)
        
        return value
    
    @classmethod
    def _normalize_numeric(cls, value: Any, target_type: Type) -> Any:
        """Normalize numeric values, handling comma-separated strings."""
        if isinstance(value, (int, float, Decimal)):
            if target_type == Decimal:
                return Decimal(str(value))
            return target_type(value)
        
        if isinstance(value, str):
            # Remove commas, whitespace, currency symbols
            cleaned = re.sub(r'[,\s$€£¥]', '', value.strip())
            
            # Try to parse
            try:
                if target_type == Decimal:
                    return Decimal(cleaned)
                elif target_type == float:
                    return float(cleaned)
                elif target_type == int:
                    return int(float(cleaned))  # Allow "123.0" -> 123
            except (ValueError, TypeError):
                pass
        
        return value
    
    @classmethod
    def _normalize_datetime(cls, value: Any) -> Any:
        """Normalize datetime values, trying multiple formats."""
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            value = value.strip()
            
            # Try ISO format first (most common)
            for fmt in cls.DATE_FORMATS:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            
            # Try parsing with dateutil if available
            try:
                from dateutil import parser
                return parser.parse(value)
            except (ImportError, ValueError, TypeError):
                pass
        
        return value
    
    @classmethod
    def _normalize_enum(cls, value: Any, enum_type: Type[Enum]) -> Any:
        """Normalize enum values, handling case-insensitive matching."""
        if isinstance(value, enum_type):
            return value
        
        if isinstance(value, str):
            value = value.strip()
            
            # Try exact match first
            try:
                return enum_type(value)
            except ValueError:
                pass
            
            # Try case-insensitive match
            value_lower = value.lower()
            for enum_member in enum_type:
                if enum_member.value.lower() == value_lower:
                    return enum_member
            
            # Try matching by name
            for enum_member in enum_type:
                if enum_member.name.lower() == value_lower:
                    return enum_member
        
        return value
    
    @classmethod
    def _normalize_list(cls, value: Any, list_type: Type) -> Any:
        """Normalize list values."""
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            # Try to parse as JSON array
            try:
                import json
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            
            # Try splitting by comma
            if ',' in value:
                return [item.strip() for item in value.split(',')]
        
        return value
    
    @classmethod
    def auto_fix_common_issues(cls, data: Dict[str, Any], schema: Type) -> Dict[str, Any]:
        """
        Automatically fix common data issues.
        
        This is a more aggressive normalization that tries to fix
        issues even when type information isn't available.
        """
        if not isinstance(data, dict):
            return data
        
        fixed = data.copy()
        
        # Fix numeric fields (by name pattern)
        numeric_patterns = ['amount', 'cost', 'price', 'value', 'score', 'confidence', 
                           'limit', 'coverage', 'deductible', 'premium']
        for key, value in fixed.items():
            if any(pattern in key.lower() for pattern in numeric_patterns):
                if isinstance(value, str):
                    fixed[key] = cls._normalize_numeric(value, Decimal)
        
        # Fix date fields (by name pattern)
        date_patterns = ['date', 'time', 'timestamp', 'created', 'updated', 'reported', 'incident']
        for key, value in fixed.items():
            if any(pattern in key.lower() for pattern in date_patterns):
                if isinstance(value, str):
                    normalized = cls._normalize_datetime(value)
                    if isinstance(normalized, datetime):
                        fixed[key] = normalized
        
        # Clean string fields
        for key, value in fixed.items():
            if isinstance(value, str):
                fixed[key] = value.strip()
        
        return fixed

