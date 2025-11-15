"""
AI Agent Logic Module for AQI Monitoring
Powered by Google Gemini API for intelligent, personalized recommendations
Specialized for Delhi NCR Region with real-time AI analysis
"""

import os
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from datetime import datetime

# Google Gemini imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Warning: google-generativeai not installed. Install with: pip install google-generativeai")


# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Set your API key in environment
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class AQICategory(Enum):
    """AQI categories based on EPA standards with Delhi NCR extensions"""
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"
    SEVERE = "Severe"
    SEVERE_PLUS = "Severe+"


class RiskProfile(Enum):
    """User risk profiles for personalized recommendations"""
    GENERAL = "general"
    CHILDREN = "children"
    TEENS = "teens"
    PREGNANT = "pregnant"
    ELDERLY = "elderly"
    SENSITIVE = "sensitive"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"


def get_aqi_category(aqi_value: float) -> str:
    """Determine the AQI category based on EPA standards"""
    if aqi_value <= 50:
        return AQICategory.GOOD.value
    elif aqi_value <= 100:
        return AQICategory.MODERATE.value
    elif aqi_value <= 150:
        return AQICategory.UNHEALTHY_SENSITIVE.value
    elif aqi_value <= 200:
        return AQICategory.UNHEALTHY.value
    elif aqi_value <= 300:
        return AQICategory.VERY_UNHEALTHY.value
    elif aqi_value <= 400:
        return AQICategory.HAZARDOUS.value
    elif aqi_value <= 450:
        return AQICategory.SEVERE.value
    else:
        return AQICategory.SEVERE_PLUS.value


def determine_risk_profile(health_conditions: List[str]) -> str:
    """Determine user's risk profile based on health conditions"""
    if not health_conditions:
        return RiskProfile.GENERAL.value
    
    conditions_lower = [condition.lower().strip() for condition in health_conditions]
    
    # Critical conditions
    critical_conditions = {
        'transplant', 'organ transplant', 'immunocompromised', 'immune compromised',
        'chemotherapy', 'cancer treatment', 'hiv', 'aids', 'severe immunodeficiency'
    }
    
    # High-risk conditions
    high_risk_conditions = {
        'copd', 'chronic obstructive pulmonary', 'emphysema', 'severe asthma',
        'heart disease', 'cardiovascular disease', 'heart failure', 'cardiac',
        'lung cancer', 'pulmonary fibrosis'
    }
    
    # Sensitive conditions
    sensitive_conditions = {
        'asthma', 'mild asthma', 'allergies', 'bronchitis', 'sinus',
        'respiratory infection', 'allergy', 'breathing problem'
    }
    
    # Age and pregnancy markers
    children_markers = {'child', 'children', 'kid', 'infant', 'toddler', 'baby', 'under 12'}
    teen_markers = {'teen', 'teenager', 'adolescent', 'age 13-18', 'youth', 'student'}
    pregnant_markers = {'pregnant', 'pregnancy', 'expecting', 'expectant', 'prenatal'}
    elderly_markers = {'elderly', 'senior', 'old age', 'aged', '60+', 'over 60'}
    
    # Check conditions in priority order
    for condition in conditions_lower:
        for critical in critical_conditions:
            if critical in condition:
                return RiskProfile.CRITICAL.value
    
    for condition in conditions_lower:
        for pregnant in pregnant_markers:
            if pregnant in condition:
                return RiskProfile.PREGNANT.value
    
    for condition in conditions_lower:
        for child in children_markers:
            if child in condition:
                return RiskProfile.CHILDREN.value
    
    for condition in conditions_lower:
        for teen in teen_markers:
            if teen in condition:
                return RiskProfile.TEENS.value
    
    for condition in conditions_lower:
        for old in elderly_markers:
            if old in condition:
                return RiskProfile.ELDERLY.value
    
    for condition in conditions_lower:
        for high_risk in high_risk_conditions:
            if high_risk in condition:
                return RiskProfile.HIGH_RISK.value
    
    for condition in conditions_lower:
        for sensitive in sensitive_conditions:
            if sensitive in condition:
                return RiskProfile.SENSITIVE.value
    
    return RiskProfile.SENSITIVE.value if health_conditions else RiskProfile.GENERAL.value


def get_personalized_recommendation_with_gemini(
    aqi_value: float,
    user_health_conditions: Optional[List[str]] = None,
    location: str = "Delhi NCR"
) -> Dict[str, Any]:
    """
    Generate AI-powered personalized recommendations using Google Gemini
    
    Args:
        aqi_value: Current AQI value
        user_health_conditions: List of user's health conditions
        location: Location context (default: Delhi NCR)
        
    Returns:
        Dictionary containing AI-generated personalized recommendations
    """
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        # Fallback to rule-based system
        return get_personalized_recommendation(aqi_value, user_health_conditions)
    
    try:
        # Determine basic category and risk profile
        aqi_category = get_aqi_category(aqi_value)
        risk_profile = determine_risk_profile(user_health_conditions or [])
        
        # Prepare context for Gemini
        conditions_text = ", ".join(user_health_conditions) if user_health_conditions else "none reported"
        
        # Create the prompt for Gemini
        prompt = f"""You are an expert air quality health advisor specializing in Delhi NCR region.

Current Situation:
- AQI Level: {aqi_value} ({aqi_category})
- Location: {location}
- User Health Conditions: {conditions_text}
- Risk Profile: {risk_profile}

Please provide a comprehensive, personalized air quality advisory with the following structure:

1. SUMMARY (2-3 sentences)
   - Clear, non-panic-inducing assessment of the situation
   - Specific to the user's health profile

2. PRECAUTIONS (3-5 bullet points)
   - Specific protective measures
   - Health-specific advice based on conditions
   - Practical, actionable steps

3. RECOMMENDED ACTIVITIES (3-5 bullet points)
   - What the user can safely do
   - Indoor/outdoor activity guidance
   - Time-of-day recommendations if relevant

4. HEALTH IMPLICATIONS (2-3 sentences)
   - Clear explanation of health risks for this user
   - What symptoms to watch for
   - When to seek medical attention

5. DELHI-SPECIFIC CONTEXT (2-3 sentences)
   - Relevant local context (winter pollution, stubble burning, etc.)
   - Government measures typically in effect at this level
   - Local resources or tips

Important guidelines:
- Be informative but not alarmist
- Focus on actionable advice
- Consider Delhi NCR's unique air quality challenges
- Adapt tone based on severity: supportive for good/moderate, serious but calm for unhealthy/hazardous
- For vulnerable groups (children, pregnant, elderly, health conditions), be extra cautious but not panic-inducing

Format your response as valid JSON with these exact keys:
{{
    "summary": "string",
    "precautions": ["string", "string", ...],
    "recommended_activities": ["string", "string", ...],
    "health_implications": "string",
    "delhi_specific": "string"
}}"""

        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_output_tokens=1500,
            )
        )
        
        # Parse the response
        response_text = response.text.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        ai_recommendation = json.loads(response_text)
        
        # Build complete response
        return {
            "aqi_value": aqi_value,
            "aqi_category": aqi_category,
            "risk_profile": risk_profile,
            "health_conditions": user_health_conditions or [],
            "summary": ai_recommendation.get("summary", ""),
            "precautions": ai_recommendation.get("precautions", []),
            "recommended_activities": ai_recommendation.get("recommended_activities", []),
            "health_implications": ai_recommendation.get("health_implications", ""),
            "delhi_specific": ai_recommendation.get("delhi_specific", ""),
            "ai_powered": True,
            "model": "gemini-1.5-flash",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        # Fallback to rule-based system
        return get_personalized_recommendation(aqi_value, user_health_conditions)


def get_personalized_recommendation(
    aqi_value: float,
    user_health_conditions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Fallback rule-based recommendation system
    Used when Gemini API is not available
    """
    if user_health_conditions is None:
        user_health_conditions = []
    
    aqi_category = get_aqi_category(aqi_value)
    risk_profile = determine_risk_profile(user_health_conditions)
    
    # Basic rule-based recommendations
    recommendations = {
        "Good": {
            "summary": "Air quality is excellent! Perfect day to enjoy outdoor activities.",
            "precautions": ["Stay hydrated", "Keep a basic mask handy"],
            "recommended_activities": ["Outdoor exercise", "Park visits", "Sports activities"],
            "health_implications": "Air quality poses minimal risk.",
            "delhi_specific": "Make the most of this rare good air quality day in Delhi NCR."
        },
        "Moderate": {
            "summary": "Air quality is acceptable. Most people can go about normal activities.",
            "precautions": ["Watch for any symptoms", "Consider masks in heavy traffic"],
            "recommended_activities": ["Normal outdoor activities", "Moderate exercise"],
            "health_implications": "Air quality is acceptable for most people.",
            "delhi_specific": "This is better than average for Delhi NCR."
        },
        "Unhealthy for Sensitive Groups": {
            "summary": "Sensitive groups should take precautions. Others can continue normal activities with awareness.",
            "precautions": ["Wear mask when outdoors", "Use air purifiers", "Limit prolonged outdoor time"],
            "recommended_activities": ["Prefer indoor activities", "Short outdoor errands with mask"],
            "health_implications": "Sensitive groups will notice effects. General public may experience minor symptoms.",
            "delhi_specific": "Typical level for Delhi NCR. Masks and air purifiers become important."
        },
        "Unhealthy": {
            "summary": "Everyone affected. Stay indoors and use protection when going out.",
            "precautions": ["Wear N95 mask outdoors", "Keep windows closed", "Use air purifiers"],
            "recommended_activities": ["Stay indoors when possible", "Work from home if available"],
            "health_implications": "Everyone may experience health effects.",
            "delhi_specific": "Common during Delhi NCR winter season. Use protective measures consistently."
        },
        "Very Unhealthy": {
            "summary": "Health alert for everyone. Stay indoors with air filtration.",
            "precautions": ["Complete indoor isolation", "Multiple air purifiers", "N95 masks mandatory"],
            "recommended_activities": ["Indoor activities only", "Work from home", "Essential travel only"],
            "health_implications": "Everyone at increased risk. Serious effects for sensitive groups.",
            "delhi_specific": "Emergency level common during Delhi winter. Follow official guidelines."
        },
        "Hazardous": {
            "summary": "Health emergency. Everyone must stay indoors with air filtration.",
            "precautions": ["Seal windows", "Multiple air purifiers", "Complete indoor isolation"],
            "recommended_activities": ["Stay indoors", "No outdoor activities", "Follow emergency guidelines"],
            "health_implications": "Serious health effects for everyone.",
            "delhi_specific": "Emergency level requiring government action. Follow all official guidelines."
        }
    }
    
    rec = recommendations.get(aqi_category, recommendations["Moderate"])
    
    return {
        "aqi_value": aqi_value,
        "aqi_category": aqi_category,
        "risk_profile": risk_profile,
        "health_conditions": user_health_conditions,
        "summary": rec["summary"],
        "precautions": rec["precautions"],
        "recommended_activities": rec["recommended_activities"],
        "health_implications": rec["health_implications"],
        "delhi_specific": rec["delhi_specific"],
        "ai_powered": False,
        "timestamp": datetime.now().isoformat()
    }


def get_aqi_trend_advice(current_aqi: float, forecasted_aqi: List[float]) -> Dict[str, Any]:
    """
    Provide advice based on AQI trends using Gemini AI
    """
    if not forecasted_aqi:
        return {"trend": "unknown", "advice": "No forecast data available."}
    
    avg_forecast = sum(forecasted_aqi) / len(forecasted_aqi)
    max_forecast = max(forecasted_aqi)
    min_forecast = min(forecasted_aqi)
    
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        # Simple rule-based fallback
        if avg_forecast > current_aqi + 30:
            trend = "worsening"
            advice = f"Air quality expected to worsen. Peak AQI may reach {max_forecast:.0f}."
        elif avg_forecast < current_aqi - 30:
            trend = "improving"
            advice = f"Air quality expected to improve. Lowest AQI may be {min_forecast:.0f}."
        else:
            trend = "stable"
            advice = f"Air quality expected to remain similar around {avg_forecast:.0f}."
        
        return {
            "trend": trend,
            "current_aqi": current_aqi,
            "average_forecast": round(avg_forecast, 1),
            "max_forecast": round(max_forecast, 1),
            "min_forecast": round(min_forecast, 1),
            "advice": advice
        }
    
    try:
        # Use Gemini for trend analysis
        prompt = f"""Analyze this AQI trend data for Delhi NCR and provide brief, actionable advice:

Current AQI: {current_aqi}
Forecasted AQI (next 24 hours): {forecasted_aqi}
Average forecast: {avg_forecast:.1f}
Peak forecast: {max_forecast:.0f}
Lowest forecast: {min_forecast:.0f}

Provide a concise trend analysis (2-3 sentences) focusing on:
1. Whether air quality is improving, worsening, or staying stable
2. Best time windows for outdoor activities (if any)
3. Key precautions to take

Keep the tone informative and practical."""

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Determine trend
        if avg_forecast > current_aqi + 30:
            trend = "worsening"
        elif avg_forecast < current_aqi - 30:
            trend = "improving"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "current_aqi": current_aqi,
            "average_forecast": round(avg_forecast, 1),
            "max_forecast": round(max_forecast, 1),
            "min_forecast": round(min_forecast, 1),
            "advice": response.text.strip(),
            "ai_powered": True
        }
        
    except Exception as e:
        print(f"⚠️ Gemini trend analysis error: {e}")
        # Fallback to simple rule
        if avg_forecast > current_aqi + 30:
            advice = f"Air quality worsening. Peak may reach {max_forecast:.0f}."
        elif avg_forecast < current_aqi - 30:
            advice = f"Air quality improving. May drop to {min_forecast:.0f}."
        else:
            advice = f"Air quality stable around {avg_forecast:.0f}."
        
        return {
            "trend": "stable",
            "current_aqi": current_aqi,
            "average_forecast": round(avg_forecast, 1),
            "advice": advice,
            "ai_powered": False
        }


def get_delhi_specific_context(aqi_value: float, risk_profile: str) -> Dict[str, Any]:
    """
    Provide Delhi NCR-specific contextual information using Gemini
    """
    aqi_category = get_aqi_category(aqi_value)
    
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        # Basic fallback context
        return {
            "seasonal_context": "Delhi NCR experiences high pollution during winter months (Oct-Feb).",
            "government_measures": "GRAP measures may be in effect at this AQI level.",
            "local_tips": "Use N95 masks, air purifiers, and monitor AQI regularly."
        }
    
    try:
        # Use Gemini for context
        prompt = f"""Provide brief Delhi NCR-specific context for AQI {aqi_value} ({aqi_category}):

1. Current season considerations (1 sentence)
2. Typical government measures at this level (1 sentence)
3. One practical local tip for Delhi residents

Keep it concise and actionable. Format as plain text, 3 short paragraphs."""

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        context_text = response.text.strip()
        
        return {
            "seasonal_context": context_text,
            "government_measures": f"GRAP Stage measures typically active at AQI {aqi_value}",
            "local_tips": "Check AQI before outdoor activities, use N95 masks, and maintain air purifiers.",
            "ai_powered": True
        }
        
    except Exception as e:
        print(f"⚠️ Gemini context error: {e}")
        return {
            "seasonal_context": "Delhi NCR pollution varies by season, worst during winter months.",
            "government_measures": "Government restrictions may apply at this AQI level.",
            "local_tips": "Use protective measures and monitor air quality regularly.",
            "ai_powered": False
        }


# Convenience function that uses Gemini when available
def get_personalized_recommendation(
    aqi_value: float,
    user_health_conditions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Main entry point - uses Gemini if available, falls back to rules"""
    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        return get_personalized_recommendation_with_gemini(aqi_value, user_health_conditions)
    else:
        # Import and use the full rule-based system from original file
        # For now, using simplified version
        return get_personalized_recommendation(aqi_value, user_health_conditions)


if __name__ == "__main__":
    # Test the agent
    print("🤖 Testing AQI Agent with Gemini AI...")
    print(f"Gemini Available: {GEMINI_AVAILABLE}")
    print(f"API Key Set: {bool(GEMINI_API_KEY)}")
    
    # Test case
    test_aqi = 150
    test_conditions = ["asthma", "child"]
    
    print(f"\nTest: AQI {test_aqi}, Conditions: {test_conditions}")
    result = get_personalized_recommendation(test_aqi, test_conditions)
    
    print(f"\nCategory: {result['aqi_category']}")
    print(f"Risk Profile: {result['risk_profile']}")
    print(f"AI Powered: {result.get('ai_powered', False)}")
    print(f"\nSummary: {result['summary']}")
    print(f"\nPrecautions: {result['precautions']}")
