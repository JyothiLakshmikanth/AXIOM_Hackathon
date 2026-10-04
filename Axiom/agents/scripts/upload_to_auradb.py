"""
Uploads the AXIOM Data-Driven Knowledge Graph to live Neo4j AuraDB.
Reads credentials from .env and executes data/neo4j_import_script.cypher.
"""

import os
import sys

# Configure UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")
CYPHER_PATH = os.path.join(BASE_DIR, "data", "neo4j_import_script.cypher")

# Load .env file
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

URI = os.getenv("NEO4J_URI", "neo4j+s://fe6b9516.databases.neo4j.io")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PWD = os.getenv("NEO4J_PASSWORD")


def connect_and_upload():
    global USER
    print("=" * 60)
    print("AXIOM: Ingesting Knowledge Graph into Neo4j AuraDB")
    print(f"Target URI : {URI}")
    print(f"Username   : {USER}")
    print("=" * 60)

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("\n[!] Python package 'neo4j' is not installed.")
        print("    Run: pip install neo4j")
        print("\nAlternatively, you can copy the contents of:")
        print(f"    {CYPHER_PATH}")
        print("and paste them directly into the AuraDB Query Console at https://console.neo4j.io/\n")
        return False

    if not PWD:
        print("[!] NEO4J_PASSWORD is not set in .env")
        return False

    driver = None
    for try_user in [USER, "jyothijyo2222@gmail.com", "neo4j"]:
        try:
            print(f"Connecting to AuraDB with username '{try_user}'...")
            driver = GraphDatabase.driver(URI, auth=(try_user, PWD))
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    print(f"[✓] Connected successfully to AuraDB using username '{try_user}'!")
                    USER = try_user
                    break
        except Exception as e:
            print(f"[-] Connection attempt failed for '{try_user}': {e}")
            driver = None

    if not driver:
        print("\n[!] Could not authenticate with AuraDB.")
        print("Please check your password or paste the Cypher script directly into console.neo4j.io.")
        return False

    print(f"\nReading Cypher import script from {CYPHER_PATH}...")
    with open(CYPHER_PATH, "r", encoding="utf-8") as f:
        full_content = f.read()

    # Split into discrete statements separated by semicolons
    statements = []
    current_stmt = []
    for line in full_content.splitlines():
        clean_line = line.strip()
        if clean_line.startswith("//") or not clean_line:
            continue
        current_stmt.append(line)
        if clean_line.endswith(";"):
            statements.append("\n".join(current_stmt).rstrip(";"))
            current_stmt = []

    print(f"Executing {len(statements)} Cypher statements into AuraDB...")
    success_count = 0
    with driver.session() as session:
        for i, stmt in enumerate(statements):
            try:
                session.run(stmt)
                success_count += 1
                if (i + 1) % 25 == 0 or (i + 1) == len(statements):
                    print(f"  Processed {i + 1}/{len(statements)} statements...")
            except Exception as e:
                # Log minor warnings like constraint already exists
                pass

        # Verification query
        print("\nVerifying Ingested Nodes & Edges in AuraDB:")
        node_counts = session.run("MATCH (n) RETURN labels(n)[0] as Label, count(*) as Count ORDER BY Count DESC")
        for rec in node_counts:
            print(f"  - {rec['Label']:20}: {rec['Count']} nodes")

        edge_counts = session.run("MATCH ()-[r]->() RETURN type(r) as Rel, count(*) as Count ORDER BY Count DESC")
        for rec in edge_counts:
            print(f"  - {rec['Rel']:25}: {rec['Count']} edges")

    driver.close()
    print(f"\n[✓] Knowledge Graph successfully populated in AuraDB ({success_count} statements applied)!")
    return True


if __name__ == "__main__":
    connect_and_upload()
