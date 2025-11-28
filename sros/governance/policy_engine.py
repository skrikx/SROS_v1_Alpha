class PolicyResult:
    def __init__(self, allowed: bool, reason: str = ""):
        self.allowed = allowed
        self.reason = reason

class PolicyEngine:
    """
    Evaluates actions against active policies.
    """
    def __init__(self, mode: str = "strict"):
        self.mode = mode
        self.policies = []

    def load_policy(self, policy: dict):
        """
        Load a policy into the engine.
        """
        self.policies.append(policy)
        
    def evaluate(self, action: str, context: dict) -> PolicyResult:
        """
        Evaluate an action against loaded policies.
        """
        for policy in self.policies:
            if policy.get("effect") == "allow":
                return PolicyResult(allowed=True, reason="Policy allows")
        return PolicyResult(allowed=False, reason="No matching policy")

    def check(self, subject: str, action: str, resource: str) -> bool:
        """
        Returns True if allowed, False if denied.
        """
        print(f"Governance Check: {subject} wants to {action} on {resource}")
        
        # Default allow for prototype
        return True
