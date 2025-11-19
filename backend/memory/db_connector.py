"""
Database Connector Abstraction

Exposes whitelisted databases (Postgres, DuckDB, SQLite) through
memory catalog so Grace can mount them as read-only or read-write slots.
"""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from backend.memory.memory_catalog import memory_catalog, AssetType


class DatabaseType(str, Enum):
    """Supported database types"""
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    DUCKDB = "duckdb"
    MYSQL = "mysql"


class AccessMode(str, Enum):
    """Database access modes"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"


@dataclass
class DatabaseConnection:
    """Database connection configuration"""
    db_name: str
    db_type: DatabaseType
    connection_string: str
    access_mode: AccessMode
    asset_id: str
    schema_info: Optional[Dict[str, Any]] = None


class DatabaseConnector(ABC):
    """Base class for database connectors"""

    @abstractmethod
    def connect(self) -> Any:
        """Establish database connection"""
        pass

    @abstractmethod
    def query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        pass

    @abstractmethod
    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connection"""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        pass


class SQLiteConnector(DatabaseConnector):
    """SQLite database connector"""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.db_path = connection.connection_string.replace("sqlite:///", "")
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Establish SQLite connection"""
        if self.conn is None:
            if self.connection.access_mode == AccessMode.READ_ONLY:
                self.conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            else:
                self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE"""
        if self.connection.access_mode == AccessMode.READ_ONLY:
            raise PermissionError("Database mounted as read-only")
        
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.rowcount

    def close(self) -> None:
        """Close connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_schema(self) -> Dict[str, Any]:
        """Get SQLite schema"""
        tables = self.query("""
            SELECT name, sql 
            FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        schema = {"tables": {}}
        for table in tables:
            columns = self.query(f"PRAGMA table_info({table['name']})")
            schema["tables"][table["name"]] = {
                "columns": [
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "nullable": not col["notnull"],
                        "primary_key": bool(col["pk"]),
                    }
                    for col in columns
                ],
                "create_sql": table["sql"],
            }
        
        return schema


class PostgresConnector(DatabaseConnector):
    """PostgreSQL database connector (requires psycopg2)"""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.conn: Optional[Any] = None

    def connect(self) -> Any:
        """Establish PostgreSQL connection"""
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError("psycopg2 required for PostgreSQL support")
        
        if self.conn is None:
            self.conn = psycopg2.connect(
                self.connection.connection_string,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            if self.connection.access_mode == AccessMode.READ_ONLY:
                self.conn.set_session(readonly=True)
        
        return self.conn

    def query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE"""
        if self.connection.access_mode == AccessMode.READ_ONLY:
            raise PermissionError("Database mounted as read-only")
        
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.rowcount

    def close(self) -> None:
        """Close connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_schema(self) -> Dict[str, Any]:
        """Get PostgreSQL schema"""
        tables = self.query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        schema = {"tables": {}}
        for table in tables:
            table_name = table["table_name"]
            columns = self.query("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
            """, (table_name,))
            
            schema["tables"][table_name] = {
                "columns": [
                    {
                        "name": col["column_name"],
                        "type": col["data_type"],
                        "nullable": col["is_nullable"] == "YES",
                        "default": col["column_default"],
                    }
                    for col in columns
                ]
            }
        
        return schema


class DuckDBConnector(DatabaseConnector):
    """DuckDB database connector (requires duckdb)"""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.db_path = connection.connection_string.replace("duckdb:///", "")
        self.conn: Optional[Any] = None

    def connect(self) -> Any:
        """Establish DuckDB connection"""
        try:
            import duckdb
        except ImportError:
            raise ImportError("duckdb required for DuckDB support")
        
        if self.conn is None:
            self.conn = duckdb.connect(
                self.db_path,
                read_only=self.connection.access_mode == AccessMode.READ_ONLY
            )
        return self.conn

    def query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        conn = self.connect()
        result = conn.execute(sql, params or ()).fetchall()
        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]

    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE"""
        if self.connection.access_mode == AccessMode.READ_ONLY:
            raise PermissionError("Database mounted as read-only")
        
        conn = self.connect()
        result = conn.execute(sql, params or ())
        conn.commit()
        return result.fetchone()[0] if result else 0

    def close(self) -> None:
        """Close connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_schema(self) -> Dict[str, Any]:
        """Get DuckDB schema"""
        tables = self.query("SHOW TABLES")
        
        schema = {"tables": {}}
        for table in tables:
            table_name = table["name"]
            columns = self.query(f"DESCRIBE {table_name}")
            schema["tables"][table_name] = {
                "columns": [
                    {
                        "name": col["column_name"],
                        "type": col["column_type"],
                        "nullable": col["null"] == "YES",
                    }
                    for col in columns
                ]
            }
        
        return schema


class DatabaseConnectorFactory:
    """Factory for creating database connectors"""

    CONNECTOR_MAP = {
        DatabaseType.SQLITE: SQLiteConnector,
        DatabaseType.POSTGRES: PostgresConnector,
        DatabaseType.DUCKDB: DuckDBConnector,
    }

    @classmethod
    def create_connector(cls, connection: DatabaseConnection) -> DatabaseConnector:
        """Create appropriate connector for database type"""
        connector_class = cls.CONNECTOR_MAP.get(connection.db_type)
        if not connector_class:
            raise ValueError(f"Unsupported database type: {connection.db_type}")
        return connector_class(connection)


class DatabaseMountManager:
    """
    Manages mounted databases through memory catalog
    
    Provides unified interface to:
    - List available databases
    - Connect to whitelisted databases
    - Execute queries with access control
    - Discover schema information
    """

    def __init__(self):
        self.active_connections: Dict[str, DatabaseConnector] = {}

    def get_connection(self, db_name: str) -> Optional[DatabaseConnector]:
        """
        Get connection to mounted database
        
        Args:
            db_name: Database name
        
        Returns:
            DatabaseConnector or None
        """
        if db_name in self.active_connections:
            return self.active_connections[db_name]
        
        assets = memory_catalog.list_assets(asset_type=AssetType.DATABASE)
        
        for asset in assets:
            if asset.metadata.get("db_name") == db_name or asset.asset_id == db_name:
                connection = DatabaseConnection(
                    db_name=db_name,
                    db_type=DatabaseType(asset.metadata.get("db_type", "sqlite")),
                    connection_string=asset.metadata.get("connection_string", ""),
                    access_mode=AccessMode(asset.metadata.get("access_mode", "read_only")),
                    asset_id=asset.asset_id,
                    schema_info=asset.metadata.get("schema_info"),
                )
                
                connector = DatabaseConnectorFactory.create_connector(connection)
                self.active_connections[db_name] = connector
                return connector
        
        return None

    def list_mounted_databases(self) -> List[Dict[str, Any]]:
        """List all mounted databases"""
        assets = memory_catalog.list_assets(asset_type=AssetType.DATABASE)
        return [
            {
                "db_name": asset.metadata.get("db_name", "unknown"),
                "db_type": asset.metadata.get("db_type", "unknown"),
                "access_mode": asset.metadata.get("access_mode", "read_only"),
                "asset_id": asset.asset_id,
            }
            for asset in assets
        ]

    def close_all(self) -> None:
        """Close all active connections"""
        for connector in self.active_connections.values():
            connector.close()
        self.active_connections.clear()


db_mount_manager = DatabaseMountManager()
