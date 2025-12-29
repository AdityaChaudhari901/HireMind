"""
Seed script to populate the database with sample questions.
Run this after setting up the backend to have initial data for testing.

Usage:
    cd backend
    python seed_data.py
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# Sample questions by topic
SAMPLE_QUESTIONS = [
    # JavaScript Questions
    {
        "topic": "JavaScript",
        "difficulty": "Easy",
        "description": "Variable declarations and hoisting",
        "variants": [
            {
                "question_text": "What is the output of: console.log(typeof undefined)?",
                "options": ["undefined", "null", "object", "string"],
                "correct_index": 0
            },
            {
                "question_text": "When using typeof operator on undefined, what is returned?",
                "options": ["undefined", "null", "object", "string"],
                "correct_index": 0
            }
        ]
    },
    {
        "topic": "JavaScript",
        "difficulty": "Medium",
        "description": "Array methods and callbacks",
        "variants": [
            {
                "question_text": "Which array method creates a new array with elements that pass a test?",
                "options": ["map()", "filter()", "reduce()", "forEach()"],
                "correct_index": 1
            }
        ]
    },
    {
        "topic": "JavaScript",
        "difficulty": "Hard",
        "description": "Closures and scope",
        "variants": [
            {
                "question_text": "What is a closure in JavaScript?",
                "options": [
                    "A function that has access to variables from its outer scope",
                    "A function that returns another function",
                    "A function that is immediately invoked",
                    "A function that has no parameters"
                ],
                "correct_index": 0
            }
        ]
    },
    # Python Questions
    {
        "topic": "Python",
        "difficulty": "Easy",
        "description": "Data types and basic operations",
        "variants": [
            {
                "question_text": "What is the output of: print(type([]))?",
                "options": ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'set'>"],
                "correct_index": 0
            }
        ]
    },
    {
        "topic": "Python",
        "difficulty": "Medium",
        "description": "List comprehensions",
        "variants": [
            {
                "question_text": "What is the result of [x**2 for x in range(3)]?",
                "options": ["[0, 1, 4]", "[1, 2, 3]", "[1, 4, 9]", "[0, 1, 2]"],
                "correct_index": 0
            }
        ]
    },
    {
        "topic": "Python",
        "difficulty": "Hard",
        "description": "Decorators and higher-order functions",
        "variants": [
            {
                "question_text": "What does the @staticmethod decorator do?",
                "options": [
                    "Makes a method that doesn't receive self or cls",
                    "Makes a method that can only access class variables",
                    "Makes a method that cannot be overridden",
                    "Makes a method that runs at class definition time"
                ],
                "correct_index": 0
            }
        ]
    },
    # SQL Questions
    {
        "topic": "SQL",
        "difficulty": "Easy",
        "description": "Basic SELECT queries",
        "variants": [
            {
                "question_text": "Which SQL clause is used to filter rows?",
                "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
                "correct_index": 0
            }
        ]
    },
    {
        "topic": "SQL",
        "difficulty": "Medium",
        "description": "JOIN operations",
        "variants": [
            {
                "question_text": "Which JOIN returns all rows from both tables?",
                "options": ["FULL OUTER JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
                "correct_index": 0
            }
        ]
    },
    {
        "topic": "SQL",
        "difficulty": "Hard",
        "description": "Subqueries and CTEs",
        "variants": [
            {
                "question_text": "What does CTE stand for in SQL?",
                "options": [
                    "Common Table Expression",
                    "Computed Table Entity",
                    "Cascading Table Element",
                    "Conditional Table Expression"
                ],
                "correct_index": 0
            }
        ]
    },
    # Data Structures Questions
    {
        "topic": "Data Structures",
        "difficulty": "Easy",
        "description": "Stack operations",
        "variants": [
            {
                "question_text": "What is the time complexity of push operation in a stack?",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                "correct_index": 0
            }
        ]
    },
    {
        "topic": "Data Structures",
        "difficulty": "Medium",
        "description": "Binary search trees",
        "variants": [
            {
                "question_text": "What is the average time complexity for search in a balanced BST?",
                "options": ["O(log n)", "O(n)", "O(1)", "O(n log n)"],
                "correct_index": 0
            }
        ]
    },
    {
        "topic": "Data Structures",
        "difficulty": "Hard",
        "description": "Graph algorithms",
        "variants": [
            {
                "question_text": "Which algorithm finds the shortest path in a weighted graph?",
                "options": ["Dijkstra's", "BFS", "DFS", "Topological Sort"],
                "correct_index": 0
            }
        ]
    },
]


async def seed_database():
    """Seed the database with sample questions."""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME]
    
    print("Connecting to MongoDB...")
    
    # Check if already seeded
    existing = await db.base_questions.count_documents({})
    if existing > 0:
        print(f"Database already has {existing} base questions. Skipping seed.")
        return
    
    print("Seeding database with sample questions...")
    
    for q in SAMPLE_QUESTIONS:
        # Create base question
        base_doc = {
            "topic": q["topic"],
            "difficulty": q["difficulty"],
            "description": q["description"],
            "created_at": datetime.utcnow(),
            "created_by": "seed_script"
        }
        
        result = await db.base_questions.insert_one(base_doc)
        base_id = str(result.inserted_id)
        
        # Create variants
        for variant in q["variants"]:
            variant_doc = {
                "question_id": base_id,
                "question_text": variant["question_text"],
                "options": variant["options"],
                "correct_answer": variant["options"][variant["correct_index"]],
                "correct_index": variant["correct_index"],
                "approved": True,
                "is_ai_generated": False,
                "created_at": datetime.utcnow()
            }
            await db.question_variants.insert_one(variant_doc)
        
        print(f"  Added: {q['topic']} - {q['difficulty']}")
    
    total_base = await db.base_questions.count_documents({})
    total_variants = await db.question_variants.count_documents({})
    
    print(f"\nSeeding complete!")
    print(f"  Base questions: {total_base}")
    print(f"  Variants: {total_variants}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
