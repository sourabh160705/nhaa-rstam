from ..models.enums import RiskLevel, InterventionType

class InterventionRecommender:
    def recommend(self, risk_level: str, svi_result: dict, text_analysis: dict | None = None) -> list[dict]:
        # ─── If LLM generated tailored case-specific recommendations, prioritize them ───
        if text_analysis and text_analysis.get("customized_recommendations"):
            llm_recs = text_analysis.get("customized_recommendations")
            mapped = []
            for r in llm_recs:
                mapped.append({
                    "intervention_type": r.get("intervention_type", InterventionType.LEGAL.value),
                    "priority": r.get("priority", 2),
                    "description": r.get("description", "Recommended Action"),
                    "action_details": r.get("action_details", ""),
                    "response_sla": r.get("response_sla", "Immediate" if risk_level == RiskLevel.CRITICAL else "24 hours")
                })
            if mapped:
                return sorted(mapped, key=lambda x: x["priority"])

        # ─── Standard Rule-Based Recommendations ───
        recommendations = []
        
        if risk_level == RiskLevel.LOW:
            recommendations.extend([
                {"intervention_type": InterventionType.INFORMATION, "priority": 4, "description": "Information on SC/ST Act rights", "action_details": "Provide rights info and legal awareness", "response_sla": "72 hours"},
                {"intervention_type": InterventionType.LEGAL, "priority": 4, "description": "Nearest legal aid center info", "action_details": "Share District Legal Services Authority (DLSA) contact", "response_sla": "72 hours"},
                {"intervention_type": InterventionType.FOLLOWUP, "priority": 4, "description": "Follow-up call in 7 days", "action_details": "Schedule a follow-up call to check grievance status", "response_sla": "7 days"}
            ])
        elif risk_level == RiskLevel.MODERATE:
            recommendations.extend([
                {"intervention_type": InterventionType.COUNSELLING, "priority": 3, "description": "Telephonic psychological counselling", "action_details": "Connect to psycho-social counsellor", "response_sla": "24 hours"},
                {"intervention_type": InterventionType.LEGAL, "priority": 3, "description": "Legal aid referral & advice", "action_details": "Refer to DLSA empaneled advocate for legal guidance", "response_sla": "24 hours"},
                {"intervention_type": InterventionType.ADMINISTRATION, "priority": 3, "description": "District administration notification", "action_details": "Send notification to Sub-Divisional Magistrate", "response_sla": "24 hours"},
                {"intervention_type": InterventionType.FOLLOWUP, "priority": 3, "description": "Follow-up in 48 hours", "action_details": "Schedule follow-up call", "response_sla": "48 hours"}
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                {"intervention_type": InterventionType.COUNSELLING, "priority": 2, "description": "Immediate crisis counselling", "action_details": "Warm transfer to Tier-2 crisis counsellor", "response_sla": "4 hours"},
                {"intervention_type": InterventionType.LEGAL, "priority": 2, "description": "FIR lodging & legal assistance", "action_details": "Assist complainant in registering FIR under SC/ST (PoA) Act", "response_sla": "4 hours"},
                {"intervention_type": InterventionType.MEDICAL, "priority": 2, "description": "Medical assistance & examination", "action_details": "Coordinate with District Hospital for medico-legal examination", "response_sla": "4 hours"},
                {"intervention_type": InterventionType.PROTECTION, "priority": 2, "description": "Witness & victim protection assessment", "action_details": "Assess immediate threat under Section 15A SC/ST PoA Act", "response_sla": "4 hours"},
                {"intervention_type": InterventionType.ADMINISTRATION, "priority": 2, "description": "District Magistrate & SP alert", "action_details": "Transmit distress alert to DM and Superintendent of Police", "response_sla": "4 hours"}
            ])
        elif risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                {"intervention_type": InterventionType.POLICE, "priority": 1, "description": "Emergency Police Control Room (PCR) dispatch", "action_details": "Dispatch nearest PCR vehicle to victim's location immediately", "response_sla": "Immediate (< 15 mins)"},
                {"intervention_type": InterventionType.COUNSELLING, "priority": 1, "description": "Emergency suicide / crisis intervention", "action_details": "Continuous call hold with specialized crisis counselor", "response_sla": "Immediate"},
                {"intervention_type": InterventionType.PROTECTION, "priority": 1, "description": "Immediate physical protection", "action_details": "Activate Witness Protection Scheme 2018 / Section 15A PoA Act", "response_sla": "Immediate"},
                {"intervention_type": InterventionType.MEDICAL, "priority": 1, "description": "Emergency ambulance dispatch", "action_details": "Dispatch emergency medical services to site", "response_sla": "Immediate"},
                {"intervention_type": InterventionType.ADMINISTRATION, "priority": 1, "description": "State SC/ST Commission escalation", "action_details": "Direct high-priority alert to State SC/ST Commission", "response_sla": "Immediate"}
            ])
            
        if text_analysis and text_analysis.get("suicidal_ideation", {}).get("flag"):
            recommendations.insert(0, {
                "intervention_type": InterventionType.CRISIS,
                "priority": 0,
                "description": "Critical Suicide Prevention Protocol",
                "action_details": "Immediate warm handoff to Tele-MANAS (14416) or suicide prevention specialist",
                "response_sla": "Immediate"
            })
            
        return recommendations
