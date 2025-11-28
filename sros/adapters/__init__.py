"""Adapters package"""
from .base import AdapterResult, AdapterError
from .registry import get_registry

__all__ = ['AdapterResult', 'AdapterError', 'get_registry']
