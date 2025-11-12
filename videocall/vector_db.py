# videocall/vector_db.py
import sqlite3
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.conf import settings

class VectorDB:
    def __init__(self, db_path): #created table for storing vector
        self.db_path = db_path
        self._create_table()
        
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        return conn, conn.cursor()
        
    def _create_table(self):
        conn, cursor = self._get_connection()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_vectors (
                session_id INTEGER PRIMARY KEY,
                vector TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
        finally:
            conn.close()
    
    def add_or_update_vector(self, session_id, vector): #stored vector as json 
        
        conn, cursor = self._get_connection()
        try:
            vector_str = json.dumps(vector.tolist())
            cursor.execute(
                """INSERT OR REPLACE INTO session_vectors (session_id, vector) 
                   VALUES (?, ?)""",
                (session_id, vector_str)
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_similar_sessions_with_scores(self, query_vector, top_k=10): #used cosine sim. to find similar session
        conn, cursor = self._get_connection()
        try:
            cursor.execute("SELECT session_id, vector FROM session_vectors")
            results = []
            query_vector = np.array(query_vector).reshape(1, -1)
            
            for row in cursor.fetchall():
                session_id, vector_str = row
                stored_vector = np.array(json.loads(vector_str))
                
            
                similarity = cosine_similarity(query_vector, stored_vector.reshape(1, -1))[0][0]
                
                # Only if similarity > 0
                if similarity > 0:
                    results.append((session_id, similarity))
            
            # result dinxa by similarity and return top K
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
        finally:
            conn.close()