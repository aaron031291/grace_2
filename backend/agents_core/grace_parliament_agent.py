"""Grace Parliament Agent

Grace as an autonomous voting member of the Parliament system.
Uses reflection, causal reasoning, Hunter alerts, and verification history.
"""

from typing import Dict, Any

from .parliament_engine import parliament_engine
from .reflection import reflection_engine
from .causal_analyzer import causal_analyzer
from .verification import verification_engine


class GraceVotingAgent:
    """
    Grace as an autonomous parliament member
    
    Capabilities:
    - Automatic registration as parliament member
    - Analyze sessions using reflection + causal reasoning
    - Cast automated votes with confidence scoring
    - Use Hunter alerts for security votes
    - Use Verification history for trust votes
    - Use Causal reasoning for prediction votes
    - Use Meta-loop metrics for optimization votes
    """
    
    def __init__(self):
        self.member_id = "grace_parliament"
        self.display_name = "GRACE Parliament Agent"
        self.registered = False
    
    async def register(self):
        """Register Grace as a parliament member"""
        
        if self.registered:
            return
        
        try:
            await parliament_engine.create_member(
                member_id=self.member_id,
                member_type="grace_agent",
                display_name=self.display_name,
                role="member",
                committees=["security", "execution", "knowledge", "meta"],
                vote_weight=1.0
            )
            self.registered = True
            print(f"✓ Grace registered as parliament member: {self.member_id}")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e) or "already exists" in str(e).lower():
                self.registered = True
                print(f"✓ Grace already registered as parliament member")
            else:
                raise
    
    async def analyze_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a session and determine vote recommendation
        
        Args:
            session: Session details from parliament
        
        Returns:
            Analysis with vote recommendation and confidence
        """
        
        action_type = session.get("action_type")
        action_payload = session.get("action_payload", {})
        category = session.get("category")
        resource = session.get("resource")
        actor = session.get("actor")
        hunter_alerts = session.get("hunter_alerts", [])
        risk_level = session.get("risk_level", "medium")
        
        analysis = {
            "session_id": session["session_id"],
            "action_type": action_type,
            "category": category,
            "risk_level": risk_level,
            "factors": [],
            "vote_recommendation": "abstain",
            "confidence": 0.5,
            "reasoning": []
        }
        
        # Factor 1: Hunter security alerts
        if hunter_alerts:
            critical_alerts = sum(1 for a in hunter_alerts if a.get("severity") == "critical")
            high_alerts = sum(1 for a in hunter_alerts if a.get("severity") == "high")
            
            if critical_alerts > 0:
                analysis["factors"].append("critical_security_alerts")
                analysis["vote_recommendation"] = "reject"
                analysis["confidence"] = 0.95
                analysis["reasoning"].append(f"{critical_alerts} critical security alert(s) detected")
            elif high_alerts > 0:
                analysis["factors"].append("high_security_alerts")
                analysis["vote_recommendation"] = "reject"
                analysis["confidence"] = 0.80
                analysis["reasoning"].append(f"{high_alerts} high severity alert(s) detected")
        
        # Factor 2: Risk level assessment
        if risk_level == "critical" and analysis["vote_recommendation"] != "reject":
            analysis["factors"].append("critical_risk_level")
            analysis["vote_recommendation"] = "reject"
            analysis["confidence"] = max(analysis["confidence"], 0.75)
            analysis["reasoning"].append(f"Action marked as critical risk level")
        
        # Factor 3: Verification history (check if actor is trusted)
        if actor:
            try:
                actor_history = await verification_engine.get_actor_history(actor)
                if actor_history:
                    success_rate = actor_history.get("success_rate", 0.5)
                    
                    if success_rate > 0.9:
                        analysis["factors"].append("trusted_actor")
                        if analysis["vote_recommendation"] == "abstain":
                            analysis["vote_recommendation"] = "approve"
                        analysis["confidence"] = min(analysis["confidence"] + 0.1, 1.0)
                        analysis["reasoning"].append(f"Actor has {success_rate*100:.1f}% success rate")
                    elif success_rate < 0.5:
                        analysis["factors"].append("untrusted_actor")
                        analysis["vote_recommendation"] = "reject"
                        analysis["confidence"] = 0.70
                        analysis["reasoning"].append(f"Actor has low success rate: {success_rate*100:.1f}%")
            except:
                pass
        
        # Factor 4: Causal reasoning (predict outcome)
        if category and action_type:
            try:
                # Use causal analysis to predict outcomes
                prediction = await causal_analyzer.predict_outcome(
                    action_type=action_type,
                    context={
                        "category": category,
                        "resource": resource,
                        "risk_level": risk_level
                    }
                )
                
                if prediction:
                    predicted_success = prediction.get("success_probability", 0.5)
                    
                    if predicted_success > 0.8:
                        analysis["factors"].append("high_success_prediction")
                        if analysis["vote_recommendation"] == "abstain":
                            analysis["vote_recommendation"] = "approve"
                        analysis["confidence"] = min(analysis["confidence"] + 0.15, 1.0)
                        analysis["reasoning"].append(f"Causal analysis predicts {predicted_success*100:.1f}% success")
                    elif predicted_success < 0.3:
                        analysis["factors"].append("low_success_prediction")
                        analysis["vote_recommendation"] = "reject"
                        analysis["confidence"] = 0.75
                        analysis["reasoning"].append(f"Causal analysis predicts only {predicted_success*100:.1f}% success")
            except:
                pass
        
        # Factor 5: Reflection on similar past actions
        if action_type:
            try:
                # Get reflection on similar actions
                reflection = await reflection_engine.reflect_on_action(
                    action_type=action_type,
                    context=action_payload
                )
                
                if reflection:
                    lessons = reflection.get("lessons", [])
                    
                    for lesson in lessons:
                        if "fail" in lesson.lower() or "error" in lesson.lower():
                            analysis["factors"].append("negative_reflection")
                            if analysis["vote_recommendation"] == "approve":
                                analysis["vote_recommendation"] = "abstain"
                            analysis["confidence"] = max(analysis["confidence"] - 0.1, 0.3)
                            analysis["reasoning"].append(f"Past lesson: {lesson}")
                            break
                        elif "success" in lesson.lower() or "effective" in lesson.lower():
                            analysis["factors"].append("positive_reflection")
                            if analysis["vote_recommendation"] == "abstain":
                                analysis["vote_recommendation"] = "approve"
                            analysis["confidence"] = min(analysis["confidence"] + 0.1, 1.0)
                            analysis["reasoning"].append(f"Past lesson: {lesson}")
                            break
            except:
                pass
        
        # Default reasoning if none provided
        if not analysis["reasoning"]:
            analysis["reasoning"].append("Insufficient data for informed decision")
            analysis["vote_recommendation"] = "abstain"
            analysis["confidence"] = 0.5
        
        return analysis
    
    async def cast_automated_vote(self, session_id: str) -> Dict[str, Any]:
        """
        Automatically analyze and vote on a session
        
        Args:
            session_id: Session to vote on
        
        Returns:
            Vote result with analysis
        """
        
        # Ensure registered
        await self.register()
        
        # Get session details
        session = await parliament_engine.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Analyze session
        analysis = await self.analyze_session(session)
        
        # Cast vote
        vote_result = await parliament_engine.cast_vote(
            session_id=session_id,
            member_id=self.member_id,
            vote=analysis["vote_recommendation"],
            reason="; ".join(analysis["reasoning"]),
            automated=True,
            confidence=analysis["confidence"]
        )
        
        return {
            "vote_result": vote_result,
            "analysis": analysis
        }
    
    async def monitor_sessions(self, auto_vote: bool = True) -> Dict[str, Any]:
        """
        Monitor pending sessions and optionally auto-vote
        
        Args:
            auto_vote: Whether to automatically cast votes
        
        Returns:
            Summary of sessions and actions taken
        """
        
        await self.register()
        
        # Get pending sessions
        sessions = await parliament_engine.list_sessions(status="voting", limit=100)
        
        results = {
            "total_sessions": len(sessions),
            "voted": 0,
            "skipped": 0,
            "votes": []
        }
        
        for session_summary in sessions:
            session_id = session_summary["session_id"]
            
            # Get full session details
            session = await parliament_engine.get_session(session_id)
            
            # Check if Grace already voted
            grace_voted = any(
                v["member_id"] == self.member_id
                for v in session.get("votes", [])
            )
            
            if grace_voted:
                results["skipped"] += 1
                continue
            
            if auto_vote:
                try:
                    vote_result = await self.cast_automated_vote(session_id)
                    results["voted"] += 1
                    results["votes"].append({
                        "session_id": session_id,
                        "vote": vote_result["analysis"]["vote_recommendation"],
                        "confidence": vote_result["analysis"]["confidence"],
                        "reasoning": vote_result["analysis"]["reasoning"]
                    })
                except Exception as e:
                    results["skipped"] += 1
                    print(f"⚠️  Failed to vote on {session_id}: {e}")
            else:
                results["skipped"] += 1
        
        return results


# Singleton instance
grace_voting_agent = GraceVotingAgent()
