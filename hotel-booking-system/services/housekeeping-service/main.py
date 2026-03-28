from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Housekeeping Service",
    description="Manages room cleaning tasks and housekeeping schedules",
    version="1.0.0"
)

tasks_db = {}
counter = {"id": 1}

class TaskType(str, Enum):
    CLEANING = "cleaning"
    TURNDOWN = "turndown"
    INSPECTION = "inspection"
    MAINTENANCE = "maintenance"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class TaskCreate(BaseModel):
    room_id: int
    room_number: str
    task_type: TaskType
    assigned_to: str
    scheduled_date: str
    notes: Optional[str] = None

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[str] = None

class HousekeepingTask(TaskCreate):
    id: int
    status: TaskStatus = TaskStatus.PENDING
    completed_at: Optional[str] = None
    created_at: str

@app.get("/", tags=["Health"])
def health_check():
    return {"service": "Housekeeping Service", "status": "running", "port": 8005}

@app.get("/housekeeping", response_model=List[HousekeepingTask], tags=["Housekeeping"])
def get_all_tasks():
    """Retrieve all housekeeping tasks"""
    return list(tasks_db.values())

@app.get("/housekeeping/{task_id}", response_model=HousekeepingTask, tags=["Housekeeping"])
def get_task(task_id: int):
    """Retrieve a specific task by ID"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

@app.get("/housekeeping/room/{room_id}", response_model=List[HousekeepingTask], tags=["Housekeeping"])
def get_tasks_by_room(room_id: int):
    """Get all housekeeping tasks for a specific room"""
    return [t for t in tasks_db.values() if t.room_id == room_id]

@app.get("/housekeeping/staff/{staff_name}", response_model=List[HousekeepingTask], tags=["Housekeeping"])
def get_tasks_by_staff(staff_name: str):
    """Get all tasks assigned to a specific staff member"""
    return [t for t in tasks_db.values() if t.assigned_to.lower() == staff_name.lower()]

@app.post("/housekeeping", response_model=HousekeepingTask, status_code=201, tags=["Housekeeping"])
def create_task(task: TaskCreate):
    """Schedule a new housekeeping task"""
    task_id = counter["id"]
    new_task = HousekeepingTask(
        id=task_id,
        created_at=datetime.now().isoformat(),
        **task.dict()
    )
    tasks_db[task_id] = new_task
    counter["id"] += 1
    return new_task

@app.put("/housekeeping/{task_id}", response_model=HousekeepingTask, tags=["Housekeeping"])
def update_task(task_id: int, update: TaskUpdate):
    """Update task status or assignment"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task = tasks_db[task_id].dict()
    for key, value in update.dict(exclude_none=True).items():
        task[key] = value
    if update.status == TaskStatus.COMPLETED and not task.get("completed_at"):
        task["completed_at"] = datetime.now().isoformat()
    tasks_db[task_id] = HousekeepingTask(**task)
    return tasks_db[task_id]

@app.delete("/housekeeping/{task_id}", tags=["Housekeeping"])
def delete_task(task_id: int):
    """Remove a housekeeping task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"message": f"Task {task_id} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
