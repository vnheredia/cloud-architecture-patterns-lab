# Cloud Architecture Patterns Lab — Web Interface

A beginner-friendly Flask dashboard for running 8 educational cloud architecture demos.

## Run locally
1. Install Python 3.9+.
2. Open this folder in VS Code.
3. In terminal, create a virtual environment: `py -m venv venv`
4. Activate on Windows PowerShell: `.\venv\Scripts\Activate`
5. Install: `pip install -r requirements.txt`
6. Start: `python app.py`
7. Open the local address printed by Flask, usually `http://127.0.0.1:5000`.


## Labs
1. Circuit Breaker
2. Retry Pattern
3. Timeout Pattern
4. Serverless & Containers (Lambda / ECS)
5. Gateway, Load Balancer & Reverse Proxy
6. Hub-and-Spoke
7. Lift-and-Shift
8. Bastion Host

## Scope note
This is an educational interface. The demonstrations are local simulations and do not provision AWS resources. Lab 3 does not cancel a real request; it shows timeout behavior. AWS labs must be deployed separately to claim real cloud execution.
