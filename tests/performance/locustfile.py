"""
Performance load tests for SpaceDock using Locust.

This file contains load test scenarios for the SpaceDock application.
"""

from locust import HttpUser, task, between


class ModUser(HttpUser):
    """User behavior for browsing and interacting with mods."""
    wait_time = between(1, 5)
    
    @task(3)
    def view_mods(self):
        """View the list of mods."""
        self.client.get("/mods")
    
    @task(2)
    def view_mod_details(self):
        """View details of a specific mod."""
        self.client.get("/mod/1")
    
    @task(1)
    def search_mods(self):
        """Search for mods."""
        self.client.get("/api/search/mod?query=test")
    
    @task(1)
    def browse_new_mods(self):
        """Browse new mods."""
        self.client.get("/api/browse/new")
    
    @task(1)
    def browse_top_mods(self):
        """Browse top mods."""
        self.client.get("/api/browse/top")


class UserProfile(HttpUser):
    """User behavior for profile-related actions."""
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login when the test starts."""
        self.client.post("/login", {
            "username": "testuser",
            "password": "password123"
        })
    
    @task(2)
    def view_profile(self):
        """View user profile."""
        self.client.get("/user/testuser")
    
    @task(1)
    def edit_profile(self):
        """Edit user profile."""
        self.client.post("/user/edit", {
            "username": "testuser",
            "email": "test@example.com",
            "description": "Updated description"
        })
    
    @task(1)
    def view_own_mods(self):
        """View user's own mods."""
        self.client.get("/user/testuser/mods")


class AdminUser(HttpUser):
    """Admin user behavior for administrative tasks."""
    wait_time = between(3, 7)
    
    def on_start(self):
        """Login as admin when the test starts."""
        self.client.post("/login", {
            "username": "admin",
            "password": "admin123"
        })
    
    @task(2)
    def view_admin_dashboard(self):
        """View admin dashboard."""
        self.client.get("/admin/dashboard")
    
    @task(1)
    def manage_users(self):
        """Manage users."""
        self.client.get("/admin/users")
    
    @task(1)
    def manage_mods(self):
        """Manage mods."""
        self.client.get("/admin/mods")
