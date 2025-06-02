from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Connect to MySQL Database (Update Credentials if needed)
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Change if needed
    password="",  # Change if needed
    database="bellreminder_db"
)
cursor = db.cursor()

# Define Data Model
class Reminder(BaseModel):
    class_name: str
    time: str

# API Route to Add Reminder
@app.post("/add_reminder")
async def add_reminder(reminder: Reminder):
    print(f"Received: {reminder}")  # Debugging: Check if FastAPI gets data

    try:
        query = "INSERT INTO reminders (class_name, time) VALUES (%s, %s)"
        values = (reminder.class_name, reminder.time)
        cursor.execute(query, values)
        db.commit()
        
        print("Reminder successfully added to MySQL!")  # Debugging
        return {"message": "Reminder added successfully!"}
    
    except Exception as e:
        print("Error:", str(e))  # Debugging
        raise HTTPException(status_code=500, detail=str(e))
