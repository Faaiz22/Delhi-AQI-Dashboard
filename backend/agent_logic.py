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


# Try to get API key from multiple sources
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    try:
        import streamlit as st
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    except:
        pass

# Configure Gemini API
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini API configured successfully")
    except Exception as e:
        print(f"⚠️ Gemini API configuration failed: {e}")
        GEMINI_AVAILABLE = False


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
    location: str = "Delhi NCR",
    family_members: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate AI-powered personalized recommendations using Google Gemini
    Supports both individual and family-based recommendations
    """
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        print("⚠️ Gemini not available, using rule-based system")
        return get_rule_based_fallback(aqi_value, user_health_conditions, family_members)
    
    try:
        # Determine basic category and risk profile
        aqi_category = get_aqi_category(aqi_value)
        risk_profile = determine_risk_profile(user_health_conditions or [])
        
        # Prepare context for Gemini
        conditions_text = ", ".join(user_health_conditions) if user_health_conditions else "none reported"
        
        # Build family context if provided
        family_context = ""
        if family_members and len(family_members) > 0:
            family_context = "\n\nFamily Members:\n"
            for idx, member in enumerate(family_members, 1):
                name = member.get('name', f'Member {idx}')
                age = member.get('age', 'N/A')
                conditions = ', '.join(member.get('health_conditions', [])) if member.get('health_conditions') else 'none'
                family_context += f"- {name} (Age: {age}): Health Conditions: {conditions}\n"
        
        # Build the JSON template based on whether family is included
        if family_members:
            json_template = """{
    "summary": "string",
    "precautions": ["string", "string", ...],
    "recommended_activities": ["string", "string", ...],
    "health_implications": "string",
    "delhi_specific": "string",
    "family_specific": "string"
}"""
        else:
            json_template = """{
    "summary": "string",
    "precautions": ["string", "string", ...],
    "recommended_activities": ["string", "string", ...],
    "health_implications": "string",
    "delhi_specific": "string"
}"""
        
        # Create the prompt for Gemini
        prompt = f"""You are an expert air quality health advisor specializing in Delhi NCR region with deep knowledge of respiratory health and environmental medicine.

Current Situation:
- AQI Level: {aqi_value} ({aqi_category})
- Location: {location}
- Primary User Health Conditions: {conditions_text}
- Risk Profile: {risk_profile}{family_context}

Please provide a comprehensive, personalized air quality advisory. Your advice should be:
1. Medically accurate and evidence-based
2. Specific to each person's health profile
3. Practical and immediately actionable
4. Culturally appropriate for Delhi NCR residents
5. Clear without being alarmist

Structure your response as follows:

1. SUMMARY (3-4 sentences)
   - Clear assessment appropriate for this AQI level
   - Specific mention of risk for this user/family profile
   - Overall recommendation (stay indoors/outdoor OK with precautions/etc.)

2. IMMEDIATE PRECAUTIONS (4-6 specific actions)
   - Health-specific protective measures
   - Practical steps for Delhi NCR context
   - Equipment/supplies needed (masks, purifiers, etc.)
   - When to seek medical attention

3. RECOMMENDED ACTIVITIES (4-5 activities)
   - What can be safely done at this AQI level
   - Time-of-day recommendations
   - Indoor alternatives for usual outdoor activities
   - Exercise/commuting guidance

4. HEALTH IMPLICATIONS (3-4 sentences)
   - Specific health risks for this profile
   - Symptoms to watch for (short-term and long-term)
   - Why this AQI level matters for this person/family
   - Vulnerable periods (early morning, evening, etc.)

5. DELHI-SPECIFIC GUIDANCE (3-4 sentences)
   - Current seasonal context (stubble burning, winter inversion, etc.)
   - Typical government measures at this AQI level
   - Local resources (air purifier availability, mask types in local stores)
   - Comparison to typical Delhi AQI patterns

{"6. FAMILY-SPECIFIC GUIDANCE (if family members provided):" if family_members else ""}
{"- Individual recommendations for each family member based on their age and health" if family_members else ""}
{"- Special precautions for most vulnerable family members" if family_members else ""}
{"- Family activity suggestions suitable for all members" if family_members else ""}

Important: 
- Be specific about mask types (N95, N99, surgical)
- Include both short-term (today) and medium-term (this week) advice
- Mention specific times of day if relevant
- Reference Delhi landmarks/areas if helpful for context

Format your response as valid JSON with these exact keys:
{json_template}"""

        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000,
            )
        )
        
        # Parse the response
        response_text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        ai_recommendation = json.loads(response_text)
        
        # Build complete response
        result = {
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
        
        # Add family-specific guidance if available
        if family_members and "family_specific" in ai_recommendation:
            result["family_specific"] = ai_recommendation["family_specific"]
        
        return result
        
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return get_rule_based_fallback(aqi_value, user_health_conditions, family_members)


def get_rule_based_fallback(
    aqi_value: float, 
    user_health_conditions: Optional[List[str]] = None,
    family_members: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Enhanced fallback to rule-based system with family support"""
    if user_health_conditions is None:
        user_health_conditions = []
    
    aqi_category = get_aqi_category(aqi_value)
    risk_profile = determine_risk_profile(user_health_conditions)
    
    rec = get_rule_based_recommendation(aqi_value, risk_profile, aqi_category)
    
    result = {
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
    
    # Add basic family guidance if family members provided
    if family_members and len(family_members) > 0:
        family_guidance = generate_basic_family_guidance(family_members, aqi_category)
        result["family_specific"] = family_guidance
    
    return result


def generate_basic_family_guidance(family_members: List[Dict[str, Any]], aqi_category: str) -> str:
    """Generate basic family-specific guidance using rules"""
    vulnerable_members = []
    
    for member in family_members:
        age = member.get('age', 0)
        conditions = member.get('health_conditions', [])
        name = member.get('name', 'Family member')
        
        if age < 12 or age > 60 or len(conditions) > 0:
            vulnerable_members.append(name)
    
    if vulnerable_members:
        return f"Extra precautions recommended for: {', '.join(vulnerable_members)}. Ensure they have proper N95 masks and limit their outdoor exposure. Keep air purifiers running in their rooms."
    else:
        return "All family members should follow general precautions for this AQI level. Ensure adequate indoor air filtration and limit outdoor activities during peak pollution hours."


def get_rule_based_recommendation(aqi_value: float, risk_profile: str, aqi_category: str) -> Dict[str, Any]:
    """
    Fallback rule-based recommendation system
    """
    # Basic rule-based recommendations by category
    recommendations = {
        "Good": {
            "summary": "Air quality is excellent! Perfect day to enjoy outdoor activities.",
            "precautions": ["Stay hydrated", "Keep a basic mask handy as conditions can change"],
            "recommended_activities": ["Outdoor exercise", "Park visits", "Sports activities", "Morning walks"],
            "health_implications": "Air quality poses minimal risk. Feel free to enjoy outdoor activities.",
            "delhi_specific": "Make the most of this rare good air quality day in Delhi NCR. Conditions like this are uncommon during winter months."
        },
        "Moderate": {
            "summary": "Air quality is acceptable. Most people can go about normal activities.",
            "precautions": ["Watch for any symptoms", "Consider masks in heavy traffic", "Take normal breaks during extended outdoor work"],
            "recommended_activities": ["Normal outdoor activities", "Moderate exercise", "Regular commuting"],
            "health_implications": "Air quality is acceptable for most people.",
            "delhi_specific": "This is better than average for Delhi NCR. Normal activities can continue."
        },
        "Unhealthy for Sensitive Groups": {
            "summary": "Sensitive groups should take precautions. Others can continue with awareness.",
            "precautions": ["Wear mask when outdoors", "Use air purifiers indoors", "Limit prolonged outdoor time", "Watch for throat irritation"],
            "recommended_activities": ["Prefer indoor activities", "Short outdoor errands with mask", "Reduce strenuous activities"],
            "health_implications": "Sensitive groups will notice effects. General public may experience minor symptoms.",
            "delhi_specific": "Typical level for Delhi NCR. Masks and air purifiers become important at this stage."
        },
        "Unhealthy": {
            "summary": "Everyone affected. Stay indoors and use protection when going out.",
            "precautions": ["Wear N95 mask outdoors", "Keep windows closed", "Use air purifiers", "Avoid outdoor exercise"],
            "recommended_activities": ["Stay indoors when possible", "Work from home if available", "Indoor activities only"],
            "health_implications": "Everyone may experience health effects. Sensitive groups at higher risk.",
            "delhi_specific": "Common during Delhi NCR winter season. Government restrictions typically begin. Use protective measures consistently."
        },
        "Very Unhealthy": {
            "summary": "Health alert for everyone. Stay indoors with air filtration.",
            "precautions": ["Complete indoor isolation", "Multiple air purifiers essential", "N95 masks mandatory for any outdoor time", "Monitor health closely"],
            "recommended_activities": ["Indoor activities only", "Work from home mandatory", "Essential travel only with maximum protection"],
            "health_implications": "Everyone at increased risk. Serious effects for sensitive groups.",
            "delhi_specific": "Emergency level common during Delhi NCR winter. Government emergency measures typically active. Follow official guidelines."
        },
        "Hazardous": {
            "summary": "Health emergency. Everyone must stay indoors with air filtration.",
            "precautions": ["Seal windows and doors", "Multiple air purifiers essential", "Complete indoor isolation", "Medical consultation if symptoms worsen"],
            "recommended_activities": ["Stay indoors in protected environment", "No outdoor activities", "Follow all emergency guidelines"],
            "health_implications": "Serious health effects for everyone. Follow all emergency protocols.",
            "delhi_specific": "Emergency level requiring government action. GRAP Stage 4 typically active. Follow all official guidelines and stay protected."
        },
        "Severe": {
            "summary": "Severe health emergency. Maximum protection required for everyone.",
            "precautions": ["Maximum air filtration essential", "Complete indoor isolation", "Consider evacuation if possible", "Medical supervision recommended"],
            "recommended_activities": ["Protected indoor environment only", "No outdoor exposure", "Follow emergency directives"],
            "health_implications": "Severe emergency affecting everyone. Maximum protection essential.",
            "delhi_specific": "Rare but critical level for Delhi NCR. Full emergency measures in effect. Follow all government directives."
        },
        "Severe+": {
            "summary": "Extreme emergency. Evacuation advisable if possible.",
            "precautions": ["Consider evacuation to cleaner area", "Maximum protection if staying", "Hospital care may be necessary for vulnerable groups"],
            "recommended_activities": ["Evacuation advisable", "Maximum protected environment if staying", "Follow all emergency protocols"],
            "health_implications": "Extreme emergency. Everyone at serious risk. Maximum protection or evacuation essential.",
            "delhi_specific": "Extreme emergency rarely reached. Consider temporary relocation if feasible. Full government emergency response active."
        }
    }
    
    # Adjust for risk profile
    rec = recommendations.get(aqi_category, recommendations["Moderate"]).copy()
    
    if risk_profile in ["children", "pregnant", "elderly", "high_risk", "critical"]:
        rec["precautions"].insert(0, f"As a {risk_profile} individual, extra caution is essential")
    
    return rec


# Main entry point function
def get_personalized_recommendation(
    aqi_value: float,
    user_health_conditions: Optional[List[str]] = None,
    family_members: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Main entry point - uses Gemini if available, falls back to rules"""
    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        return get_personalized_recommendation_with_gemini(aqi_value, user_health_conditions, family_members=family_members)
    else:
        return get_rule_based_fallback(aqi_value, user_health_conditions, family_members)


def format_recommendation_for_sms(recommendation: Dict[str, Any], recipient_name: str = "") -> str:
    """Format recommendation as SMS/WhatsApp/Telegram message"""
    name_prefix = f"Dear {recipient_name},\n\n" if recipient_name else ""
    
    msg = f"""{name_prefix}🌫️ Delhi AQI Alert - {recommendation['aqi_category']}
Current AQI: {recommendation['aqi_value']:.0f}

📋 SUMMARY
{recommendation['summary']}

⚠️ KEY PRECAUTIONS
"""
    
    for idx, precaution in enumerate(recommendation['precautions'][:4], 1):
        msg += f"{idx}. {precaution}\n"
    
    msg += f"\n✅ RECOMMENDED ACTIVITIES\n"
    for activity in recommendation['recommended_activities'][:3]:
        msg += f"• {activity}\n"
    
    msg += f"\n🏥 HEALTH IMPLICATIONS\n{recommendation['health_implications']}\n"
    
    msg += f"\n📍 DELHI CONTEXT\n{recommendation['delhi_specific']}\n"
    
    if 'family_specific' in recommendation:
        msg += f"\n👨‍👩‍👧‍👦 FAMILY GUIDANCE\n{recommendation['family_specific']}\n"
    
    msg += f"\n⏰ Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
    msg += f"\n{'🤖 AI-Powered' if recommendation.get('ai_powered') else '📊 Rule-Based'} Recommendation"
    
    return msg


if __name__ == "__main__":
    # Test the agent
    print("🤖 Testing AQI Agent...")
    print(f"Gemini Available: {GEMINI_AVAILABLE}")
    print(f"API Key Set: {bool(GEMINI_API_KEY)}")
    
    test_aqi = 184
    test_conditions = ["asthma", "child"]
    test_family = [
        {"name": "John", "age": 8, "health_conditions": ["asthma"]},
        {"name": "Mary", "age": 35, "health_conditions": []},
        {"name": "Grandpa", "age": 68, "health_conditions": ["heart disease"]}
    ]
    
    print(f"\nTest: AQI {test_aqi}, Conditions: {test_conditions}")
    result = get_personalized_recommendation(test_aqi, test_conditions, test_family)
    
    print(f"\nCategory: {result['aqi_category']}")
    print(f"Risk Profile: {result['risk_profile']}")
    print(f"AI Powered: {result.get('ai_powered', False)}")
    print(f"\nSummary: {result['summary']}")
    
    print("\n" + "="*50)
    print("TELEGRAM FORMAT:")
    print("="*50)
    print(format_recommendation_for_sms(result, "John's Family"))
