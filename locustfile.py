from locust import HttpUser, task, between

class ChemsToolsUser(HttpUser):
    wait_time = between(1, 5) # Espera entre 1 y 5 segundos entre tareas

    def on_start(self):
        """Se ejecuta cuando un usuario simulado inicia."""
        # Simula el registro y login para obtener un token
        self.username = f"user_{self.environment.runner.user_count}"
        self.password = "password123"

        self.client.post("/api/auth/register/", json={
            "username": self.username,
            "password": self.password,
            "email": f"{self.username}@example.com"
        })

        res = self.client.post("/api/auth/token/", json={
            "username": self.username,
            "password": self.password
        })

        self.token = res.json()['access']
        self.client.headers['Authorization'] = f'Bearer {self.token}'

    @task(5) # Esta tarea se ejecutará 5 veces más que las otras
    def get_molecules(self):
        self.client.get("/api/molecules/")

    @task
    def create_molecule(self):
        self.client.post("/api/molecules/", json={
            "name": "Caffeine",
            "structure_data": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            "format": "SMILES"
        })
