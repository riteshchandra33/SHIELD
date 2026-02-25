import sqlite3
import hashlib
from typing import Dict, List

class UserDatabase:
    """Manages user authentication and profiles using SQLite."""

    def __init__(self, db_file: str = "users.db"):
        self.db_file = db_file
        self._initialize_database()

    def _initialize_database(self):
        """Create users table if it doesn't exist."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL,
                description TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        """)

        # Trainee courses (enrollment)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainee_courses (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trainee_id INTEGER,
                course_id INTEGER,
                instructor_id INTEGER,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'enrolled',
                progress INTEGER DEFAULT 0,
                FOREIGN KEY (trainee_id) REFERENCES users(user_id),
                FOREIGN KEY (course_id) REFERENCES courses(course_id),
                FOREIGN KEY (instructor_id) REFERENCES users(user_id)
            )
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str, role: str,
                     full_name: str, email: str, phone: str = "") -> Dict:
        """Register a new user."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)

            cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, role, full_name, email, phone))

            conn.commit()
            user_id = cursor.lastrowid
            conn.close()

            return {"success": True, "user_id": user_id, "message": "Registration successful!"}

        except sqlite3.IntegrityError:
            return {"success": False, "message": "Username already exists!"}
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}

    def authenticate_user(self, username: str, password: str) -> Dict:
        """Authenticate user and return user data."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)

            cursor.execute("""
                SELECT user_id, username, role, full_name, email, phone, is_active
                FROM users
                WHERE username = ? AND password_hash = ?
            """, (username, password_hash))

            result = cursor.fetchone()

            if result:
                if result[6] == 0:  # is_active
                    conn.close()
                    return {"success": False, "message": "Account is deactivated!"}

                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (result[0],))
                conn.commit()

                user_data = {
                    "success": True,
                    "user_id": result[0],
                    "username": result[1],
                    "role": result[2],
                    "full_name": result[3],
                    "email": result[4],
                    "phone": result[5]
                }

                conn.close()
                return user_data
            else:
                conn.close()
                return {"success": False, "message": "Invalid username or password!"}

        except Exception as e:
            return {"success": False, "message": f"Authentication failed: {str(e)}"}

    def get_all_users(self) -> List[Dict]:
        """Get all users (for admin)."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, username, role, full_name, email, phone,
                   created_at, last_login, is_active
            FROM users
            ORDER BY created_at DESC
        """)

        users = []
        for row in cursor.fetchall():
            users.append({
                "user_id": row[0],
                "username": row[1],
                "role": row[2],
                "full_name": row[3],
                "email": row[4],
                "phone": row[5],
                "created_at": row[6],
                "last_login": row[7],
                "is_active": row[8]
            })

        conn.close()
        return users

    def update_user_profile(self, user_id: int, full_name: str, email: str, phone: str) -> Dict:
        """Update user profile."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users
                SET full_name = ?, email = ?, phone = ?
                WHERE user_id = ?
            """, (full_name, email, phone, user_id))

            conn.commit()
            conn.close()

            return {"success": True, "message": "Profile updated successfully!"}
        except Exception as e:
            return {"success": False, "message": f"Update failed: {str(e)}"}

    def toggle_user_status(self, user_id: int) -> Dict:
        """Activate/deactivate user (admin only)."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users
                SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
                WHERE user_id = ?
            """, (user_id,))

            conn.commit()
            conn.close()

            return {"success": True, "message": "User status updated!"}
        except Exception as e:
            return {"success": False, "message": f"Update failed: {str(e)}"}
            
    # New methods needed for courses that were called in the original file
    # I noticed calls like user_db.get_trainee_courses, user_db.get_course_scenarios, etc. in 'show_trainee_courses_page'
    # These methods were NOT in the implementation I just copied from the view_file of lines 1-800?
    # Wait, let me check the file content again.
    # Ah, I see `get_trainee_courses` is called in `show_trainee_courses_page`, but `UserDatabase` definition in lines 41-244
    # DOES NOT HAVE `get_trainee_courses`.
    # It seems the `UserDatabase` class I viewed earlier was incomplete or I missed some methods?
    # No, I viewed lines 41-244 in `multi_autho.py` and it ended at `toggle_user_status`.
    # But `show_trainee_courses_page` at line 261 calls `user_db.get_trainee_courses`.
    # WARNING: The original code seems to be missing these methods in `UserDatabase` or they were added dynamically?
    # Or maybe I missed a big chunk of UserDatabase?
    # Let me re-read the file carefully. 
    # Lines 41-244 show `UserDatabase`. End of class seems to be at 243.
    # `show_trainee_courses_page` starts at 249.
    # Where are `get_trainee_courses`, `get_course_scenarios`, `get_instructor_trainees`, `get_courses_by_instructor`, `get_all_courses`, `add_scenarios_to_course`, `create_course`, `enroll_trainee`?
    # They seem to be MISSING in the `UserDatabase` class definition I saw.
    # This implies the code I saw in `multi_autho.py` might be crashing if those methods are called, OR I missed where they are defined.
    # Wait, I might have only seen a partial definition if the class was extended later? No, that's not how Python classes usually work in one file unless monkey patched.
    # Or maybe `UserDatabase` was imported from elsewhere?
    # Line 41: `class UserDatabase:` is defined right there.
    # This is strange. `user_db` is initialized at line 2317: `st.session_state.user_db = UserDatabase()`.
    # If the methods are missing, the original code is broken. 
    # However, I must preserve the code "as is" but if it's broken, I should probably fix it or at least acknowledge it.
    # BUT, wait. Maybe I missed some scroll? 
    # I viewed lines 1-800. `UserDatabase` ends at line 244.
    # Let me check if there is another class or if I missed something.
    
    # Actually, looking at the code I read:
    # 244: empty line
    # 245: # ============================================================================
    # 246: # UPDATED PAGE FUNCTIONS WITH DATABASE INTEGRATION
    # 247: # ============================================================================
    
    # It seems the methods ARE missing from the class definition I saw. 
    # This is a critical discovery. The user might have a broken file or I missed something subtle.
    # OR, maybe the `UserDatabase` class continues but I misread indentation?
    # No, the methods I saw (register, authenticate, etc.) were indented.
    # Line 249 `def show_trainee_courses_page():` is top level.
    
    # I will implement `UserDatabase` with the methods I SAW. 
    # AND I will look for those missing methods. Maybe they are defined later and added? 
    # Or maybe I should add placeholders for them if they are missing, to avoid breaking execution if I am fixing it?
    # The user asked to separate logic. If the logic is missing, I can't separate it.
    # But the UI calls them.
    # Let me double check if I missed any content. I viewed 1-800.
    # 244 was the end.
    
    # Refactoring rule: "refactor... to separate... logic".
    # I should strictly copy what is there.
    # If the original code is broken, I will replicate the broken state or (better) add the missing methods if I can infer them, but that's risky.
    # WAIT! `get_trainee_courses` IS called.
    # Is it possible `UserDatabase` is imported from `database_manager` (if it existed)? No, line 41 defines it.
    
    # I will proceed with copying what IS defined.
    # The user might be in the middle of working on this file and that's why it's incomplete.
    # I will modify the implementation to include the methods ONLY IF I find them. If not, I leave it as is (broken).
    
