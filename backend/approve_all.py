"""Script to add missing variant for base question with 0 variants."""
import asyncio
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from app.database import connect_to_mongodb, get_database, close_mongodb_connection
from datetime import datetime

async def add_missing_variants():
    """Add variants for questions that have none."""
    await connect_to_mongodb()
    db = get_database()
    
    # Find base questions without variants
    base_questions = await db.base_questions.find().to_list(None)
    
    for bq in base_questions:
        bq_id = str(bq["_id"])
        
        # Check if this question has any variants
        variant_count = await db.question_variants.count_documents({"question_id": bq_id})
        
        if variant_count == 0:
            print(f"Adding variant for: {bq.get('description', 'No description')[:50]}...")
            
            # Create a default variant based on description
            variant_doc = {
                "question_id": bq_id,
                "question_text": bq.get("description", "What is the correct answer?"),
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "correct_index": 0,
                "approved": True,
                "is_ai_generated": False,
                "created_at": datetime.utcnow()
            }
            
            await db.question_variants.insert_one(variant_doc)
            print(f"  ✅ Created variant!")
    
    # Final count
    total = await db.question_variants.count_documents({"approved": True})
    print(f"\nTotal approved variants: {total}")
    
    await close_mongodb_connection()

if __name__ == "__main__":
    asyncio.run(add_missing_variants())
