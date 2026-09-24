from ..models.enums import RiskLevel, InterventionType

class InterventionRecommender:
    def recommend(self, risk_level: str, svi_result: dict, text_analysis: dict | None = None) -> list[dict]:
        recommendations = []
        
        if risk_level == RiskLevel.LOW:
            recommendations.extend([
                {"intervention_type": InterventionType.INFORMATION, "priority": 4, "description": "Information on SC/ST Act rights", "action_details": "Provide rights info", "response_sla": "72 hours"},
                {"intervention_type": InterventionType.LEGAL, "priority": 4, "description": "Nearest legal aid center info", "action_details": "Share address and contact", "response_sla": "72 hours"},
                {"intervention_type": InterventionType.FOLLOWUP, "priority": 4, "description": "Follow-up call in 7 days", "action_details": "Schedule a follow-up call", "response_sla": "7 days"}
            ])
        elif risk_level == RiskLevel.MODERATE:
            recommendations.extend([
                {"intervention_type": InterventionType.COUNSELLING, "priority": 3, "description": "Telephonic counselling session", "action_details": "Connect to counsellor", "response_sla": "24 hours"},
                {"intervention_type": InterventionType.LEGAL, "priority": 3, "description": "Legal aid referral", "action_details": "Refer to lawyer", "response_sla": "24 hours"},
                {"intervention_type": InterventionType.ADMINISTRATION, "priority": 3, "description": "District administration notification", "action_details": "Send alert to DA", "response_sla": "24 hours"},
                {"intervention_type": InterventionType.FOLLOWUP, "priority": 3, "description": "Follow-up in 48 hours", "action_details": "Schedule follow-up", "response_sla": "48 hours"}
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                {"intervention_type": InterventionType.COUNSELLING, "priority": 2, "description": "Immediate counselling", "action_details": "Connect to crisis counsellor", "response_sla": "4 hours"},
                {"intervention_type": InterventionType.LEGAL, "priority": 2, "description": "FIR lodging support", "action_details": "Assist with FIR", "response_sla": "4 hours"},
                {"intervention_type": InterventionType.MEDICAL, "priority": 2, "description": "Medical assistance referral", "action_details": "Refer to hospital", "response_sla": "4 hours"},
                {"intervention_type": InterventionType.PROTECTION, "priority": 2, "description": "Witness protection assessment", "action_details": "Assess need for protection", "response_sla": "4 hours"},
                {"intervention_type": InterventionType.ADMINISTRATION, "priority": 2, "description": "District magistrate alert", "action_details": "Alert DM", "response_sla": "4 hours"}
            ])
        elif risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                {"intervention_type": InterventionType.POLICE, "priority": 1, "description": "Emergency police dispatch", "action_details": "Dispatch police", "response_sla": "Immediate"},
                {"intervention_type": InterventionType.COUNSELLING, "priority": 1, "description": "Crisis counselling", "action_details": "Immediate crisis intervention", "response_sla": "Immediate"},
                {"intervention_type": InterventionType.MEDICAL, "priority": 1, "description": "Hospital/medical team alert", "action_details": "Alert medical team", "response_sla": "Immediate"},
                {"intervention_type": InterventionType.PROTECTION, "priority": 1, "description": "Witness protection activation", "action_details": "Activate protection", "response_sla": "Immediate"},
                {"intervention_type": InterventionType.ADMINISTRATION, "priority": 1, "description": "State Commission notification", "action_details": "Notify State Commission", "response_sla": "Immediate"},
                {"intervention_type": InterventionType.REHABILITATION, "priority": 1, "description": "Rehabilitation support", "action_details": "Start rehab support", "response_sla": "Immediate"}
            ])
            
        if text_analysis and text_analysis.get("suicidal_ideation", {}).get("flag"):
            recommendations.insert(0, {
                "intervention_type": InterventionType.CRISIS,
                "priority": 0,
                "description": "Crisis suicide prevention counselling",
                "action_details": "Immediate suicide prevention protocol",
                "response_sla": "Immediate"
            })
            
        return recommendations
