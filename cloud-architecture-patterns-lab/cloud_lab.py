"""
Cloud Architecture Patterns Lab
A single-menu educational demo of 8 cloud patterns and concepts.
Some AWS/network labs are LOCAL SIMULATIONS, not real AWS deployments.
Run: python cloud_lab.py
"""

import random
import time


def pause():
    input("\nPress Enter to return to the menu...")


def title(name):
    print("\n" + "=" * 62)
    print(f"  {name}")
    print("=" * 62)


# 1. Circuit Breaker
def circuit_breaker():
    title("1. CIRCUIT BREAKER")
    failures = 0
    threshold = 3
    state = "CLOSED"
    service_up = False

    print("Service initially unavailable. Threshold = 3 failures.")
    for request in range(1, 5):
        print(f"\nRequest {request}: state={state}")
        if state == "OPEN":
            print("Blocked: circuit is OPEN. Request is not sent.")
            continue
        if service_up:
            print("Service responded successfully.")
            failures = 0
            state = "CLOSED"
        else:
            print("Service error: unavailable.")
            failures += 1
            if failures >= threshold:
                state = "OPEN"
                print("Threshold reached. Circuit changes to OPEN.")

    print("\nWaiting briefly, then testing recovery (HALF-OPEN)...")
    time.sleep(2)
    state = "HALF-OPEN"
    service_up = True
    print("Trial request: service is now available.")
    state = "CLOSED"
    failures = 0
    print("Successful test. Circuit CLOSED; normal requests resume.")
    print(f"Final state: {state}")


# 2. Retry
def retry_pattern():
    title("2. RETRY PATTERN")
    max_attempts = 4
    failures_before_success = 2

    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts}...")
        if attempt <= failures_before_success:
            print("Temporary error. Retrying...")
            time.sleep(0.6)
        else:
            print("Success! Response received.")
            break
    else:
        print("All attempts failed. Giving up.")


# 3. Timeout (demonstration)
def timeout_pattern():
    title("3. TIMEOUT PATTERN")
    timeout_seconds = 1.0
    simulated_operation_seconds = 2.5
    print(f"Operation simulated duration: {simulated_operation_seconds:.1f}s")
    print(f"Configured timeout: {timeout_seconds:.1f}s")
    print("Waiting up to the timeout...")
    time.sleep(timeout_seconds)
    print("TIMEOUT: stopped waiting after 1 second.")
    print("(Educational simulation: the demo does not cancel a real remote request.)")


# 4. Lambda & ECS
def serverless_containers():
    title("4. SERVERLESS (LAMBDA) & CONTAINERS (ECS)")
    event = {"name": "Student", "action": "hello"}

    def lambda_function(event_data):
        return {"statusCode": 200, "message": f"Hello, {event_data['name']}! Lambda processed this event."}

    print("AWS Lambda simulation: event arrives -> function runs -> response")
    print("Event:", event)
    print("Lambda result:", lambda_function(event))
    print("\nAmazon ECS simulation: container task starts and serves a request.")
    print("Container image: demo-web:1.0")
    print("Task status: RUNNING")
    print("Response: Hello from a container managed by ECS!")
    print("(Local simulation only; no AWS resources were created.)")


# 5. Gateway, load balancer, reverse proxy
def gateway_proxy():
    title("5. API GATEWAY, LOAD BALANCER & REVERSE PROXY")
    services = ["Backend-A", "Backend-B"]
    print("Incoming requests arrive at the proxy/router.")
    print("Routes: /users -> Backend-A | /orders -> Backend-B")
    paths = ["/users", "/orders", "/users", "/orders"]
    next_backend = 0

    for path in paths:
        if path == "/users":
            backend = services[0]
        elif path == "/orders":
            backend = services[1]
        else:
            backend = "404"
        print(f"Request {path} routed to {backend}")

    print("\nLoad Balancer demo: round-robin across two backend instances.")
    instances = ["Web-1", "Web-2"]
    for request in range(1, 7):
        chosen = instances[(request - 1) % len(instances)]
        print(f"Request {request} -> {chosen}")


# 6. Hub-and-Spoke
def hub_spoke():
    title("6. HUB-AND-SPOKE ARCHITECTURE")
    hub = "HUB (central network)"
    spokes = ["Spoke-1 (App network)", "Spoke-2 (Database network)", "Spoke-3 (Monitoring network)"]
    print(hub)
    for spoke in spokes:
        print(f"  |---- connection ----> {spoke}")
    print("\nTraffic between spokes is shown as passing through the Hub.")
    print("This is a topology simulation; no virtual networks were created.")


# 7. Lift-and-Shift
def lift_shift():
    title("7. LIFT-AND-SHIFT MIGRATION")
    app = {
        "name": "Demo Web App",
        "runtime": "Python",
        "version": "1.0",
        "port": 8080,
        "config": "basic"
    }
    print("SOURCE: On-Premise server")
    print("Application configuration:", app)
    print("\nMigration: copy the same application and configuration to cloud VM.")
    cloud_app = dict(app)
    cloud_app["environment"] = "AWS EC2 (simulated)"
    print("DESTINATION: AWS")
    print("Application configuration:", cloud_app)
    print("\nThe app is moved with minimal changes (lift-and-shift).")
    print("(Simulation only; no EC2 instance was launched.)")


# 8. Bastion
def bastion():
    title("8. BASTION HOST")
    print("User -> Bastion (public subnet) -> Private server (private subnet)")
    print("\nSimulating a connection request...")
    user_authenticated = True
    bastion_reachable = True
    private_server = "Private-Server-01"

    if user_authenticated and bastion_reachable:
        print("Access to Bastion: AUTHORIZED")
        print(f"Bastion forwards admin connection to {private_server}.")
        print("Private server is not directly exposed to the internet.")
        print("Result: simulated administrative access successful.")
    else:
        print("Access denied.")
    print("(Simulation only; no SSH session or cloud network was created.)")


LABS = {
    "1": ("Circuit Breaker", circuit_breaker),
    "2": ("Retry", retry_pattern),
    "3": ("Timeout", timeout_pattern),
    "4": ("Serverless / Lambda and ECS", serverless_containers),
    "5": ("API Gateway / Load Balancer / Reverse Proxy", gateway_proxy),
    "6": ("Hub-and-Spoke", hub_spoke),
    "7": ("Lift-and-Shift", lift_shift),
    "8": ("Bastion Host", bastion),
}


def main():
    while True:
        print("\n" + "=" * 62)
        print("           CLOUD ARCHITECTURE PATTERNS LAB")
        print("=" * 62)
        for key, (name, _) in LABS.items():
            print(f"{key}. {name}")
        print("0. Exit")

        choice = input("\nSelect a laboratory (0-8): ").strip()
        if choice == "0":
            print("Bye!")
            break
        if choice in LABS:
            LABS[choice][1]()
            pause()
        else:
            print("Invalid selection. Choose a number from 0 to 8.")


if __name__ == "__main__":
    main()
