import asyncpg
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.append(src_dir)

import DbContext
from IQuizRepository import IQuizRepository

class QuizRepository(IQuizRepository):
    async def get(self, user_id):
        results = await DbContext.pool.fetchrow(f"""select quiz_id from quiz_state
            where user_id = $1""", user_id)
        if results is not None:
            return results['quiz_id']
        else:
            return 0
    
    async def add(self, user_id, quiz_id):
        await DbContext.pool.execute("""
            INSERT INTO quiz_state(user_id, quiz_id, total_questions_count)
            VALUES($1, $2, 0)
            ON CONFLICT (user_id)
            DO UPDATE SET quiz_id = $2
        """, user_id, quiz_id)

    async def getAll(self):
        return await DbContext.pool.fetch(f"""select * from quiz order by id""")