import os
from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()

HOST = os.getenv("FALKORDB_HOST")
PORT = int(os.getenv("FALKORDB_PORT", "6379"))
USERNAME = os.getenv("FALKORDB_USERNAME")
PASSWORD = os.getenv("FALKORDB_PASSWORD")

print("Testing FalkorDB connection...")

db = FalkorDB(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    ssl=True,
)

graph = db.select_graph("benchmark")

print("FalkorDB connection successful!")
print("Graph selected successfully:", graph.name)