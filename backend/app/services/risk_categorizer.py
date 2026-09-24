from ..models.enums import RiskLevel

class RiskCategorizer:
    def categorize(self, svi_result: dict) -> dict:
        risk_level = svi_result.get("risk_level", RiskLevel.LOW)
        
        if risk_level == RiskLevel.LOW:
            return {
                "risk_level": RiskLevel.LOW,
                "color": "green",
                "response_sla": "72 hours",
                "description": "Standard processing",
                "priority_rank": 4
            }
        elif risk_level == RiskLevel.MODERATE:
            return {
                "risk_level": RiskLevel.MODERATE,
                "color": "yellow",
                "response_sla": "24 hours",
                "description": "Priority processing",
                "priority_rank": 3
            }
        elif risk_level == RiskLevel.HIGH:
            return {
                "risk_level": RiskLevel.HIGH,
                "color": "red",
                "response_sla": "4 hours",
                "description": "Urgent \u2014 counselling + legal aid required",
                "priority_rank": 2
            }
        else:
            return {
                "risk_level": RiskLevel.CRITICAL,
                "color": "black",
                "response_sla": "Immediate",
                "description": "Emergency \u2014 all support systems activated",
                "priority_rank": 1
            }
