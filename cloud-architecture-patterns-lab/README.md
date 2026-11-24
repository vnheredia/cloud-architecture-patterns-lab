# Cloud Architecture Patterns Lab

A beginner-friendly, single Python program that demonstrates 8 cloud architecture patterns and concepts from a menu.

## Requirements
- Python 3.8 or newer
- No third-party packages required

## Run
```bash
python cloud_lab.py
```
On Windows, if needed:
```bash
py cloud_lab.py
```

## Labs
1. Circuit Breaker
2. Retry
3. Timeout
4. Serverless / AWS Lambda and ECS (local simulation)
5. API Gateway, Load Balancer, Reverse Proxy (routing simulation)
6. Hub-and-Spoke (network topology simulation)
7. Lift-and-Shift (migration simulation)
8. Bastion Host (access-flow simulation)

## Important note
Labs 1-3 are behavioral demos in Python. Labs 4-8 are local educational simulations: they do not create AWS resources, Docker containers, VPCs, EC2 instances, SSH sessions, or incur AWS charges. They demonstrate the concepts and flow only. For a real AWS deployment, these would need separate configuration and evidence.

## Suggested evidence
Take screenshots of:
- The main menu
- Each lab's execution output
- The final successful/recovery result for Circuit Breaker and Retry
- Routing output for Lab 5
- The topology output for Lab 6
- The migration before/after for Lab 7
- The access flow for Lab 8
