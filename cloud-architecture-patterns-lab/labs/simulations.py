from datetime import datetime



def log(message, level="INFO"):
    stamp = datetime.now().strftime("%H:%M:%S")
    return {"time": stamp, "level": level, "message": message}


def as_int(params, name, default, minimum, maximum):
    try:
        value = int(params.get(name, default))
    except (ValueError, TypeError):
        raise ValueError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def as_bool(params, name, default=True):
    raw = params.get(name, str(default).lower())
    if isinstance(raw, bool):
        return raw
    if str(raw).lower() in ("true", "1", "yes"):
        return True
    if str(raw).lower() in ("false", "0", "no"):
        return False
    raise ValueError(f"{name} must be true or false")


def circuit(params):
    threshold = as_int(params, "failure_threshold", 3, 1, 5)
    probe_ok = as_bool(params, "probe_success", True)
    logs, fails = [], 0
    for n in range(1, threshold + 1):
        fails += 1
        logs.append(log(f"Request {n}: dependency returned simulated 503", "ERROR"))
    logs.append(log(f"Failure threshold ({threshold}) reached. Circuit transitions CLOSED → OPEN", "WARN"))
    logs.append(log("Request blocked: circuit is OPEN; dependency not called", "WARN"))
    logs.append(log("Recovery window elapsed. Circuit transitions OPEN → HALF-OPEN", "INFO"))
    if probe_ok:
        logs.append(log("Probe succeeded. Circuit transitions HALF-OPEN → CLOSED", "SUCCESS"))
        state, summary = "CLOSED", "Recovery probe succeeded; circuit closed and calls can flow."
    else:
        logs.append(log("Probe failed. Circuit transitions HALF-OPEN → OPEN", "ERROR"))
        state, summary = "OPEN", "Recovery probe failed; circuit remains open to protect the dependency."
    return {"summary": summary, "status": state, "metrics": {"failure_threshold": threshold, "state": state}, "logs": logs}


def retry(params):
    failures = as_int(params, "failures_before_success", 2, 0, 5)
    maximum = as_int(params, "max_attempts", 4, 1, 6)
    base = as_int(params, "base_delay", 1, 1, 4)
    logs, attempts, delay = [], 0, base
    success = False
    while attempts < maximum:
        attempts += 1
        if attempts <= failures:
            logs.append(log(f"Attempt {attempts}/{maximum}: transient failure", "WARN"))
            if attempts < maximum:
                logs.append(log(f"Scheduled retry delay: {delay}s (simulated, no real wait)"))
                delay *= 2
        else:
            logs.append(log(f"Attempt {attempts}/{maximum}: SUCCESS", "SUCCESS"))
            success = True
            break
    if not success:
        logs.append(log("Retry limit reached; operation failed", "ERROR"))
    summary = f"Succeeded on attempt {attempts}." if success else f"Failed after {attempts} attempts; retry limit reached."
    return {"summary": summary, "status": "SUCCESS" if success else "FAILED", "metrics": {"attempts": attempts, "max_attempts": maximum, "succeeded": success}, "logs": logs}


def timeout(params):
    limit = as_int(params, "timeout_ms", 2000, 500, 5000)
    fast = as_int(params, "fast_response_ms", 800, 100, 3000)
    slow = as_int(params, "slow_response_ms", 3500, 500, 8000)
    logs = []
    outcomes = []
    for name, duration in [("Service A", fast), ("Service B", slow)]:
        passed = duration <= limit
        logs.append(log(f"{name}: simulated response {duration}ms; timeout limit {limit}ms", "INFO"))
        logs.append(log(f"{name}: {'SUCCESS' if passed else 'TIMEOUT'}", "SUCCESS" if passed else "WARN"))
        outcomes.append({"service": name, "response_ms": duration, "result": "SUCCESS" if passed else "TIMEOUT"})
    success_count = sum(1 for o in outcomes if o["result"] == "SUCCESS")
    return {"summary": f"{success_count} of 2 requests completed within the timeout limit.", "status": "COMPLETED", "metrics": {"timeout_ms": limit, "completed": success_count, "timed_out": 2-success_count}, "logs": logs, "details": outcomes}


def compute(params):
    event = str(params.get("event_name", "order.created"))[:80] or "sample.event"
    tasks = as_int(params, "container_tasks", 2, 1, 5)
    logs = [log(f"Event received: {event}"), log("Lambda-like handler started", "INFO"), log("Handler processed event and returned simulated success", "SUCCESS")]
    logs.extend([log(f"ECS task {i} scheduled from container image cloud-lab:latest", "INFO") for i in range(1, tasks+1)])
    logs.append(log(f"Container service stable: {tasks} task(s) running", "SUCCESS"))
    return {"summary": "Event-driven function and container task scenarios completed locally.", "status": "COMPLETED", "metrics": {"event": event, "container_tasks": tasks, "execution_models": 2}, "logs": logs}


def routing(params):
    count = as_int(params, "request_count", 12, 3, 30)
    servers = as_int(params, "backend_count", 3, 2, 6)
    logs = [log("Client request enters API Gateway / reverse proxy simulation")]
    counts = {f"Backend {i}": 0 for i in range(1, servers+1)}
    for n in range(1, count+1):
        backend = f"Backend {(n-1) % servers + 1}"
        counts[backend] += 1
        logs.append(log(f"Request {n:02d} routed to {backend}"))
    logs.append(log("Request distribution completed", "SUCCESS"))
    return {"summary": f"Distributed {count} requests across {servers} backend servers using Round Robin.", "status": "COMPLETED", "metrics": {"requests": count, "backends": servers}, "logs": logs, "details": [{"server": k, "requests": v} for k,v in counts.items()]}


def hub(params):
    spokes = as_int(params, "spoke_count", 4, 2, 6)
    allow = as_bool(params, "allow_spoke_to_spoke", True)
    logs = [log("Hub network initialized", "SUCCESS")]
    for i in range(1, spokes+1):
        logs.append(log(f"Spoke {i} connected to central hub"))
    if allow:
        logs.append(log("Route Spoke 1 → Hub → Spoke 2 permitted", "SUCCESS"))
        summary = f"{spokes} spokes connected. Inter-spoke routing is allowed through the hub in this simulation."
        status = "CONNECTED"
    else:
        logs.append(log("Spoke 1 → Spoke 2 route denied by policy; hub attachment remains available", "WARN"))
        summary = f"{spokes} spokes connected to hub; spoke-to-spoke traffic is blocked by policy."
        status = "RESTRICTED"
    return {"summary": summary, "status": status, "metrics": {"spokes": spokes, "inter_spoke": "allowed" if allow else "blocked"}, "logs": logs}


def migration(params):
    count = as_int(params, "server_count", 3, 1, 8)
    valid = as_bool(params, "validation_pass", True)
    stages = ["Inventory and dependency discovery", "Cloud landing-zone readiness", "Replication / transfer", "Cutover to cloud", "Post-migration validation"]
    logs = [log(f"Migration plan created for {count} on-prem server(s)")]
    for stage in stages[:4]:
        logs.append(log(f"Stage: {stage} — COMPLETED", "SUCCESS"))
    if valid:
        logs.append(log("Post-migration validation passed; workload accepted in cloud", "SUCCESS"))
        logs.append(log("Migration status: COMPLETE", "SUCCESS"))
        status, summary = "COMPLETE", f"{count} simulated server(s) rehosted and validated."
    else:
        logs.append(log("Post-migration validation failed; rollback decision triggered", "ERROR"))
        logs.append(log("Migration status: ROLLBACK SIMULATED", "WARN"))
        status, summary = "ROLLBACK", "Validation failed; rollback path simulated. No actual resources were changed."
    return {"summary": summary, "status": status, "metrics": {"servers": count, "validation": "passed" if valid else "failed"}, "logs": logs}


def bastion(params):
    authorized = as_bool(params, "admin_authorized", True)
    direct = as_bool(params, "direct_access", False)
    logs = [log("Admin request received", "INFO")]
    if direct:
        logs.append(log("Direct connection to private server rejected by network policy", "WARN"))
    if authorized:
        logs.append(log("Admin identity validated at bastion", "SUCCESS"))
        logs.append(log("Bastion forwards controlled session to private server", "SUCCESS"))
        through, status = True, "ACCESS GRANTED"
    else:
        logs.append(log("Admin identity validation failed; session denied", "ERROR"))
        through, status = False, "ACCESS DENIED"
    summary = "Authorized session reached private server through bastion." if through else "Session denied; private server remains inaccessible."
    return {"summary": summary, "status": status, "metrics": {"authorized": authorized, "direct_access_attempted": direct, "private_server_reached": through}, "logs": logs}



SIMULATIONS = {1: circuit, 2: retry, 3: timeout, 4: compute, 5: routing, 6: hub, 7: migration, 8: bastion}

def run_lab(lab_id, params):
    if lab_id not in SIMULATIONS:
        raise ValueError("Unknown lab identifier")
    return SIMULATIONS[lab_id](params)
