from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from ...config.settings import settings
from ...monitoring.logger import get_logger
from ...database import SessionLocal, engine

logger = get_logger(__name__)

class DatabaseActionSystem:
    """System for database operations as actions"""
    
    def __init__(self):
        self.allowed_tables = [
            'actions_log', 'notifications', 'user_rules', 
            'data_streams', 'system_metrics'
        ]
        self.max_rows_per_operation = 1000
    
    async def update_data(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Update database records"""
        table = parameters.get('table')
        query = parameters.get('query', {})
        update_data = parameters.get('update', {})
        operation = parameters.get('operation', 'update')
        
        if not table:
            raise ValueError("Table name is required")
        
        # Validate table access
        if table not in self.allowed_tables:
            raise ValueError(f"Table '{table}' is not allowed for automatic updates")
        
        # Validate operation
        if operation not in ['update', 'insert', 'delete']:
            raise ValueError(f"Invalid operation: {operation}")
        
        db = SessionLocal()
        try:
            if operation == 'update':
                result = await self._update_records(db, table, query, update_data)
            elif operation == 'insert':
                result = await self._insert_record(db, table, update_data)
            elif operation == 'delete':
                result = await self._delete_records(db, table, query)
            
            db.commit()
            
            logger.info(f"Database {operation} successful on table '{table}'")
            return {
                "status": "success",
                "operation": operation,
                "table": table,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            db.close()
    
    async def _update_records(self, db, table: str, query: Dict, update_data: Dict) -> Dict[str, Any]:
        """Update multiple records"""
        # Convert query dict to SQL WHERE clause
        where_clause = self._build_where_clause(query)
        
        # Build SET clause
        set_clause = ', '.join([f"{k} = :{k}" for k in update_data.keys()])
        
        # Execute update
        sql = text(f"UPDATE {table} SET {set_clause} WHERE {where_clause}")
        
        # Add parameters
        params = {**update_data, **query}
        
        result = db.execute(sql, params)
        
        return {
            "rows_affected": result.rowcount,
            "query": str(sql),
            "parameters": params
        }
    
    async def _insert_record(self, db, table: str, data: Dict) -> Dict[str, Any]:
        """Insert a new record"""
        # Validate data against table schema
        self._validate_insert_data(table, data)
        
        # Build INSERT statement
        columns = ', '.join(data.keys())
        values = ', '.join([f":{k}" for k in data.keys()])
        
        sql = text(f"INSERT INTO {table} ({columns}) VALUES ({values})")
        
        result = db.execute(sql, data)
        db.flush()  # Get the generated ID
        
        # Try to get the inserted ID
        inserted_id = None
        if hasattr(result, 'inserted_primary_key'):
            inserted_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
        
        return {
            "rows_affected": result.rowcount,
            "inserted_id": inserted_id,
            "data": data
        }
    
    async def _delete_records(self, db, table: str, query: Dict) -> Dict[str, Any]:
        """Delete records"""
        # Safety check - prevent mass deletion
        if not query:
            raise ValueError("Delete operation requires a query to prevent mass deletion")
        
        # Check how many rows would be affected
        count_sql = text(f"SELECT COUNT(*) FROM {table} WHERE {self._build_where_clause(query)}")
        count_result = db.execute(count_sql, query).scalar()
        
        if count_result > self.max_rows_per_operation:
            raise ValueError(f"Delete operation would affect {count_result} rows, exceeding limit of {self.max_rows_per_operation}")
        
        # Execute delete
        sql = text(f"DELETE FROM {table} WHERE {self._build_where_clause(query)}")
        result = db.execute(sql, query)
        
        return {
            "rows_affected": result.rowcount,
            "expected_count": count_result,
            "query": str(sql)
        }
    
    def _build_where_clause(self, query: Dict) -> str:
        """Build SQL WHERE clause from query dict"""
        if not query:
            return "1=1"  # Match all rows (use with caution)
        
        conditions = []
        for key, value in query.items():
            if isinstance(value, dict):
                # Handle operators
                for op, op_value in value.items():
                    if op == '$gt':
                        conditions.append(f"{key} > :{key}")
                    elif op == '$lt':
                        conditions.append(f"{key} < :{key}")
                    elif op == '$gte':
                        conditions.append(f"{key} >= :{key}")
                    elif op == '$lte':
                        conditions.append(f"{key} <= :{key}")
                    elif op == '$ne':
                        conditions.append(f"{key} != :{key}")
                    elif op == '$in':
                        # Handle IN clause
                        placeholders = ', '.join([f":{key}_{i}" for i in range(len(op_value))])
                        conditions.append(f"{key} IN ({placeholders})")
                    elif op == '$like':
                        conditions.append(f"{key} LIKE :{key}")
            else:
                conditions.append(f"{key} = :{key}")
        
        return " AND ".join(conditions) if conditions else "1=1"
    
    def _validate_insert_data(self, table: str, data: Dict):
        """Validate data against table schema"""
        inspector = inspect(engine)
        
        # Get table columns
        columns = inspector.get_columns(table)
        column_names = [col['name'] for col in columns]
        
        # Check for required columns
        for column in columns:
            if not column.get('nullable', True) and column['name'] not in data:
                raise ValueError(f"Required column '{column['name']}' is missing")
        
        # Check for unknown columns
        for key in data.keys():
            if key not in column_names:
                raise ValueError(f"Unknown column '{key}' for table '{table}'")
    
    async def execute_raw_sql(self, sql: str, params: Dict = None) -> Dict[str, Any]:
        """Execute raw SQL (with extreme caution)"""
        # Only allow SELECT queries for raw SQL
        sql_lower = sql.strip().lower()
        if not sql_lower.startswith('select'):
            raise ValueError("Raw SQL execution only allowed for SELECT queries")
        
        db = SessionLocal()
        try:
            result = db.execute(text(sql), params or {})
            
            # Convert to list of dicts
            rows = [dict(row._mapping) for row in result]
            
            return {
                "status": "success",
                "rows": rows,
                "row_count": len(rows),
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    def get_table_info(self, table: str) -> Dict[str, Any]:
        """Get information about a table"""
        inspector = inspect(engine)
        
        try:
            columns = inspector.get_columns(table)
            primary_keys = inspector.get_pk_constraint(table)
            foreign_keys = inspector.get_foreign_keys(table)
            
            return {
                "table": table,
                "columns": [
                    {
                        "name": col['name'],
                        "type": str(col['type']),
                        "nullable": col.get('nullable', True),
                        "default": str(col.get('default', '')),
                        "autoincrement": col.get('autoincrement', False)
                    }
                    for col in columns
                ],
                "primary_keys": primary_keys.get('constrained_columns', []),
                "foreign_keys": [
                    {
                        "constrained_columns": fk['constrained_columns'],
                        "referred_table": fk['referred_table'],
                        "referred_columns": fk['referred_columns']
                    }
                    for fk in foreign_keys
                ]
            }
        except Exception as e:
            raise ValueError(f"Failed to get table info: {e}")