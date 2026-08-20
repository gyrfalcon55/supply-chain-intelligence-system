from sqlglot import parse
from sqlglot.errors import ParseError
from utils.logger import logging

class SQLSafetyService:

    ALLOWED_STATEMENTS = {"SELECT"}

    @classmethod
    def validate(cls, query: str) -> bool:
        """
        Validate that the SQL query is safe for the read-only
        Analytics Agent.

        Only SELECT statements are allowed.
        Multiple statements are rejected.
        """

        logging.info("validating generated sql query")

        if not query or not query.strip():
            raise ValueError("SQL query cannot be empty.")

        query = query.strip()

        try:
            statements = parse(query, read="postgres")

        except ParseError as exc:
            raise ValueError(
                f"Invalid SQL query: {exc}"
            ) from exc

        if not statements:
            raise ValueError("No SQL statement found.")

        if len(statements) != 1:
            raise ValueError(
                "Multiple SQL statements are not allowed."
            )

        statement = statements[0]

        statement_type = statement.key.upper()

        if statement_type not in cls.ALLOWED_STATEMENTS:
            logging.error("Generated sql query contains unsafe operations, query not allowed.")
            raise ValueError(
                f"Unsafe SQL operation '{statement_type}'. "
                "Only SELECT statements are allowed."
            )

        return True