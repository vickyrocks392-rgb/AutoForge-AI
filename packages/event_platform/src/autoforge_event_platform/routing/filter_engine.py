"""
Event Filter Engine (Section 7.1, 21).

Filters events based on subscription filters.
Evaluates filter expressions.
Optimizes filter performance.
Returns filtered events.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from autoforge_event_platform.interfaces import IEventFilterEngine
from autoforge_event_platform.models.event import (
    Event,
    ValidationError,
    ValidationResult,
)


class FilterEngine(IEventFilterEngine):
    """
    Filter Engine implementation (Section 7.1, 21).

    Supports filter expressions with the following syntax:
        {field} {operator} {value}

    Operators (Section 21.2):
        =, !=, >, <, >=, <=, IN, NOT IN, CONTAINS, STARTS WITH, ENDS WITH

    Logical operators: AND, OR, NOT
    """

    _COMPARISON_OPS = {
        "=",
        "!=",
        ">",
        "<",
        ">=",
        "<=",
        "IN",
        "NOT IN",
        "CONTAINS",
        "STARTS WITH",
        "ENDS WITH",
    }

    def evaluate(self, event: Event, filter_expression: str) -> bool:
        """
        Evaluate a filter expression against an event (Section 21.3).

        Returns True if the event matches the filter.
        """
        if not filter_expression or not filter_expression.strip():
            return True

        try:
            tokens = self._tokenize(filter_expression)
            result, _ = self._parse_and_evaluate(tokens, 0, event)
            return result
        except Exception:
            return False

    def validate_filter(self, filter_expression: str) -> ValidationResult:
        """Validate a filter expression (Section 21.3)."""
        if not filter_expression or not filter_expression.strip():
            return ValidationResult(valid=True, errors=[])

        errors: list[ValidationError] = []

        try:
            tokens = self._tokenize(filter_expression)
            self._validate_tokens(tokens)
        except ValueError as e:
            errors.append(
                ValidationError(
                    field="filter",
                    error="invalid_filter",
                    message=str(e),
                )
            )

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def _tokenize(self, expr: str) -> list[str]:
        """Tokenize a filter expression into tokens."""
        expr = expr.replace("\n", " ").strip()

        token_pattern = re.compile(
            r"""
            \s*(
                '[^']*'
                | "[^"]*"
                | \(
                | \)
                | >=|<=|!=|<>|=
                | >|<
                | \bIN\b
                | \bNOT\s+IN\b
                | \bCONTAINS\b
                | \bSTARTS\s+WITH\b
                | \bENDS\s+WITH\b
                | \bAND\b
                | \bOR\b
                | \bNOT\b
                | [^\s()]+
            )\s*
            """,
            re.IGNORECASE | re.VERBOSE,
        )

        tokens: list[str] = []
        pos = 0
        while pos < len(expr):
            match = token_pattern.match(expr, pos)
            if not match:
                if expr[pos:].strip() == "":
                    break
                raise ValueError(f"Unexpected token at position {pos}: {expr[pos:]}")
            token = match.group(1).strip()
            if token:
                token = re.sub(r"\s+", " ", token)
                tokens.append(token)
            pos = match.end()

        return tokens

    def _validate_tokens(self, tokens: list[str]) -> None:
        """Validate that tokens form a syntactically correct expression."""
        if not tokens:
            return

        depth = 0
        for token in tokens:
            if token == "(":
                depth += 1
            elif token == ")":
                depth -= 1
                if depth < 0:
                    raise ValueError("Unbalanced parentheses")
        if depth != 0:
            raise ValueError("Unbalanced parentheses")

    def _parse_and_evaluate(
        self, tokens: list[str], pos: int, event: Event
    ) -> tuple[bool, int]:
        """Parse and evaluate an OR expression (lowest precedence)."""
        left, pos = self._parse_and(tokens, pos, event)

        while pos < len(tokens) and tokens[pos].upper() == "OR":
            pos += 1
            right, pos = self._parse_and(tokens, pos, event)
            left = left or right

        return left, pos

    def _parse_and(
        self, tokens: list[str], pos: int, event: Event
    ) -> tuple[bool, int]:
        """Parse and evaluate an AND expression."""
        left, pos = self._parse_not(tokens, pos, event)

        while pos < len(tokens) and tokens[pos].upper() == "AND":
            pos += 1
            right, pos = self._parse_not(tokens, pos, event)
            left = left and right

        return left, pos

    def _parse_not(
        self, tokens: list[str], pos: int, event: Event
    ) -> tuple[bool, int]:
        """Parse and evaluate a NOT expression."""
        if pos < len(tokens) and tokens[pos].upper() == "NOT":
            pos += 1
            result, pos = self._parse_not(tokens, pos, event)
            return not result, pos

        return self._parse_comparison(tokens, pos, event)

    def _parse_comparison(
        self, tokens: list[str], pos: int, event: Event
    ) -> tuple[bool, int]:
        """Parse and evaluate a comparison or parenthesized expression."""
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression")

        if tokens[pos] == "(":
            pos += 1
            result, pos = self._parse_and_evaluate(tokens, pos, event)
            if pos >= len(tokens) or tokens[pos] != ")":
                raise ValueError("Missing closing parenthesis")
            pos += 1
            return result, pos

        if pos + 2 > len(tokens):
            raise ValueError("Incomplete comparison expression")

        field = tokens[pos]
        pos += 1

        if pos >= len(tokens):
            raise ValueError("Missing operator in comparison")

        operator = tokens[pos].upper()
        pos += 1

        if operator == "NOT":
            if pos < len(tokens) and tokens[pos].upper() == "IN":
                operator = "NOT IN"
                pos += 1
            else:
                raise ValueError("Expected IN after NOT")

        if operator == "STARTS":
            if pos < len(tokens) and tokens[pos].upper() == "WITH":
                operator = "STARTS WITH"
                pos += 1
        elif operator == "ENDS":
            if pos < len(tokens) and tokens[pos].upper() == "WITH":
                operator = "ENDS WITH"
                pos += 1

        if operator not in self._COMPARISON_OPS:
            raise ValueError(f"Unknown operator: {operator}")

        if pos >= len(tokens):
            raise ValueError("Missing value in comparison")

        value = tokens[pos]
        pos += 1

        # Handle IN / NOT IN with parenthesized list
        if operator in ("IN", "NOT IN"):
            values: list[Any] = []
            if value == "(":
                while pos < len(tokens) and tokens[pos] != ")":
                    if tokens[pos] != ",":
                        values.append(self._parse_value(tokens[pos]))
                    pos += 1
                if pos < len(tokens):
                    pos += 1  # skip )
            else:
                values.append(self._parse_value(value))
            result = self._compare(field, operator, values, event)
        else:
            result = self._compare(field, operator, self._parse_value(value), event)

        return result, pos

    def _parse_value(self, token: str) -> Any:
        """Parse a token value into a Python type."""
        if (token.startswith("'") and token.endswith("'")) or (
            token.startswith('"') and token.endswith('"')
        ):
            return token[1:-1]

        if token.lower() == "true":
            return True
        if token.lower() == "false":
            return False

        try:
            if "." in token:
                return float(token)
            return int(token)
        except ValueError:
            pass

        try:
            return datetime.fromisoformat(token)
        except (ValueError, TypeError):
            pass

        return token

    def _get_field_value(self, event: Event, field: str) -> Any:
        """Extract a field value from an event."""
        event_fields = {
            "eventId": str(event.event_id),
            "eventType": event.event_type.value,
            "eventCategory": event.event_category.value,
            "source": event.source,
            "timestamp": event.timestamp,
            "version": event.version,
            "correlationId": str(event.correlation_id),
            "causationId": str(event.causation_id) if event.causation_id else None,
            "aggregateId": str(event.aggregate_id),
            "aggregateType": event.aggregate_type,
            "priority": event.priority.value,
            "deliveryMode": event.delivery_mode.value,
        }

        if field in event_fields:
            return event_fields[field]

        if field.startswith("payload."):
            key = field[8:]
            return event.payload.get(key)

        if field.startswith("metadata."):
            key = field[9:]
            return event.metadata.get(key)

        if field in event.payload:
            return event.payload[field]

        if field in event.metadata:
            return event.metadata[field]

        return None

    def _compare(
        self, field: str, operator: str, value: Any, event: Event
    ) -> bool:
        """Compare a field value against a comparison value."""
        field_value = self._get_field_value(event, field)

        if field_value is None:
            return False

        if operator == "=":
            return str(field_value) == str(value)
        elif operator == "!=":
            return str(field_value) != str(value)
        elif operator == ">":
            try:
                return field_value > value
            except TypeError:
                return False
        elif operator == "<":
            try:
                return field_value < value
            except TypeError:
                return False
        elif operator == ">=":
            try:
                return field_value >= value
            except TypeError:
                return False
        elif operator == "<=":
            try:
                return field_value <= value
            except TypeError:
                return False
        elif operator == "IN":
            if isinstance(value, list):
                return str(field_value) in [str(v) for v in value]
            return str(field_value) == str(value)
        elif operator == "NOT IN":
            if isinstance(value, list):
                return str(field_value) not in [str(v) for v in value]
            return str(field_value) != str(value)
        elif operator == "CONTAINS":
            return str(value) in str(field_value)
        elif operator == "STARTS WITH":
            return str(field_value).startswith(str(value))
        elif operator == "ENDS WITH":
            return str(field_value).endswith(str(value))
        else:
            return False
