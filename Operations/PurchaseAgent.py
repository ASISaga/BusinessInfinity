from PurposeDrivenAgent.PurposeDrivenAgent import PurposeDrivenAgent

purpose = """
Physics: Basic concepts of motion, force, and energy.
AI Research: Current trends and methodologies in artificial intelligence.
Education: Effective teaching strategies and methods for knowledge dissemination.
"""

class PurchaseAgent(PurposeDrivenAgent):
    def __init__(self, interval=5):
        super().__init__(purpose, interval)

    def specific_task(self):
        return "Purchase specific task"
