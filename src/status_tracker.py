"""
Status tracking for segmentation tasks
Handles tracking of segmentation progress and user activities
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class StatusTracker:
    """Tracks segmentation task status and user activities"""

    def __init__(self, storage_path: str = "./status_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.status_file = self.storage_path / "segmentation_status.json"
        self.user_activities_file = self.storage_path / "user_activities.json"
        self.load_status()

    def load_status(self):
        """Load existing status data"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    self.status_data = json.load(f)
            except Exception:
                self.status_data = {}
        else:
            self.status_data = {}

        if self.user_activities_file.exists():
            try:
                with open(self.user_activities_file, 'r') as f:
                    self.user_activities = json.load(f)
            except Exception:
                self.user_activities = []
        else:
            self.user_activities = []

    def save_status(self):
        """Save status data to file"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.status_data, f, indent=2)
        except Exception as e:
            print(f"Error saving status: {e}")

    def save_user_activities(self):
        """Save user activities to file"""
        try:
            with open(self.user_activities_file, 'w') as f:
                json.dump(self.user_activities, f, indent=2)
        except Exception as e:
            print(f"Error saving user activities: {e}")

    def create_segmentation_task(self, task_id: str, patient_id: str,
                                series_uid: str, created_by: str) -> Dict:
        """
        Create a new segmentation task

        Args:
            task_id: Unique task identifier
            patient_id: Patient identifier
            series_uid: Series identifier
            created_by: User who created the task

        Returns:
            Task information dictionary
        """
        task_info = {
            'task_id': task_id,
            'patient_id': patient_id,
            'series_uid': series_uid,
            'created_by': created_by,
            'created_at': datetime.now().isoformat(),
            'status': 'created',
            'progress': 0,
            'last_updated': datetime.now().isoformat(),
            'annotations': [],
            'segments': []
        }

        self.status_data[task_id] = task_info
        self.save_status()
        self.log_user_activity('create_task', task_id, created_by)
        return task_info

    def update_task_status(self, task_id: str, status: str,
                          progress: int = None, updated_by: str = None) -> bool:
        """
        Update task status

        Args:
            task_id: Task identifier
            status: New status
            progress: Progress percentage
            updated_by: User who updated

        Returns:
            Success status
        """
        if task_id not in self.status_data:
            return False

        task = self.status_data[task_id]
        task['status'] = status
        task['last_updated'] = datetime.now().isoformat()

        if progress is not None:
            task['progress'] = max(0, min(100, progress))

        if updated_by:
            self.log_user_activity('update_task', task_id, updated_by)

        self.save_status()
        return True

    def add_annotation(self, task_id: str, annotation: Dict) -> bool:
        """
        Add an annotation to a task

        Args:
            task_id: Task identifier
            annotation: Annotation data

        Returns:
            Success status
        """
        if task_id not in self.status_data:
            return False

        task = self.status_data[task_id]
        annotation['timestamp'] = datetime.now().isoformat()
        task['annotations'].append(annotation)
        task['last_updated'] = datetime.now().isoformat()

        self.save_status()
        return True

    def add_segment(self, task_id: str, segment: Dict) -> bool:
        """
        Add a segment to a task

        Args:
            task_id: Task identifier
            segment: Segment data

        Returns:
            Success status
        """
        if task_id not in self.status_data:
            return False

        task = self.status_data[task_id]
        segment['timestamp'] = datetime.now().isoformat()
        task['segments'].append(segment)
        task['last_updated'] = datetime.now().isoformat()

        self.save_status()
        return True

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get status of a specific task

        Args:
            task_id: Task identifier

        Returns:
            Task status information or None
        """
        return self.status_data.get(task_id)

    def get_all_tasks(self) -> List[Dict]:
        """
        Get all tasks

        Returns:
            List of all tasks
        """
        return list(self.status_data.values())

    def get_user_tasks(self, user_id: str) -> List[Dict]:
        """
        Get tasks for a specific user

        Args:
            user_id: User identifier

        Returns:
            List of user's tasks
        """
        user_tasks = []
        for task in self.status_data.values():
            if task.get('created_by') == user_id:
                user_tasks.append(task)
        return user_tasks

    def log_user_activity(self, activity_type: str, task_id: str, user_id: str):
        """
        Log user activity

        Args:
            activity_type: Type of activity
            task_id: Task identifier
            user_id: User identifier
        """
        activity = {
            'activity_type': activity_type,
            'task_id': task_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        self.user_activities.append(activity)
        self.save_user_activities()

    def get_user_activities(self, user_id: str = None, limit: int = 100) -> List[Dict]:
        """
        Get user activities

        Args:
            user_id: User identifier (optional)
            limit: Maximum number of activities to return

        Returns:
            List of user activities
        """
        if user_id:
            activities = [a for a in self.user_activities if a['user_id'] == user_id]
        else:
            activities = self.user_activities

        return activities[-limit:]

    def get_task_statistics(self) -> Dict:
        """
        Get overall task statistics

        Returns:
            Statistics dictionary
        """
        total_tasks = len(self.status_data)
        completed_tasks = sum(1 for t in self.status_data.values() if t['status'] == 'completed')
        in_progress_tasks = sum(1 for t in self.status_data.values() if t['status'] == 'in_progress')
        created_tasks = sum(1 for t in self.status_data.values() if t['status'] == 'created')

        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'created_tasks': created_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }

    def reset_task(self, task_id: str) -> bool:
        """
        Reset a task to initial state

        Args:
            task_id: Task identifier

        Returns:
            Success status
        """
        if task_id not in self.status_data:
            return False

        task = self.status_data[task_id]
        task['status'] = 'created'
        task['progress'] = 0
        task['annotations'] = []
        task['segments'] = []
        task['last_updated'] = datetime.now().isoformat()

        self.save_status()
        self.log_user_activity('reset_task', task_id, 'system')
        return True