from flask import Flask, jsonify, render_template

app = Flask(__name__)

LABS = [
    (1, "Circuit Breaker", "Resilience", "⚡", "Protect a service from repeated failures by opening the circuit."),
    (2, "Retry Pattern", "Resilience", "🔁", "Retry temporary failures until success or a maximum attempt count."),
    (3, "Timeout Pattern", "Resilience", "⏱️", "Stop waiting when an operation exceeds its allowed duration."),
    (4, "Serverless & Containers", "AWS", "☁️", "Compare event-driven Lambda execution with an ECS container task."),
    (5, "Gateway, Load Balancer & Proxy", "Traffic", "🔀", "Route requests to backends and distribute traffic between instances."),
    (6, "Hub-and-Spoke", "Networking", "🕸️", "Connect several networks through a central hub."),
    (7, "Lift-and-Shift", "Migration", "🚚", "Move an application to cloud with minimal changes."),
    (8, "Bastion Host", "Security", "🛡️", "Reach a private server through an authenticated jump host."),
]


def execute(n):
    outputs = {
        1: (
            "Circuit breaker protected the failing service and returned to CLOSED after recovery.",
            [
                "Payment service initially unavailable.",
                "Request 1 failed.",
                "Request 2 failed.",
                "Request 3 failed.",
                "Failure threshold reached: circuit OPEN.",
                "Next requests are blocked.",
                "Recovery test succeeded: circuit CLOSED.",
            ],
        ),
        2: (
            "Retry recovered from temporary failures on the third attempt.",
            [
                "Attempt 1: temporary failure.",
                "Waiting before retry...",
                "Attempt 2: temporary failure.",
                "Waiting before retry...",
                "Attempt 3: success.",
            ],
        ),
        3: (
            "Timeout behavior demonstrated. This is a local demonstration, not cancellation of a real remote request.",
            [
                "Request started.",
                "Timeout configured: 1.0 second.",
                "Simulated service duration: 2.5 seconds.",
                "Timeout reached: client stops waiting.",
            ],
        ),
        4: (
            "Lambda event execution and an ECS-style container task were simulated locally; no AWS resources were created.",
            [
                "Lambda simulation: event received.",
                "Function executed: greeting generated.",
                "Result: Hello, Student!",
                "ECS simulation: task definition loaded.",
                "Container task status: RUNNING.",
                "Container response: Hello from ECS demo.",
            ],
        ),
        5: (
            "Routing and round-robin distribution demonstrated locally. No external gateway or proxy was deployed.",
            [
                "Incoming request: /users -> User backend.",
                "Incoming request: /orders -> Order backend.",
                "Load balancer: request 1 -> Web-1.",
                "Load balancer: request 2 -> Web-2.",
                "Load balancer: request 3 -> Web-1.",
                "Load balancer: request 4 -> Web-2.",
            ],
        ),
        6: (
            "Hub-and-Spoke topology simulated. No virtual networks or route tables were created.",
            [
                "Hub: Central Network.",
                "Spoke-1: Application Network connected to Hub.",
                "Spoke-2: Database Network connected to Hub.",
                "Spoke-3: Monitoring Network connected to Hub.",
                "Traffic is represented as passing through the central Hub.",
            ],
        ),
        7: (
            "Lift-and-Shift migration represented by copying application configuration with minimal changes.",
            [
                "Source environment: On-Premises.",
                "Application: Demo Web App | Python 1.0 | Port 8080.",
                "Copying configuration to destination...",
                "Destination environment: AWS EC2 (simulated).",
                "Application configuration preserved.",
            ],
        ),
        8: (
            "Bastion access flow simulated. No SSH session or cloud network was created.",
            [
                "Administrator requests access.",
                "Authentication: SUCCESS.",
                "Connecting to public-subnet Bastion Host...",
                "Bastion forwards administrative connection to private server.",
                "Private server is not directly exposed to the internet.",
                "Connection simulation: SUCCESS.",
            ],
        ),
    }
    return outputs.get(n)


@app.route("/")
def home():
    return render_template("index.html", labs=LABS)


@app.post("/api/lab/<int:lab_id>")
def run_lab(lab_id):
    data = execute(lab_id)
    if data is None:
        return jsonify(error="Unknown lab"), 404
    result, logs = data
    return jsonify(result=result, logs=logs, simulation=lab_id >= 3)


if __name__ == "__main__":
    app.run(debug=True)