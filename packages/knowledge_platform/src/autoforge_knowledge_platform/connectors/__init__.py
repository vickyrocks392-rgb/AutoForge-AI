"""
Knowledge Platform Source Connectors

Concrete source connector implementations as defined in the Knowledge Platform Specification v1.0, Section 10.
"""

from .documentation_connector import DocumentationConnector
from .code_connector import CodeConnector
from .academic_connector import AcademicConnector
from .expert_connector import ExpertConnector
from .community_connector import CommunityConnector
from .proprietary_connector import ProprietaryConnector

__all__ = [
    "DocumentationConnector",
    "CodeConnector",
    "AcademicConnector",
    "ExpertConnector",
    "CommunityConnector",
    "ProprietaryConnector",
]