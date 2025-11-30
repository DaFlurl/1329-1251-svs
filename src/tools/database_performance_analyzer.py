#!/usr/bin/env python3
"""
AgentDaf1.1 Database Performance Analyzer
Analyzes database queries and identifies performance bottlenecks
"""

import sqlite3
import time
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

class DatabasePerformanceAnalyzer:
    """Analyzes and optimizes database performance"""
    
    def __init__(self, db_path: str = "data/agentdaf1.db"):
        self.db_path = db_path
        self.analysis_results = {}
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with performance settings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Performance optimizations
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA mmap_size = 268435456")  # 256MB
        
        return conn
    
    def analyze_current_performance(self) -> Dict[str, Any]:
        """Comprehensive database performance analysis"""
        print("🔍 Analyzing database performance...")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "database_info": self._get_database_info(),
            "table_analysis": self._analyze_tables(),
            "query_performance": self._test_query_performance(),
            "index_analysis": self._analyze_indexes(),
            "recommendations": []
        }
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        self.analysis_results = analysis
        return analysis
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get basic database information"""
        info = {}
        
        with self.get_connection() as conn:
            # Database size
            if os.path.exists(self.db_path):
                size_bytes = os.path.getsize(self.db_path)
                info["size_bytes"] = size_bytes
                info["size_mb"] = round(size_bytes / (1024 * 1024), 2)
            
            # Page size and settings
            cursor = conn.execute("PRAGMA page_size")
            info["page_size"] = cursor.fetchone()[0]
            
            cursor = conn.execute("PRAGMA page_count")
            info["page_count"] = cursor.fetchone()[0]
            
            # SQLite version
            cursor = conn.execute("SELECT sqlite_version()")
            info["sqlite_version"] = cursor.fetchone()[0]
            
            # Journal mode
            cursor = conn.execute("PRAGMA journal_mode")
            info["journal_mode"] = cursor.fetchone()[0]
            
            # Synchronous mode
            cursor = conn.execute("PRAGMA synchronous")
            info["synchronous_mode"] = cursor.fetchone()[0]
            
            # Cache size
            cursor = conn.execute("PRAGMA cache_size")
            info["cache_size"] = cursor.fetchone()[0]
            
        return info
    
    def _analyze_tables(self) -> Dict[str, Any]:
        """Analyze all tables in the database"""
        tables_info = {}
        
        with self.get_connection() as conn:
            # Get all table names
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                table_info = {
                    "row_count": 0,
                    "columns": [],
                    "indexes": [],
                    "size_estimate": 0
                }
                
                # Get row count
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                table_info["row_count"] = cursor.fetchone()[0]
                
                # Get column information
                cursor = conn.execute(f"PRAGMA table_info({table})")
                table_info["columns"] = [dict(row) for row in cursor.fetchall()]
                
                # Get index information
                cursor = conn.execute(f"PRAGMA index_list({table})")
                table_info["indexes"] = [dict(row) for row in cursor.fetchall()]
                
                # Estimate table size (rough calculation)
                if table_info["row_count"] > 0:
                    avg_row_size = len(str(table_info["columns"])) * 50  # Rough estimate
                    table_info["size_estimate"] = table_info["row_count"] * avg_row_size
                
                tables_info[table] = table_info
        
        return tables_info
    
    def _test_query_performance(self) -> Dict[str, Any]:
        """Test performance of common queries"""
        query_tests = {}
        
        with self.get_connection() as conn:
            # Test common queries
            queries = [
                {
                    "name": "get_all_players_ordered",
                    "query": "SELECT * FROM players ORDER BY score DESC, created_at ASC",
                    "description": "Get all players ordered by score"
                },
                {
                    "name": "get_all_alliances_ordered", 
                    "query": "SELECT * FROM alliances ORDER BY total_score DESC, created_at ASC",
                    "description": "Get all alliances ordered by total score"
                },
                {
                    "name": "get_recent_system_logs",
                    "query": "SELECT * FROM system_logs ORDER BY created_at DESC LIMIT 100",
                    "description": "Get recent system logs"
                },
                {
                    "name": "get_player_sessions",
                    "query": """
                        SELECT gs.*, p.name as player_name 
                        FROM game_sessions gs 
                        JOIN players p ON gs.player_id = p.id 
                        ORDER BY gs.created_at DESC LIMIT 10
                    """,
                    "description": "Get recent game sessions with player names"
                },
                {
                    "name": "database_stats_query",
                    "query": """
                        SELECT 
                            'players' as table_name, COUNT(*) as row_count 
                        FROM players 
                        UNION ALL 
                        SELECT 'alliances', COUNT(*) FROM alliances 
                        UNION ALL 
                        SELECT 'game_sessions', COUNT(*) FROM game_sessions 
                        UNION ALL 
                        SELECT 'system_logs', COUNT(*) FROM system_logs
                    """,
                    "description": "Get row counts for all tables"
                }
            ]
            
            for query_test in queries:
                try:
                    # Warm up
                    conn.execute(query_test["query"]).fetchall()
                    
                    # Performance test
                    start_time = time.time()
                    result = conn.execute(query_test["query"]).fetchall()
                    end_time = time.time()
                    
                    query_tests[query_test["name"]] = {
                        "query": query_test["query"],
                        "description": query_test["description"],
                        "execution_time_ms": round((end_time - start_time) * 1000, 2),
                        "result_count": len(result),
                        "performance_rating": self._rate_query_performance(end_time - start_time)
                    }
                    
                except Exception as e:
                    query_tests[query_test["name"]] = {
                        "query": query_test["query"],
                        "error": str(e),
                        "execution_time_ms": None,
                        "result_count": 0,
                        "performance_rating": "ERROR"
                    }
        
        return query_tests
    
    def _analyze_indexes(self) -> Dict[str, Any]:
        """Analyze existing and missing indexes"""
        index_analysis = {
            "existing_indexes": {},
            "recommended_indexes": [],
            "index_usage": {}
        }
        
        with self.get_connection() as conn:
            # Get all tables
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Get existing indexes
                cursor = conn.execute(f"PRAGMA index_list({table})")
                existing_indexes = [dict(row) for row in cursor.fetchall()]
                
                index_analysis["existing_indexes"][table] = existing_indexes
                
                # Analyze index details
                for index in existing_indexes:
                    cursor = conn.execute(f"PRAGMA index_info({index['name']})")
                    index_info = [dict(row) for row in cursor.fetchall()]
                    index_analysis["index_usage"][index['name']] = {
                        "table": table,
                        "columns": [info['name'] for info in index_info],
                        "unique": index['unique'] == 1,
                        "partial": index['partial'] == 1
                    }
        
        # Generate recommended indexes based on query patterns
        index_analysis["recommended_indexes"] = self._generate_index_recommendations()
        
        return index_analysis
    
    def _generate_index_recommendations(self) -> List[Dict[str, Any]]:
        """Generate index recommendations based on common query patterns"""
        recommendations = [
            {
                "table": "players",
                "columns": ["score", "created_at"],
                "type": "composite",
                "reason": "Frequently used for ordering players by score and date",
                "priority": "high",
                "sql": "CREATE INDEX IF NOT EXISTS idx_players_score_created ON players(score DESC, created_at ASC);"
            },
            {
                "table": "players",
                "columns": ["name"],
                "type": "unique",
                "reason": "Frequently used for player lookups by name",
                "priority": "high",
                "sql": "CREATE UNIQUE INDEX IF NOT EXISTS idx_players_name ON players(name);"
            },
            {
                "table": "alliances",
                "columns": ["total_score", "created_at"],
                "type": "composite",
                "reason": "Frequently used for ordering alliances by total score",
                "priority": "high",
                "sql": "CREATE INDEX IF NOT EXISTS idx_alliances_score_created ON alliances(total_score DESC, created_at ASC);"
            },
            {
                "table": "game_sessions",
                "columns": ["player_id", "created_at"],
                "type": "composite",
                "reason": "Frequently used for getting player sessions ordered by date",
                "priority": "medium",
                "sql": "CREATE INDEX IF NOT EXISTS idx_game_sessions_player_created ON game_sessions(player_id, created_at DESC);"
            },
            {
                "table": "system_logs",
                "columns": ["created_at"],
                "type": "single",
                "reason": "Frequently used for getting recent logs",
                "priority": "medium",
                "sql": "CREATE INDEX IF NOT EXISTS idx_system_logs_created ON system_logs(created_at DESC);"
            },
            {
                "table": "system_logs",
                "columns": ["level", "created_at"],
                "type": "composite",
                "reason": "Frequently used for filtering logs by level and date",
                "priority": "medium",
                "sql": "CREATE INDEX IF NOT EXISTS idx_system_logs_level_created ON system_logs(level, created_at DESC);"
            },
            {
                "table": "user_preferences",
                "columns": ["user_id"],
                "type": "unique",
                "reason": "Frequently used for user preference lookups",
                "priority": "high",
                "sql": "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);"
            }
        ]
        
        return recommendations
    
    def _rate_query_performance(self, execution_time: float) -> str:
        """Rate query performance based on execution time"""
        if execution_time < 0.01:  # < 10ms
            return "EXCELLENT"
        elif execution_time < 0.05:  # < 50ms
            return "GOOD"
        elif execution_time < 0.1:  # < 100ms
            return "FAIR"
        elif execution_time < 0.5:  # < 500ms
            return "POOR"
        else:
            return "CRITICAL"
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance recommendations based on analysis"""
        recommendations = []
        
        # Database size recommendations
        db_size_mb = analysis["database_info"].get("size_mb", 0)
        if db_size_mb > 100:
            recommendations.append({
                "category": "Database Size",
                "priority": "medium",
                "issue": f"Database size is {db_size_mb}MB",
                "recommendation": "Consider implementing data archiving for old records",
                "impact": "Reduced backup time and improved query performance"
            })
        
        # Query performance recommendations
        slow_queries = [
            name for name, test in analysis["query_performance"].items()
            if test.get("performance_rating") in ["POOR", "CRITICAL"]
        ]
        
        if slow_queries:
            recommendations.append({
                "category": "Query Performance",
                "priority": "high",
                "issue": f"Slow queries detected: {', '.join(slow_queries)}",
                "recommendation": "Add recommended indexes and optimize query structure",
                "impact": "Significantly improved response times"
            })
        
        # Index recommendations
        missing_indexes = len(analysis["index_analysis"]["recommended_indexes"])
        if missing_indexes > 0:
            recommendations.append({
                "category": "Indexing",
                "priority": "high",
                "issue": f"{missing_indexes} recommended indexes missing",
                "recommendation": "Create recommended indexes for better query performance",
                "impact": "Improved query performance, especially for ordered queries"
            })
        
        # Journal mode recommendations
        journal_mode = analysis["database_info"].get("journal_mode", "delete")
        if journal_mode != "wal":
            recommendations.append({
                "category": "Database Configuration",
                "priority": "medium",
                "issue": f"Journal mode is '{journal_mode}' instead of 'wal'",
                "recommendation": "Enable WAL mode for better concurrency",
                "impact": "Improved concurrent read/write performance"
            })
        
        # Table-specific recommendations
        for table_name, table_info in analysis["table_analysis"].items():
            if table_info["row_count"] > 10000 and not table_info["indexes"]:
                recommendations.append({
                    "category": "Table Optimization",
                    "priority": "high",
                    "issue": f"Table '{table_name}' has {table_info['row_count']} rows but no indexes",
                    "recommendation": f"Add indexes to {table_name} table",
                    "impact": "Dramatically improved query performance on large tables"
                })
        
        return recommendations
    
    def apply_optimizations(self) -> Dict[str, Any]:
        """Apply database performance optimizations"""
        print("⚡ Applying database optimizations...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": [],
            "errors": [],
            "performance_improvement": {}
        }
        
        with self.get_connection() as conn:
            try:
                # Apply database configuration optimizations
                optimizations = [
                    ("journal_mode", "WAL", "Enable WAL mode for better concurrency"),
                    ("synchronous", "NORMAL", "Set synchronous mode to NORMAL for better performance"),
                    ("cache_size", "10000", "Increase cache size to 10MB"),
                    ("temp_store", "MEMORY", "Store temporary tables in memory"),
                    ("mmap_size", "268435456", "Enable memory-mapped I/O (256MB)")
                ]
                
                for pragma, value, description in optimizations:
                    try:
                        conn.execute(f"PRAGMA {pragma} = {value}")
                        results["optimizations_applied"].append({
                            "type": "pragma",
                            "setting": pragma,
                            "value": value,
                            "description": description
                        })
                    except Exception as e:
                        results["errors"].append({
                            "type": "pragma_error",
                            "setting": pragma,
                            "error": str(e)
                        })
                
                # Apply recommended indexes
                index_recommendations = self._generate_index_recommendations()
                for index_rec in index_recommendations:
                    try:
                        conn.execute(index_rec["sql"])
                        results["optimizations_applied"].append({
                            "type": "index",
                            "table": index_rec["table"],
                            "columns": index_rec["columns"],
                            "sql": index_rec["sql"],
                            "description": index_rec["reason"]
                        })
                    except Exception as e:
                        results["errors"].append({
                            "type": "index_error",
                            "table": index_rec["table"],
                            "error": str(e)
                        })
                
                # Analyze tables to update query planner statistics
                conn.execute("ANALYZE")
                results["optimizations_applied"].append({
                    "type": "analyze",
                    "description": "Updated table statistics for query optimizer"
                })
                
                # Vacuum to rebuild database file
                conn.execute("VACUUM")
                results["optimizations_applied"].append({
                    "type": "vacuum",
                    "description": "Rebuilt database file to reduce fragmentation"
                })
                
                conn.commit()
                
            except Exception as e:
                results["errors"].append({
                    "type": "general_error",
                    "error": str(e)
                })
        
        # Measure performance improvement
        try:
            before_analysis = self.analysis_results.get("query_performance", {})
            after_analysis = self._test_query_performance()
            
            performance_improvement = {}
            for query_name in before_analysis:
                if query_name in after_analysis:
                    before_time = before_analysis[query_name].get("execution_time_ms", 0)
                    after_time = after_analysis[query_name].get("execution_time_ms", 0)
                    
                    if before_time > 0 and after_time > 0:
                        improvement = ((before_time - after_time) / before_time) * 100
                        performance_improvement[query_name] = {
                            "before_ms": before_time,
                            "after_ms": after_time,
                            "improvement_percent": round(improvement, 2)
                        }
            
            results["performance_improvement"] = performance_improvement
            
        except Exception as e:
            results["errors"].append({
                "type": "performance_measurement_error",
                "error": str(e)
            })
        
        return results
    
    def save_analysis_report(self, filename: str = None) -> str:
        """Save analysis report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_performance_analysis_{timestamp}.json"
        
        report_path = os.path.join("data", filename)
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        report_data = {
            "analysis": self.analysis_results,
            "generated_at": datetime.now().isoformat(),
            "analyzer_version": "1.0.0"
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return report_path

def main():
    """Main function to run database performance analysis"""
    print("🚀 AgentDaf1.1 Database Performance Analyzer")
    print("=" * 50)
    
    analyzer = DatabasePerformanceAnalyzer()
    
    # Analyze current performance
    print("\n📊 Analyzing current database performance...")
    analysis = analyzer.analyze_current_performance()
    
    # Display key findings
    print(f"\n📈 Database Size: {analysis['database_info']['size_mb']} MB")
    print(f"📋 Total Tables: {len(analysis['table_analysis'])}")
    
    # Show query performance
    print("\n⏱️ Query Performance:")
    for name, test in analysis['query_performance'].items():
        rating = test.get('performance_rating', 'UNKNOWN')
        time_ms = test.get('execution_time_ms', 0)
        print(f"  {name}: {time_ms}ms ({rating})")
    
    # Show recommendations
    print(f"\n💡 Recommendations: {len(analysis['recommendations'])}")
    for rec in analysis['recommendations']:
        print(f"  [{rec['priority'].upper()}] {rec['issue']}")
    
    # Ask if user wants to apply optimizations
    apply_optimizations = input("\n🔧 Apply optimizations? (y/n): ").lower().strip()
    
    if apply_optimizations == 'y':
        print("\n⚡ Applying optimizations...")
        results = analyzer.apply_optimizations()
        
        print(f"\n✅ Optimizations Applied: {len(results['optimizations_applied'])}")
        print(f"❌ Errors: {len(results['errors'])}")
        
        if results['errors']:
            print("\nErrors encountered:")
            for error in results['errors']:
                print(f"  - {error['type']}: {error['error']}")
        
        # Show performance improvements
        if results['performance_improvement']:
            print("\n📈 Performance Improvements:")
            for query, improvement in results['performance_improvement'].items():
                before = improvement['before_ms']
                after = improvement['after_ms']
                percent = improvement['improvement_percent']
                print(f"  {query}: {before}ms → {after}ms ({percent:+.1f}%)")
    
    # Save analysis report
    save_report = input("\n💾 Save analysis report? (y/n): ").lower().strip()
    if save_report == 'y':
        report_path = analyzer.save_analysis_report()
        print(f"📄 Report saved to: {report_path}")
    
    print("\n🎉 Database performance analysis complete!")

if __name__ == "__main__":
    main()