#!/usr/bin/env python3
"""
Load Decision Trees into Database
Populates the database with metadata about all available decision trees
"""

import yaml
from pathlib import Path
import psycopg2
from datetime import datetime
import sys

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'realdiag',
    'user': 'realdiag_user',
    'password': 'staging_db_pass_2024'
}

TREES_PATH = Path(__file__).parent.parent / "backend" / "trees"

def load_tree_metadata():
    """Load metadata from all YAML tree files"""
    trees = []
    
    if not TREES_PATH.exists():
        print(f"❌ Trees path not found: {TREES_PATH}")
        return trees
    
    for yaml_file in sorted(TREES_PATH.glob("*.yml")):
        try:
            with open(yaml_file, 'r') as f:
                doc = yaml.safe_load(f) or {}
            
            tree_id = doc.get("id") or doc.get("tree_id")
            if not tree_id:
                print(f"⚠️  Skipping {yaml_file.name}: no tree_id")
                continue
            
            # Extract metadata
            metadata = {
                'tree_id': tree_id,
                'name': doc.get("title") or doc.get("name") or tree_id,
                'family': doc.get("family", "GENERAL"),
                'specialty': doc.get("specialty", "General Medicine"),
                'chief_complaint': doc.get("chief_complaint", ""),
                'description': doc.get("description", ""),
                'version': doc.get("version", "1.0"),
                'author': doc.get("author", "RealDiag Team"),
                'node_count': len(doc.get("nodes", [])),
                'yaml_file': yaml_file.name
            }
            
            trees.append(metadata)
            print(f"✓ Loaded: {tree_id} - {metadata['name']}")
            
        except Exception as e:
            print(f"❌ Error loading {yaml_file.name}: {e}")
    
    return trees

def create_tables(conn):
    """Create tables for storing tree metadata"""
    with conn.cursor() as cur:
        # Decision trees catalog table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS decision_trees (
                tree_id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                family VARCHAR(100) NOT NULL,
                specialty VARCHAR(100),
                chief_complaint VARCHAR(255),
                description TEXT,
                version VARCHAR(20),
                author VARCHAR(100),
                node_count INTEGER DEFAULT 0,
                yaml_file VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Statistics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tree_statistics (
                tree_id VARCHAR(100) PRIMARY KEY,
                total_queries INTEGER DEFAULT 0,
                successful_diagnoses INTEGER DEFAULT 0,
                avg_decision_depth FLOAT DEFAULT 0,
                last_used TIMESTAMP,
                FOREIGN KEY (tree_id) REFERENCES decision_trees(tree_id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        print("✓ Tables created/verified")

def populate_trees(conn, trees):
    """Insert or update tree metadata in database"""
    with conn.cursor() as cur:
        inserted = 0
        updated = 0
        
        for tree in trees:
            # Check if exists
            cur.execute(
                "SELECT tree_id FROM decision_trees WHERE tree_id = %s",
                (tree['tree_id'],)
            )
            exists = cur.fetchone()
            
            if exists:
                # Update existing
                cur.execute("""
                    UPDATE decision_trees 
                    SET name = %s, family = %s, specialty = %s, 
                        chief_complaint = %s, description = %s, 
                        version = %s, author = %s, node_count = %s,
                        yaml_file = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE tree_id = %s
                """, (
                    tree['name'], tree['family'], tree['specialty'],
                    tree['chief_complaint'], tree['description'],
                    tree['version'], tree['author'], tree['node_count'],
                    tree['yaml_file'], tree['tree_id']
                ))
                updated += 1
            else:
                # Insert new
                cur.execute("""
                    INSERT INTO decision_trees 
                    (tree_id, name, family, specialty, chief_complaint, 
                     description, version, author, node_count, yaml_file)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    tree['tree_id'], tree['name'], tree['family'], 
                    tree['specialty'], tree['chief_complaint'], tree['description'],
                    tree['version'], tree['author'], tree['node_count'], 
                    tree['yaml_file']
                ))
                
                # Initialize statistics
                cur.execute("""
                    INSERT INTO tree_statistics (tree_id, total_queries, successful_diagnoses)
                    VALUES (%s, 0, 0)
                """, (tree['tree_id'],))
                
                inserted += 1
        
        conn.commit()
        print(f"✓ Inserted: {inserted}, Updated: {updated}")

def show_statistics(conn):
    """Display tree statistics"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT family, COUNT(*) as count
            FROM decision_trees
            WHERE is_active = TRUE
            GROUP BY family
            ORDER BY count DESC
        """)
        
        print("\n📊 Decision Trees by Family:")
        print("-" * 50)
        for family, count in cur.fetchall():
            print(f"  {family:20s} : {count:3d} trees")
        
        cur.execute("SELECT COUNT(*) FROM decision_trees WHERE is_active = TRUE")
        total = cur.fetchone()[0]
        print("-" * 50)
        print(f"  {'TOTAL':20s} : {total:3d} trees")

def main():
    print("=" * 60)
    print("RealDiag Decision Tree Database Loader")
    print("=" * 60)
    print()
    
    # Load tree metadata from YAML files
    print("📂 Loading decision tree YAML files...")
    trees = load_tree_metadata()
    
    if not trees:
        print("❌ No trees found!")
        return 1
    
    print(f"\n✓ Loaded {len(trees)} decision trees\n")
    
    # Connect to database
    print("🔌 Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected to PostgreSQL\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return 1
    
    try:
        # Create tables
        print("📋 Creating/verifying tables...")
        create_tables(conn)
        print()
        
        # Populate trees
        print("💾 Populating decision trees...")
        populate_trees(conn, trees)
        print()
        
        # Show statistics
        show_statistics(conn)
        
        print("\n" + "=" * 60)
        print("✅ Decision trees successfully loaded into database!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        return 1
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
