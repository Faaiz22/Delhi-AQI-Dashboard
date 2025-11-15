"""
Agent Logic Module - The "Brain" of the AQI Monitoring Agent
Specialized for Delhi NCR Region

This module contains the rule-based knowledge base and recommendation engine
that provides personalized air quality advice based on AQI levels and user health profiles.
Optimized for Delhi NCR's air quality conditions with balanced, actionable guidance.
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class AQICategory(Enum):
    """AQI categories based on EPA standards with Delhi NCR extensions"""
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"
    SEVERE = "Severe"  # Delhi NCR specific category (401-450)
    SEVERE_PLUS = "Severe+"  # Delhi NCR specific for 450+


class RiskProfile(Enum):
    """User risk profiles for personalized recommendations - Delhi NCR specific"""
    GENERAL = "general"
    CHILDREN = "children"  # 0-12 years
    TEENS = "teens"  # 13-18 years
    PREGNANT = "pregnant"  # Pregnant women
    ELDERLY = "elderly"  # 60+ years
    SENSITIVE = "sensitive"  # Mild respiratory/cardiac conditions
    HIGH_RISK = "high_risk"  # Severe chronic conditions
    CRITICAL = "critical"  # Multiple severe conditions or immunocompromised


# Comprehensive AQI Rule-Based Knowledge Base - Delhi NCR Optimized
# Balanced guidance that informs without causing unnecessary panic
AQI_RULE_KNOWLEDGE_BASE = {
    "Good": {
        "aqi_range": (0, 50),
        "color": "#00E400",
        "delhi_context": "Rare but wonderful - enjoy the fresh air!",
        "general": {
            "summary": "Air quality is excellent! Perfect day to enjoy outdoor activities.",
            "activities": [
                "Great day for jogging, cycling, or outdoor yoga",
                "Ideal for visiting parks like Lodhi Gardens or India Gate",
                "Perfect for outdoor sports and recreation",
                "Good time for morning walks and evening strolls"
            ],
            "precautions": [
                "Stay hydrated, especially in warm weather",
                "Keep a basic mask handy as conditions can change"
            ],
            "health_implications": "Air quality poses minimal risk. Feel free to enjoy outdoor activities.",
            "delhi_specific": "Make the most of this rare good air quality day in Delhi NCR. Conditions like this are uncommon, especially during winter months."
        },
        "children": {
            "summary": "Perfect day for children to play outdoors!",
            "activities": [
                "Safe for all outdoor play and sports",
                "Great for school outdoor activities",
                "Ideal for park visits and outdoor games",
                "Good for cycling and learning new outdoor skills"
            ],
            "precautions": [
                "Ensure children stay hydrated",
                "Apply sunscreen for extended play",
                "Keep an eye on energy levels to avoid overexertion"
            ],
            "health_implications": "Excellent conditions for children's outdoor activities and development.",
            "delhi_specific": "These days are precious in Delhi NCR. Encourage outdoor play to build healthy habits."
        },
        "teens": {
            "summary": "Excellent conditions for sports and outdoor activities!",
            "activities": [
                "Perfect for competitive sports and athletics",
                "Great for training and practice sessions",
                "Good for outdoor study sessions",
                "Safe for extended physical activities"
            ],
            "precautions": [
                "Stay well hydrated during intense activities",
                "Take normal breaks as you would on any active day"
            ],
            "health_implications": "Safe for all physical activities. Great day to be active.",
            "delhi_specific": "Take advantage of good air quality for outdoor sports and activities."
        },
        "pregnant": {
            "summary": "Safe and pleasant conditions for outdoor activities.",
            "activities": [
                "Good for prenatal walks and light exercise",
                "Safe for attending outdoor appointments",
                "Comfortable for shopping and errands",
                "Nice day for spending time outdoors"
            ],
            "precautions": [
                "Continue regular prenatal care routine",
                "Avoid overexertion as you normally would",
                "Stay hydrated and comfortable"
            ],
            "health_implications": "Air quality is safe for pregnancy. Good time for gentle outdoor activities.",
            "delhi_specific": "Enjoy this comfortable day for outdoor activities while maintaining your normal pregnancy precautions."
        },
        "elderly": {
            "summary": "Wonderful conditions for outdoor activities and socializing.",
            "activities": [
                "Perfect for morning walks in nearby parks",
                "Good for visiting friends or community centers",
                "Comfortable for outdoor yoga or light exercises",
                "Nice weather for outdoor activities"
            ],
            "precautions": [
                "Continue regular medications as prescribed",
                "Carry water and take breaks as needed",
                "Avoid midday heat if weather is warm"
            ],
            "health_implications": "Safe conditions for elderly individuals, including those with mild heart or lung conditions.",
            "delhi_specific": "Lovely day to enjoy outdoor spaces. Take advantage of the fresh air at parks like Nehru Park or Buddha Garden."
        },
        "sensitive": {
            "summary": "Excellent air quality - safe even with respiratory sensitivities.",
            "activities": [
                "Safe for outdoor exercise and activities",
                "Good day for extended outdoor time",
                "Can enjoy normal daily activities"
            ],
            "precautions": [
                "Keep your regular medications handy as always",
                "Stay hydrated during activities",
                "Listen to your body and take breaks as needed"
            ],
            "health_implications": "Air quality is safe. Asthma and allergies should not be triggered.",
            "delhi_specific": "Good opportunity to enjoy outdoor activities you might normally avoid during pollution season."
        },
        "high_risk": {
            "summary": "Safe conditions with proper pacing and normal precautions.",
            "activities": [
                "Outdoor activities okay with appropriate pacing",
                "Good for gentle outdoor exercises",
                "Comfortable for necessary errands and appointments"
            ],
            "precautions": [
                "Continue all regular medications",
                "Keep rescue inhalers accessible as usual",
                "Monitor how you feel and adjust activity accordingly",
                "Consult your doctor before major activity changes"
            ],
            "health_implications": "Air quality is safe when you follow your usual health management plan.",
            "delhi_specific": "Enjoy improved air quality while maintaining your normal health routines and precautions."
        },
        "critical": {
            "summary": "Safe air quality, but maintain your regular medical care routine.",
            "activities": [
                "Short outdoor sessions possible with supervision",
                "Fresh air can be beneficial in small doses",
                "Keep regular medical appointments"
            ],
            "precautions": [
                "Continue all prescribed medications and treatments",
                "Have caregiver present for outdoor time",
                "Keep emergency contacts accessible",
                "Monitor symptoms as you normally do"
            ],
            "health_implications": "Good air quality, but always prioritize your medical treatment plan.",
            "delhi_specific": "While air quality is good, maintain your regular medical supervision and care routine."
        }
    },
    
    "Moderate": {
        "aqi_range": (51, 100),
        "color": "#FFFF00",
        "delhi_context": "Typical acceptable day - better than usual conditions",
        "general": {
            "summary": "Air quality is acceptable. Most people can go about their normal activities.",
            "activities": [
                "Normal outdoor activities are fine",
                "Good for moderate exercise",
                "Regular commuting and work activities okay"
            ],
            "precautions": [
                "Sensitive individuals should watch for any symptoms",
                "Consider masks during heavy traffic if you're sensitive",
                "Take normal breaks during extended outdoor work"
            ],
            "health_implications": "Air quality is acceptable for most people.",
            "delhi_specific": "This is actually better than average for Delhi NCR. Normal activities can continue."
        },
        "children": {
            "summary": "Generally safe with some common-sense precautions.",
            "activities": [
                "Outdoor play is fine with time limits (2-3 hours)",
                "School activities can proceed normally",
                "Morning hours typically offer better air quality",
                "Regular sports and activities okay"
            ],
            "precautions": [
                "Watch for any coughing or discomfort",
                "Keep children hydrated",
                "Consider masks for long commutes in heavy traffic",
                "Adjust outdoor time if child has active cold symptoms"
            ],
            "health_implications": "Generally safe, but monitor children with asthma or allergies.",
            "delhi_specific": "Schools typically operate normally at this level. Standard precautions apply."
        },
        "teens": {
            "summary": "Safe for most activities with awareness.",
            "activities": [
                "Sports and athletics can continue",
                "May want to reduce intensity of very strenuous training",
                "Morning hours ideal for outdoor activities",
                "Indoor alternatives available if preferred"
            ],
            "precautions": [
                "Watch for unusual fatigue or breathing changes",
                "Take appropriate breaks during intense exercise",
                "Consider masks for two-wheeler commutes",
                "Stay hydrated"
            ],
            "health_implications": "Most teens can continue normal activities. Those with asthma should monitor symptoms.",
            "delhi_specific": "Typical conditions for Delhi NCR. Schools and sports continue with normal precautions."
        },
        "pregnant": {
            "summary": "Acceptable with sensible precautions for expectant mothers.",
            "activities": [
                "Regular walks and light exercise are fine (30-45 min)",
                "Prenatal appointments and errands can proceed",
                "Choose morning hours when air is typically cleaner",
                "Prefer air-conditioned transport when available"
            ],
            "precautions": [
                "Consider wearing mask in heavy traffic areas",
                "Stay well hydrated",
                "Listen to your body and rest as needed",
                "Keep indoor spaces well-ventilated or use air purifiers",
                "Continue prenatal vitamins"
            ],
            "health_implications": "Generally acceptable, though pregnant women may be more sensitive to air quality.",
            "delhi_specific": "Common conditions in Delhi NCR. Follow your doctor's advice and maintain prenatal care routine."
        },
        "elderly": {
            "summary": "Acceptable with standard precautions for seniors.",
            "activities": [
                "Morning walks are fine (30-40 minutes)",
                "Regular errands and appointments can continue",
                "Early morning typically offers better air",
                "Use comfortable transport options"
            ],
            "precautions": [
                "Consider wearing mask during busy traffic periods",
                "Carry regular medications",
                "Watch for any chest discomfort or breathlessness",
                "Choose less trafficked routes when possible",
                "Return indoors if feeling unwell"
            ],
            "health_implications": "Acceptable for most elderly, though those with heart or lung conditions should be mindful.",
            "delhi_specific": "Standard conditions for Delhi NCR. Maintain your regular routine with common-sense precautions."
        },
        "sensitive": {
            "summary": "Use care and limit prolonged outdoor exposure.",
            "activities": [
                "Limit outdoor activities to essentials",
                "Choose morning hours for any outdoor needs",
                "Consider indoor exercise alternatives",
                "Short errands are manageable with mask"
            ],
            "precautions": [
                "Wear N95 mask when outdoors, especially in traffic",
                "Keep rescue inhalers readily accessible",
                "Monitor for coughing, wheezing, or shortness of breath",
                "Use air purifiers indoors",
                "Avoid exercise near high-traffic roads"
            ],
            "health_implications": "Sensitive individuals may notice minor symptoms. Take reasonable precautions.",
            "delhi_specific": "At this level, those with respiratory conditions should use protective measures like masks."
        },
        "high_risk": {
            "summary": "Limit outdoor time and use protective measures.",
            "activities": [
                "Minimize outdoor time to necessities",
                "Prefer indoor activities",
                "Use air-conditioned transport for travel",
                "Choose times with lighter traffic"
            ],
            "precautions": [
                "Wear N95 mask for outdoor exposure",
                "Carry all rescue medications",
                "Keep oxygen equipment accessible if prescribed",
                "Monitor symptoms regularly",
                "Have emergency contacts handy",
                "Use air purifiers indoors"
            ],
            "health_implications": "Increased risk of symptoms for those with severe respiratory or cardiac conditions.",
            "delhi_specific": "Those with serious health conditions should take this level seriously and limit exposure."
        },
        "critical": {
            "summary": "Stay indoors with medical monitoring.",
            "activities": [
                "Remain indoors in filtered air environment",
                "Essential medical appointments only",
                "Use medical transport if travel needed",
                "Minimize physical exertion"
            ],
            "precautions": [
                "Stay in air-filtered environment",
                "Use HEPA air purifiers",
                "Seal windows if needed",
                "Monitor oxygen levels if equipment available",
                "Have caregiver assistance",
                "Keep medical team informed",
                "Emergency contacts readily available"
            ],
            "health_implications": "Significant risk for immunocompromised individuals. Follow medical guidance closely.",
            "delhi_specific": "Maintain close medical supervision and stay in protected indoor environment."
        }
    },
    
    "Unhealthy for Sensitive Groups": {
        "aqi_range": (101, 150),
        "color": "#FF7E00",
        "delhi_context": "Common in Delhi NCR - protective measures recommended",
        "general": {
            "summary": "Air quality affects sensitive groups. General public should take precautions for prolonged outdoor activities.",
            "activities": [
                "Reduce prolonged outdoor activities",
                "Take breaks during outdoor work",
                "Choose less strenuous activities",
                "Indoor alternatives recommended when possible"
            ],
            "precautions": [
                "Wear mask when outdoors, especially in traffic",
                "Watch for throat irritation or coughing",
                "Stay hydrated",
                "Use air purifiers indoors"
            ],
            "health_implications": "General public may experience minor symptoms. Sensitive groups will notice effects.",
            "delhi_specific": "Typical level for Delhi NCR. Masks and air purifiers become important at this stage."
        },
        "children": {
            "summary": "Children should limit outdoor activities and use protection.",
            "activities": [
                "Prefer indoor play and activities",
                "Limit outdoor time to 1-2 hours if needed",
                "School may modify outdoor activities",
                "Indoor alternatives are better choice"
            ],
            "precautions": [
                "Mask recommended for school commute",
                "Use air purifiers in child's room",
                "Watch for persistent cough or eye irritation",
                "Keep asthma medication handy if applicable",
                "Postpone outdoor play if child has cold or cough"
            ],
            "health_implications": "Children's developing lungs are more vulnerable. Protective measures help minimize exposure.",
            "delhi_specific": "Schools in Delhi NCR may reduce outdoor activities at this level. Follow school guidelines and protect commute time."
        },
        "teens": {
            "summary": "Avoid strenuous outdoor activities. Use protective measures.",
            "activities": [
                "Skip outdoor sports practice when possible",
                "Indoor gym and activities preferred",
                "Avoid jogging or cycling outdoors",
                "Reduce outdoor exposure during commute"
            ],
            "precautions": [
                "Wear mask for outdoor exposure and commute",
                "Watch for reduced stamina or persistent cough",
                "Keep inhaler handy even without asthma history",
                "Stay hydrated",
                "Report breathing difficulties to parents or teachers"
            ],
            "health_implications": "Athletic performance may be affected. Lung function can be temporarily reduced with prolonged exposure.",
            "delhi_specific": "Many Delhi NCR schools modify outdoor sports at this level. Focus on indoor activities and protect health."
        },
        "pregnant": {
            "summary": "Pregnant women should minimize outdoor exposure.",
            "activities": [
                "Stay indoors when possible",
                "Essential errands only",
                "Work from home if option available",
                "Telehealth consultations when feasible"
            ],
            "precautions": [
                "Wear N95 mask for any outdoor time",
                "Use air purifiers at home, especially in bedroom",
                "Keep rooms well-sealed during high pollution hours",
                "Take antioxidant-rich prenatal vitamins",
                "Monitor for any respiratory discomfort",
                "Maintain regular prenatal appointments"
            ],
            "health_implications": "Prolonged exposure at this level may affect pregnancy. Take protective measures seriously but stay calm.",
            "delhi_specific": "Many Delhi NCR doctors recommend protective measures for pregnant women at this level. Follow medical advice and use available protection."
        },
        "elderly": {
            "summary": "Seniors should stay indoors as much as possible.",
            "activities": [
                "Limit outdoor activities to essentials",
                "Essential medical appointments only",
                "Use air-conditioned transport when going out",
                "Indoor activities and socializing preferred"
            ],
            "precautions": [
                "Wear mask for any outdoor exposure",
                "Keep all medications accessible",
                "Monitor for chest discomfort or breathlessness",
                "Use air purifiers at home",
                "Have family check in regularly",
                "Keep emergency contacts handy"
            ],
            "health_implications": "Elderly with heart or lung conditions face increased risk. Protective measures important.",
            "delhi_specific": "Delhi NCR hospitals see increased elderly patients at this level. Take precautions seriously but maintain calm routine with protection."
        },
        "sensitive": {
            "summary": "Those with respiratory conditions should stay indoors with protection.",
            "activities": [
                "Indoor activities only",
                "Essential outdoor errands with protection",
                "Work from home if possible",
                "Postpone non-essential appointments"
            ],
            "precautions": [
                "Use air purifiers in main living areas",
                "Wear N95 mask for any outdoor exposure",
                "Keep rescue inhalers readily accessible",
                "Monitor peak flow if you have asthma",
                "May need to adjust medication (consult doctor)",
                "Have nebulizer ready if you use one",
                "Keep doctor's contact handy"
            ],
            "health_implications": "Asthma and respiratory conditions likely to be aggravated. Follow your action plan and use protection.",
            "delhi_specific": "This is when respiratory clinics in Delhi NCR see increased patients. Use your medications and protective measures consistently."
        },
        "high_risk": {
            "summary": "Serious health conditions require strong protective measures.",
            "activities": [
                "Stay indoors in filtered air",
                "No outdoor activities",
                "Essential medical appointments only with protection",
                "Rest and minimize exertion"
            ],
            "precautions": [
                "Create clean air space with HEPA purifiers",
                "Oxygen equipment ready if prescribed",
                "Monitor symptoms regularly",
                "Have someone nearby for assistance",
                "Hospital bag ready for emergencies",
                "Keep all medications organized",
                "Medical contacts easily accessible"
            ],
            "health_implications": "Significant risk for severe COPD and cardiac conditions. Follow medical guidance and use all protective measures.",
            "delhi_specific": "At this level, those with serious conditions should be under medical supervision. Stay in contact with your healthcare team."
        },
        "critical": {
            "summary": "Immunocompromised individuals need maximum protection.",
            "activities": [
                "Complete indoor isolation in clean air environment",
                "Medical consultation for any necessary travel",
                "All activities indoors only",
                "Rest and minimize physical demands"
            ],
            "precautions": [
                "Medical-grade air filtration required",
                "Continuous health monitoring",
                "Oxygen therapy as prescribed",
                "24/7 caregiver presence",
                "Medical team on standby",
                "Hospital admission may be advisable",
                "Keep all medical records accessible"
            ],
            "health_implications": "High risk for complications. Medical supervision essential. Stay calm and follow medical guidance.",
            "delhi_specific": "Those with transplants or severe immunocompromise should be under medical care. Coordinate closely with your medical team."
        }
    },

    "Unhealthy": {
        "aqi_range": (151, 200),
        "color": "#FF0000",
        "delhi_context": "Frequent in Delhi NCR during winter - strong protection needed",
        "general": {
            "summary": "Everyone affected. Stay indoors and use protection when going out.",
            "activities": [
                "Stay indoors when possible",
                "Work from home if available",
                "Avoid outdoor exercise",
                "Reschedule non-essential outdoor activities"
            ],
            "precautions": [
                "Wear N95 mask for any outdoor time",
                "Keep windows closed",
                "Use air purifiers indoors",
                "Monitor family members for symptoms",
                "Avoid activities that create indoor pollution (smoking, certain cooking)"
            ],
            "health_implications": "Everyone may experience health effects. Sensitive groups at higher risk.",
            "delhi_specific": "Common during Delhi NCR winter season. Government restrictions typically begin. Use protective measures consistently."
        },
        "children": {
            "summary": "Keep children indoors. Schools may close or go online.",
            "activities": [
                "Indoor activities only",
                "Schools may shift to online classes",
                "No outdoor play or sports",
                "Focus on indoor learning and games"
            ],
            "precautions": [
                "Keep children in rooms with air purifiers",
                "Mask required if going outdoors briefly",
                "Monitor for cough, wheezing, or eye irritation",
                "Nebulizer treatments if needed for respiratory issues",
                "Vitamin supplements as recommended by pediatrician",
                "Keep symptoms diary if persistent issues"
            ],
            "health_implications": "Significant impact on children's health. Protection important to minimize exposure effects.",
            "delhi_specific": "Schools in Delhi NCR typically close or go online at this level. Keep children protected indoors with air filtration."
        },
        "teens": {
            "summary": "All outdoor activities should be avoided. Stay home when possible.",
            "activities": [
                "Attend online classes",
                "Indoor exercises only - yoga, stretching, home workouts",
                "No outdoor activities or sports",
                "Focus on indoor study and activities"
            ],
            "precautions": [
                "Use air purifiers in study area",
                "Wear N95 mask for essential outdoor exposure",
                "Monitor for fatigue or breathing difficulty",
                "Stay well hydrated",
                "Report persistent symptoms to parents",
                "Limit screen time if experiencing eye irritation"
            ],
            "health_implications": "Affects physical performance and concentration. Protection helps minimize long-term impact.",
            "delhi_specific": "Board exam students should use air purifiers while studying. Many families consider temporary relocation during this period."
        },
        "pregnant": {
            "summary": "Pregnant women need strong protection. Minimize all outdoor exposure.",
            "activities": [
                "Stay indoors consistently",
                "Work from home strongly recommended",
                "Prenatal appointments via telemedicine when possible",
                "Only essential outdoor errands with full protection"
            ],
            "precautions": [
                "Use 2-3 air purifiers at home",
                "Seal windows during high pollution hours",
                "N95 mask mandatory for any outdoor time",
                "High-quality prenatal vitamins with antioxidants",
                "Monitor baby movements regularly",
                "Keep healthcare provider informed",
                "Watch for concerning symptoms",
                "Monitor blood pressure at home if possible"
            ],
            "health_implications": "Increased risk to pregnancy health. Strong protection measures help reduce exposure impact.",
            "delhi_specific": "Delhi NCR doctors recommend strong protective measures for pregnant women. Follow medical advice and stay indoors with good air filtration."
        },
        "elderly": {
            "summary": "Seniors should stay indoors with good air quality protection.",
            "activities": [
                "Stay indoors",
                "Indoor activities and rest",
                "Medical appointments at home if possible",
                "Essential travel only with protection"
            ],
            "precautions": [
                "Use multiple air purifiers at home",
                "Monitor health vitals daily",
                "Keep all medications accessible",
                "Have family member check in daily",
                "Oxygen equipment ready if prescribed",
                "Emergency contacts clearly posted",
                "Watch for breathlessness, chest pain, or severe fatigue"
            ],
            "health_implications": "Increased risk of cardiac and respiratory complications. Protection and monitoring important.",
            "delhi_specific": "Delhi NCR hospitals see increased elderly admissions at this level. Stay protected and maintain medical contact."
        },
        "sensitive": {
            "summary": "Those with respiratory conditions need indoor isolation with filtration.",
            "activities": [
                "Complete indoor isolation",
                "No outdoor activities",
                "Work from home mandatory if possible",
                "Rest and minimal physical exertion"
            ],
            "precautions": [
                "Hospital-grade air filtration in main rooms",
                "Follow your asthma action plan closely",
                "Increase controller medications as directed by doctor",
                "Keep rescue inhalers at hand always",
                "Nebulizer treatments as needed",
                "Monitor peak flow regularly if asthmatic",
                "Seek medical care if symptoms worsen despite medication"
            ],
            "health_implications": "Significant aggravation of respiratory conditions likely. Medical management and protection essential.",
            "delhi_specific": "Respiratory clinics in Delhi NCR are busy at this level. Follow your treatment plan and stay protected indoors."
        },
        "high_risk": {
            "summary": "Serious conditions require medical coordination and maximum protection.",
            "activities": [
                "Complete indoor isolation with medical-grade filtration",
                "No outdoor exposure",
                "Medical supervision recommended",
                "Rest and avoid physical strain"
            ],
            "precautions": [
                "Medical-grade HEPA filtration required",
                "Oxygen therapy as prescribed",
                "Continuous symptom monitoring",
                "24/7 supervision or assistance",
                "Hospital contact maintained",
                "All medications strictly followed",
                "Emergency plan in place and practiced"
            ],
            "health_implications": "High risk of serious complications. Medical supervision and maximum protection critical.",
            "delhi_specific": "Those with severe COPD or heart failure should be under medical supervision. Coordinate with healthcare team and consider hospital monitoring if symptoms worsen."
        },
        "critical": {
            "summary": "Maximum medical supervision required. Hospital care may be advisable.",
            "activities": [
                "Medical facility admission may be recommended",
                "Complete rest under medical supervision",
                "All care coordinated with medical team",
                "Protected indoor environment mandatory"
            ],
            "precautions": [
                "Coordinate closely with medical team",
                "Medical-grade air filtration essential",
                "Continuous medical monitoring",
                "Oxygen therapy and all treatments as prescribed",
                "24/7 medical supervision or standby",
                "Hospital admission advisable for some conditions",
                "All emergency procedures in place"
            ],
            "health_implications": "Serious risk for immunocompromised and transplant patients. Medical supervision essential.",
            "delhi_specific": "Those with transplants or severe immunocompromise should be under hospital care or close medical supervision. Work closely with your medical team."
        }
    },

    "Very Unhealthy": {
        "aqi_range": (201, 300),
        "color": "#8F3F97",
        "delhi_context": "Common during Delhi NCR winter peak - emergency measures in effect",
        "general": {
            "summary": "Health alert for everyone. Stay indoors with air filtration.",
            "activities": [
                "Stay indoors",
                "All activities indoors only",
                "Work from home",
                "Essential travel only with maximum protection"
            ],
            "precautions": [
                "Keep windows and doors closed",
                "Use air purifiers on high settings",
                "N95 mask mandatory for any outdoor time",
                "Monitor all family members for symptoms",
                "Stay informed about air quality updates",
                "Avoid cooking methods that create smoke"
            ],
            "health_implications": "Everyone at increased risk. Serious effects for sensitive groups.",
            "delhi_specific": "Emergency level common during Delhi NCR winter. Government emergency measures typically active. Follow official guidelines and stay protected."
        },
        "children": {
            "summary": "Schools closed. Children must stay indoors with air filtration.",
            "activities": [
                "Indoor isolation mandatory",
                "Online classes",
                "Indoor games and activities only",
                "No outdoor exposure"
            ],
            "precautions": [
                "Multiple air purifiers in home",
                "Keep children in filtered rooms",
                "Monitor health daily",
                "Nebulizer ready for respiratory issues",
                "Medical consultation if persistent symptoms",
                "Consider temporary relocation if feasible and symptoms severe"
            ],
            "health_implications": "Serious impact on children's health. Strong protection reduces exposure effects.",
            "delhi_specific": "All Delhi NCR schools closed at this level. Many families temporarily relocate children if feasible. Focus on indoor protection and health monitoring."
        },
        "teens": {
            "summary": "Complete indoor isolation. Online schooling only.",
            "activities": [
                "Stay home completely",
                "Online classes only",
                "Indoor exercises - yoga, light workouts",
                "No outdoor activities"
            ],
            "precautions": [
                "Air purifiers in study and sleep areas",
                "N95 mask for any brief outdoor necessity",
                "Monitor for symptoms affecting study - headaches, fatigue",
                "Stay well hydrated",
                "Medical consultation if symptoms persist"
            ],
            "health_implications": "Affects health and academic performance. Protection and indoor environment quality important.",
            "delhi_specific": "Critical period for students, especially those preparing for board exams. Use air purifiers while studying. Follow online classes and stay protected."
        },
        "pregnant": {
            "summary": "High risk level. Maximum protection and medical coordination needed.",
            "activities": [
                "Complete indoor isolation mandatory",
                "Work from home non-negotiable",
                "All prenatal care via telemedicine if possible",
                "No non-essential outdoor exposure"
            ],
            "precautions": [
                "Multiple HEPA air purifiers essential",
                "Windows sealed during high pollution",
                "N95 mask for essential outdoor exposure only",
                "High-dose prenatal vitamins as prescribed",
                "Daily fetal movement monitoring",
                "Regular medical check-ins",
                "Blood pressure monitoring at home",
                "Immediate medical consultation for any concerns"
            ],
            "health_implications": "Serious risk to pregnancy. Strong protection measures critical to minimize impact.",
            "delhi_specific": "Delhi NCR obstetricians see increased pregnancy complications at this level. Follow medical advice strictly. Some consider temporary relocation if medically advised and feasible."
        },
        "elderly": {
            "summary": "High risk for seniors. Indoor isolation with medical monitoring needed.",
            "activities": [
                "Complete indoor isolation",
                "All activities indoors",
                "Medical care at home when possible",
                "Essential appointments only with maximum protection"
            ],
            "precautions": [
                "Multiple air purifiers operating continuously",
                "Daily health monitoring - BP, oxygen, temperature",
                "All medications maintained strictly",
                "Family member or caregiver present regularly",
                "Oxygen concentrator ready if prescribed",
                "Emergency contacts posted prominently",
                "Medical consultation for: severe breathlessness, chest pain, extreme fatigue",
                "Consider medical facility if living alone with serious conditions"
            ],
            "health_implications": "High risk of cardiac and respiratory events. Medical coordination and protection essential.",
            "delhi_specific": "Delhi NCR cardiac units see significant increase in elderly admissions. Stay protected, maintain medical contact, and don't hesitate to seek care if needed."
        },
        "sensitive": {
            "summary": "Emergency level for respiratory conditions. Medical supervision important.",
            "activities": [
                "Complete indoor isolation with medical-grade filtration",
                "No outdoor exposure",
                "Medical consultation for activity guidance",
                "Rest and minimal exertion"
            ],
            "precautions": [
                "Medical-grade air filtration mandatory",
                "Strict adherence to treatment plan",
                "Peak flow monitoring 3x daily if asthmatic",
                "Controller medication adjustments with doctor guidance",
                "Rescue medication readily available always",
                "Nebulizer treatments as directed",
                "Medical consultation if symptoms worsen",
                "Emergency plan practiced and ready"
            ],
            "health_implications": "Serious risk of respiratory exacerbations. Medical management and protection critical.",
            "delhi_specific": "Respiratory specialists in Delhi NCR are very busy at this level. Follow treatment plan strictly and maintain medical contact."
        },
        "high_risk": {
            "summary": "Critical level for severe conditions. Medical supervision mandatory.",
            "activities": [
                "Medical-supervised indoor environment only",
                "No physical activities",
                "Medical facility monitoring may be advisable",
                "Complete rest required"
            ],
            "precautions": [
                "Hospital-grade air filtration essential",
                "Oxygen therapy as prescribed",
                "Continuous health monitoring",
                "Medical team actively involved",
                "Caregiver present 24/7",
                "Hospital admission may be recommended",
                "All emergency protocols active",
                "Medical equipment maintained and ready"
            ],
            "health_implications": "Life-threatening risk for severe COPD, heart failure, recent surgery patients. Medical supervision essential.",
            "delhi_specific": "Those with severe conditions should be under active medical care. Hospital admission may be advisable. Work closely with your medical team."
        },
        "critical": {
            "summary": "Medical emergency level. Hospital care strongly recommended.",
            "activities": [
                "Hospital admission recommended for most",
                "Complete rest under medical supervision",
                "All care coordinated by medical team",
                "ICU monitoring may be necessary"
            ],
            "precautions": [
                "Hospital admission strongly advisable",
                "If at home: medical-grade air filtration with medical supervision",
                "Continuous oxygen and vital sign monitoring",
                "Medical team on active standby",
                "All medications and treatments strictly followed",
                "Emergency medical services on immediate call",
                "Family informed of situation severity"
            ],
            "health_implications": "Extreme risk for immunocompromised and transplant patients. Medical facility care strongly recommended.",
            "delhi_specific": "Transplant and severely immunocompromised patients should be in hospital care. Delhi NCR ICUs prepared for such cases. Follow medical team guidance."
        }
    },

    "Hazardous": {
        "aqi_range": (301, 400),
        "color": "#7E0023",
        "delhi_context": "Severe emergency - common during Delhi winter peaks",
        "general": {
            "summary": "Health emergency. Everyone must stay indoors with air filtration.",
            "activities": [
                "Stay indoors in protected environment",
                "No outdoor activities under any circumstances",
                "Work from home mandatory",
                "Follow all official emergency guidelines"
            ],
            "precautions": [
                "Seal windows and doors",
                "Multiple air purifiers essential",
                "N95 mask even indoors if air quality compromised",
                "Monitor all family members closely",
                "Follow emergency broadcasts",
                "Emergency supplies ready",
                "Medical contacts accessible"
            ],
            "health_implications": "Serious health effects for everyone. Follow all emergency protocols.",
            "delhi_specific": "Emergency level requiring government action. GRAP Stage 4 typically active. Follow all official guidelines and stay protected."
        },
        "children": {
            "summary": "Emergency level. Children must be in protected indoor environment.",
            "activities": [
                "Protected indoor environment mandatory",
                "Online classes only",
                "Indoor activities in filtered air only",
                "Medical consultation for any symptoms"
            ],
            "precautions": [
                "Multiple air purifiers in home essential",
                "Keep children in best-filtered rooms",
                "Daily health monitoring mandatory",
                "Immediate medical attention for respiratory issues",
                "Vitamin supplements as recommended",
                "Consider temporary relocation if medically advised and feasible"
            ],
            "health_implications": "Emergency level for children's health. Strong protection essential to minimize impact.",
            "delhi_specific": "Schools closed, outdoor activities banned. Many Delhi NCR families relocate children temporarily if feasible. Focus on maximum indoor protection."
        },
        "teens": {
            "summary": "Emergency conditions. Complete indoor protection required.",
            "activities": [
                "Stay in protected indoor environment",
                "Online education only",
                "Light indoor activities only",
                "Medical guidance for any health concerns"
            ],
            "precautions": [
                "Air-filtered environment essential",
                "Monitor for health impacts on studying",
                "Immediate medical consultation if symptoms worsen",
                "Stay well hydrated",
                "Follow all protective guidelines"
            ],
            "health_implications": "Emergency level affecting health and activities. Protection critical.",
            "delhi_specific": "Critical period for students. Board exams may be affected. Use air purifiers, follow online classes, maintain medical contact."
        },
        "pregnant": {
            "summary": "Critical emergency for pregnancy. Maximum medical coordination required.",
            "activities": [
                "Protected indoor environment mandatory",
                "No outdoor exposure",
                "Medical team actively monitoring",
                "Hospital admission may be advisable for high-risk pregnancies"
            ],
            "precautions": [
                "Maximum air filtration essential",
                "Strict medical supervision",
                "Daily fetal monitoring",
                "All prenatal care via protected means",
                "Emergency obstetric services on standby",
                "Blood pressure monitoring",
                "Immediate medical consultation for any concerns",
                "Consider medical facility admission if advised"
            ],
            "health_implications": "Critical risk to pregnancy. Maximum protection and medical supervision essential.",
            "delhi_specific": "Delhi NCR obstetricians recommend maximum protection and close monitoring. Some advise temporary relocation if medically indicated and feasible. Follow medical guidance strictly."
        },
        "elderly": {
            "summary": "Critical emergency for seniors. Medical supervision essential.",
            "activities": [
                "Protected indoor environment mandatory",
                "Medical supervision required",
                "All activities coordinated with medical team",
                "Hospital monitoring may be advisable"
            ],
            "precautions": [
                "Hospital-grade air filtration mandatory",
                "Continuous health monitoring",
                "Medical team actively involved",
                "All medications strictly maintained",
                "Caregiver presence essential",
                "Emergency medical services on standby",
                "Hospital admission advisable for serious conditions",
                "Oxygen therapy ready if prescribed"
            ],
            "health_implications": "Life-threatening risk for elderly. Medical supervision and maximum protection essential.",
            "delhi_specific": "Delhi NCR cardiac and respiratory units at high capacity. Seniors with serious conditions should be under active medical care. Don't delay seeking help if needed."
        },
        "sensitive": {
            "summary": "Medical emergency. Hospital care may be necessary.",
            "activities": [
                "Medical-supervised environment only",
                "Hospital admission may be necessary",
                "No activities except under medical guidance",
                "Complete rest required"
            ],
            "precautions": [
                "Medical facility care may be advisable",
                "If at home: medical-grade filtration with supervision",
                "Strict treatment plan adherence",
                "Continuous monitoring",
                "Medical team actively managing care",
                "Emergency services on immediate call",
                "Hospital admission for severe symptoms"
            ],
            "health_implications": "Life-threatening risk for respiratory conditions. Medical care and maximum protection essential.",
            "delhi_specific": "Respiratory patients should be under active medical management. Hospital admission advisable for severe cases. Work closely with your medical team."
        },
        "high_risk": {
            "summary": "Life-threatening emergency. Hospital care strongly recommended.",
            "activities": [
                "Hospital admission strongly recommended",
                "ICU monitoring may be necessary",
                "All care under medical supervision",
                "No activities except as medically directed"
            ],
            "precautions": [
                "Hospital admission strongly advised",
                "ICU care may be necessary",
                "Continuous medical monitoring",
                "All life support measures ready",
                "Medical team managing all aspects of care",
                "Family fully informed and involved",
                "All emergency protocols active"
            ],
            "health_implications": "Extreme life-threatening risk. Immediate medical facility care essential.",
            "delhi_specific": "Patients with severe conditions should be in hospital. Delhi NCR ICUs prepared but may be busy. Early hospital contact recommended."
        },
        "critical": {
            "summary": "Maximum medical emergency. Immediate hospital care required.",
            "activities": [
                "Hospital/ICU admission mandatory",
                "Intensive medical care required",
                "All care under emergency medical protocols",
                "Life support measures as needed"
            ],
            "precautions": [
                "Immediate hospital admission required",
                "ICU care essential",
                "All emergency medical measures active",
                "Continuous life support monitoring",
                "Medical team managing crisis",
                "Family support and involvement critical",
                "All emergency resources deployed"
            ],
            "health_implications": "Maximum emergency. Immediate life-saving medical care required.",
            "delhi_specific": "Immunocompromised and transplant patients require immediate hospital care. Contact your transplant center or medical team immediately."
        }
    },

    "Severe": {
        "aqi_range": (401, 450),
        "color": "#6B0019",
        "delhi_context": "Severe emergency - occasionally reached during worst Delhi pollution episodes",
        "general": {
            "summary": "Severe health emergency. Maximum protection required for everyone.",
            "activities": [
                "Protected indoor environment mandatory for all",
                "No outdoor exposure",
                "Follow all emergency directives",
                "Emergency supplies maintained"
            ],
            "precautions": [
                "Maximum air filtration essential",
                "Complete indoor isolation",
                "Follow all official emergency protocols",
                "Medical contacts readily accessible",
                "Monitor all family members continuously",
                "Emergency action plans ready"
            ],
            "health_implications": "Severe emergency affecting everyone. Maximum protection essential.",
            "delhi_specific": "Rare but critical level for Delhi NCR. Full emergency measures in effect. Follow all government directives and stay protected."
        },
        "children": {
            "summary": "Critical emergency. Maximum protection essential.",
            "activities": [
                "Maximum protected indoor environment",
                "Medical consultation for protection guidance",
                "Health monitoring essential"
            ],
            "precautions": [
                "Maximum air filtration required",
                "Complete indoor isolation in filtered environment",
                "Continuous health monitoring",
                "Immediate medical attention for any symptoms",
                "Temporary relocation advisable if feasible"
            ],
            "health_implications": "Critical risk to children's health. Maximum protection essential.",
            "delhi_specific": "Critical emergency level. Many families relocate if possible. Focus on maximum indoor protection and medical monitoring."
        },
        "teens": {
            "summary": "Critical emergency requiring maximum protection.",
            "activities": [
                "Maximum protected indoor environment",
                "Medical monitoring recommended",
                "Follow all emergency guidelines"
            ],
            "precautions": [
                "Maximum air filtration essential",
                "Complete indoor isolation",
                "Health monitoring required",
                "Medical consultation for any concerns",
                "Follow all protective measures strictly"
            ],
            "health_implications": "Critical level affecting health. Maximum protection required.",
            "delhi_specific": "Emergency level requiring maximum protection. Follow all guidelines and maintain medical contact."
        },
        "pregnant": {
            "summary": "Maximum emergency. Immediate medical coordination required.",
            "activities": [
                "Medical facility care recommended",
                "Maximum protected environment if at home",
                "Active medical supervision mandatory"
            ],
            "precautions": [
                "Hospital admission may be advisable",
                "Maximum air filtration if at home",
                "Continuous medical monitoring",
                "Emergency obstetric care on standby",
                "Relocation strongly advisable if feasible"
            ],
            "health_implications": "Maximum risk to pregnancy. Immediate medical coordination essential.",
            "delhi_specific": "Obstetricians strongly recommend relocation if feasible. If not possible, hospital monitoring may be advisable. Follow medical guidance."
        },
        "elderly": {
            "summary": "Maximum emergency. Hospital care strongly recommended.",
            "activities": [
                "Hospital admission strongly advised",
                "Maximum medical supervision required",
                "All care coordinated by medical team"
            ],
            "precautions": [
                "Hospital admission strongly recommended",
                "Maximum medical monitoring",
                "All emergency measures active",
                "Life support ready if needed",
                "Medical team managing all care"
            ],
            "health_implications": "Maximum life-threatening risk. Hospital care strongly recommended.",
            "delhi_specific": "Seniors with any health conditions should be hospitalized. Contact medical team immediately."
        },
        "sensitive": {
            "summary": "Maximum emergency. Hospital care required.",
            "activities": [
                "Hospital admission required",
                "Intensive medical care necessary",
                "All care under emergency protocols"
            ],
            "precautions": [
                "Immediate hospital admission",
                "Emergency medical care",
                "Continuous monitoring",
                "All life support measures ready",
                "Medical team managing crisis"
            ],
            "health_implications": "Life-threatening emergency. Immediate hospital care required.",
            "delhi_specific": "Respiratory patients require immediate hospital care. Contact your pulmonologist or go to ER."
        },
        "high_risk": {
            "summary": "Maximum emergency. ICU care may be required.",
            "activities": [
                "ICU admission may be necessary",
                "Maximum medical intervention",
                "Life support as needed"
            ],
            "precautions": [
                "ICU care may be required",
                "Maximum life support measures",
                "Continuous intensive monitoring",
                "Medical team managing all care",
                "All emergency resources deployed"
            ],
            "health_implications": "Maximum life-threatening emergency. ICU care may be necessary.",
            "delhi_specific": "Critical patients require ICU care. Contact your hospital immediately."
        },
        "critical": {
            "summary": "Maximum medical emergency. Immediate ICU care required.",
            "activities": [
                "ICU admission mandatory",
                "Maximum life support measures",
                "Crisis medical management"
            ],
            "precautions": [
                "Immediate ICU admission",
                "Maximum emergency medical care",
                "All life support active",
                "Medical crisis management",
                "Family support essential"
            ],
            "health_implications": "Maximum emergency. Immediate life-saving care required.",
            "delhi_specific": "Maximum emergency. Contact transplant center or specialized medical facility immediately."
        }
    },

    "Severe+": {
        "aqi_range": (451, 500),
        "color": "#4B0012",
        "delhi_context": "Extreme emergency - very rare but has occurred during worst pollution episodes",
        "general": {
            "summary": "Extreme emergency. Evacuation advisable if possible. Maximum protection essential.",
            "activities": [
                "Evacuation advisable if feasible",
                "Maximum protected environment if staying",
                "Follow all emergency directives",
                "Emergency services coordination"
            ],
            "precautions": [
                "Consider evacuation to cleaner area",
                "If staying: maximum air filtration and protection",
                "Follow all government emergency measures",
                "Medical care readily accessible",
                "Emergency action plans active"
            ],
            "health_implications": "Extreme emergency. Everyone at serious risk. Maximum protection or evacuation essential.",
            "delhi_specific": "Extreme emergency rarely reached. Full government emergency response. Consider temporary relocation if feasible."
        },
        "children": {
            "summary": "Extreme emergency. Evacuation strongly recommended.",
            "activities": [
                "Evacuation to cleaner area strongly recommended",
                "Maximum protection if unable to evacuate",
                "Medical supervision essential"
            ],
            "precautions": [
                "Temporary relocation strongly advised",
                "If not possible: maximum indoor protection",
                "Continuous medical monitoring",
                "Emergency medical care accessible",
                "All protective measures at maximum"
            ],
            "health_implications": "Extreme risk. Evacuation strongly recommended to protect health.",
            "delhi_specific": "Extreme emergency. Most families who can relocate do so. Maximum protection essential if staying."
        },
        "teens": {
            "summary": "Extreme emergency. Evacuation recommended.",
            "activities": [
                "Evacuation advisable",
                "Maximum protection if staying",
                "Medical monitoring required"
            ],
            "precautions": [
                "Consider temporary relocation",
                "Maximum protective measures if staying",
                "Continuous health monitoring",
                "Medical care accessible",
                "Follow all emergency protocols"
            ],
            "health_implications": "Extreme risk. Evacuation advisable for health protection.",
            "delhi_specific": "Extreme emergency. Relocation advisable if feasible. Maximum protection if staying."
        },
        "pregnant": {
            "summary": "Extreme emergency. Evacuation or hospital care essential.",
            "activities": [
                "Evacuation strongly recommended",
                "Hospital admission if staying",
                "Maximum medical supervision"
            ],
            "precautions": [
                "Temporary relocation strongly advised",
                "If staying: hospital admission recommended",
                "Maximum medical monitoring",
                "Emergency obstetric care ready",
                "All protective measures at maximum"
            ],
            "health_implications": "Extreme risk to pregnancy. Evacuation or hospital care essential.",
            "delhi_specific": "Obstetricians strongly recommend evacuation. If not feasible, hospital admission advisable."
        },
        "elderly": {
            "summary": "Extreme emergency. Hospital care essential.",
            "activities": [
                "Hospital admission essential",
                "Maximum medical care required",
                "ICU monitoring may be necessary"
            ],
            "precautions": [
                "Immediate hospital admission",
                "ICU care may be required",
                "Maximum medical monitoring",
                "All life support measures ready",
                "Medical team managing all care"
            ],
            "health_implications": "Extreme life-threatening risk. Hospital care essential.",
            "delhi_specific": "All elderly with health conditions should be hospitalized. Contact medical facility immediately."
        },
        "sensitive": {
            "summary": "Extreme emergency. Hospital/ICU care required.",
            "activities": [
                "Hospital/ICU admission required",
                "Maximum medical intervention",
                "Crisis management protocols"
            ],
            "precautions": [
                "Immediate hospital/ICU admission",
                "Maximum emergency care",
                "Life support ready",
                "Medical crisis management",
                "All emergency resources deployed"
            ],
            "health_implications": "Extreme emergency. Immediate hospital care essential.",
            "delhi_specific": "Respiratory patients require immediate hospital care. Go to ER or call emergency services."
        },
        "high_risk": {
            "summary": "Extreme emergency. ICU care essential.",
            "activities": [
                "ICU admission essential",
                "Maximum life support measures",
                "Medical crisis management"
            ],
            "precautions": [
                "Immediate ICU admission",
                "Maximum life support",
                "Continuous intensive monitoring",
                "Medical crisis protocols",
                "All emergency measures active"
            ],
            "health_implications": "Extreme life-threatening emergency. ICU care essential.",
            "delhi_specific": "Critical condition patients require immediate ICU care. Contact hospital immediately."
        },
        "critical": {
            "summary": "Extreme medical emergency. Immediate ICU/specialized care required.",
            "activities": [
                "Immediate ICU/specialized care mandatory",
                "Maximum medical intervention",
                "Life-saving measures"
            ],
            "precautions": [
                "Immediate specialized medical facility admission",
                "Maximum emergency protocols",
                "All life support measures",
                "Medical crisis management",
                "Transplant center coordination if applicable"
            ],
            "health_implications": "Extreme emergency requiring immediate specialized life-saving care.",
            "delhi_specific": "Maximum emergency. Contact transplant center or specialized facility immediately. Emergency evacuation may be necessary."
        }
    }
}


def get_aqi_category(aqi_value: float) -> str:
    """
    Determine the AQI category based on EPA standards with Delhi NCR extensions.
    
    Args:
        aqi_value: The AQI numeric value
        
    Returns:
        The AQI category name
    """
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
    """
    Determine the user's risk profile based on their health conditions.
    Enhanced for Delhi NCR population with specific focus on vulnerable groups.
    
    Args:
        health_conditions: List of health conditions
        
    Returns:
        The risk profile (general, children, teens, pregnant, elderly, sensitive, high_risk, critical)
    """
    if not health_conditions:
        return RiskProfile.GENERAL.value
    
    # Convert to lowercase for case-insensitive matching
    conditions_lower = [condition.lower().strip() for condition in health_conditions]
    
    # Critical conditions - multiple severe issues or immunocompromised
    critical_conditions = {
        'transplant', 'organ transplant', 'immunocompromised', 'immune compromised',
        'chemotherapy', 'cancer treatment', 'hiv', 'aids', 'severe immunodeficiency',
        'multiple severe conditions', 'icu patient', 'ventilator'
    }
    
    # High-risk conditions - severe chronic diseases
    high_risk_conditions = {
        'copd', 'chronic obstructive pulmonary', 'emphysema', 'severe asthma',
        'heart disease', 'cardiovascular disease', 'heart failure', 'cardiac',
        'lung cancer', 'pulmonary fibrosis', 'cystic fibrosis', 'bronchiectasis',
        'stroke history', 'recent surgery', 'severe cardiac'
    }
    
    # Sensitive conditions - mild to moderate respiratory/cardiac issues
    sensitive_conditions = {
        'asthma', 'mild asthma', 'allergies', 'bronchitis', 'sinus',
        'respiratory infection', 'pneumonia', 'allergy', 'wheeze',
        'breathing problem', 'lung issue', 'heart condition'
    }
    
    # Age and pregnancy specific markers
    children_markers = {'child', 'children', 'kid', 'infant', 'toddler', 'baby', 'under 12', 'age 0-12'}
    teen_markers = {'teen', 'teenager', 'adolescent', 'age 13-18', 'youth', 'student'}
    pregnant_markers = {'pregnant', 'pregnancy', 'expecting', 'expectant', 'gravid', 'prenatal'}
    elderly_markers = {'elderly', 'senior', 'old age', 'aged', '60+', 'over 60', 'geriatric'}
    
    # Check for critical conditions first (highest priority)
    for condition in conditions_lower:
        for critical in critical_conditions:
            if critical in condition:
                return RiskProfile.CRITICAL.value
    
    # Check for pregnancy (high priority for vulnerable group)
    for condition in conditions_lower:
        for pregnant in pregnant_markers:
            if pregnant in condition:
                return RiskProfile.PREGNANT.value
    
    # Check for age groups
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
    
    # Check for high-risk conditions
    for condition in conditions_lower:
        for high_risk in high_risk_conditions:
            if high_risk in condition:
                return RiskProfile.HIGH_RISK.value
    
    # Check for sensitive conditions
    for condition in conditions_lower:
        for sensitive in sensitive_conditions:
            if sensitive in condition:
                return RiskProfile.SENSITIVE.value
    
    # Default to sensitive if any condition is listed but not specifically recognized
    # (better to be cautious)
    return RiskProfile.SENSITIVE.value if health_conditions else RiskProfile.GENERAL.value


def get_personalized_recommendation(
    aqi_value: float,
    user_health_conditions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate personalized recommendations based on AQI and user health profile.
    
    This is the main "brain" function that analyzes the air quality and user's
    health profile to provide tailored, balanced advice without causing panic.
    
    Args:
        aqi_value: Current AQI value
        user_health_conditions: List of user's health conditions (optional)
        
    Returns:
        Dictionary containing personalized recommendations
    """
    if user_health_conditions is None:
        user_health_conditions = []
    
    # Determine AQI category and risk profile
    aqi_category = get_aqi_category(aqi_value)
    risk_profile = determine_risk_profile(user_health_conditions)
    
    # Get the appropriate recommendation from knowledge base
    category_data = AQI_RULE_KNOWLEDGE_BASE.get(aqi_category, {})
    recommendation_data = category_data.get(risk_profile, {})
    
    # Fallback to general if specific profile not found
    if not recommendation_data:
        recommendation_data = category_data.get("general", {})
    
    # Build the response
    response = {
        "aqi_value": aqi_value,
        "aqi_category": aqi_category,
        "aqi_range": category_data.get("aqi_range", (0, 0)),
        "color": category_data.get("color", "#000000"),
        "risk_profile": risk_profile,
        "health_conditions": user_health_conditions,
        "delhi_context": category_data.get("delhi_context", ""),
        "summary": recommendation_data.get("summary", "Air quality information not available."),
        "recommended_activities": recommendation_data.get("activities", []),
        "precautions": recommendation_data.get("precautions", []),
        "health_implications": recommendation_data.get("health_implications", ""),
        "delhi_specific": recommendation_data.get("delhi_specific", ""),
        "timestamp": None,  # Will be added by the API endpoint
        "urgency_level": _get_urgency_level(aqi_category, risk_profile)
    }
    
    return response


def _get_urgency_level(aqi_category: str, risk_profile: str) -> str:
    """
    Determine the urgency level of the alert.
    Balanced to inform without causing unnecessary panic.
    
    Args:
        aqi_category: The AQI category
        risk_profile: The user's risk profile
        
    Returns:
        Urgency level (info, caution, warning, serious, critical, emergency)
    """
    urgency_matrix = {
        "Good": {
            "general": "info", "children": "info", "teens": "info",
            "pregnant": "info", "elderly": "info", "sensitive": "info",
            "high_risk": "info", "critical": "caution"
        },
        "Moderate": {
            "general": "info", "children": "caution", "teens": "caution",
            "pregnant": "caution", "elderly": "caution", "sensitive": "caution",
            "high_risk": "warning", "critical": "warning"
        },
        "Unhealthy for Sensitive Groups": {
            "general": "caution", "children": "warning", "teens": "warning",
            "pregnant": "warning", "elderly": "warning", "sensitive": "warning",
            "high_risk": "serious", "critical": "serious"
        },
        "Unhealthy": {
            "general": "warning", "children": "serious", "teens": "serious",
            "pregnant": "serious", "elderly": "serious", "sensitive": "serious",
            "high_risk": "critical", "critical": "critical"
        },
        "Very Unhealthy": {
            "general": "serious", "children": "critical", "teens": "critical",
            "pregnant": "critical", "elderly": "critical", "sensitive": "critical",
            "high_risk": "emergency", "critical": "emergency"
        },
        "Hazardous": {
            "general": "critical", "children": "emergency", "teens": "emergency",
            "pregnant": "emergency", "elderly": "emergency", "sensitive": "emergency",
            "high_risk": "emergency", "critical": "emergency"
        },
        "Severe": {
            "general": "emergency", "children": "emergency", "teens": "emergency",
            "pregnant": "emergency", "elderly": "emergency", "sensitive": "emergency",
            "high_risk": "emergency", "critical": "emergency"
        },
        "Severe+": {
            "general": "emergency", "children": "emergency", "teens": "emergency",
            "pregnant": "emergency", "elderly": "emergency", "sensitive": "emergency",
            "high_risk": "emergency", "critical": "emergency"
        }
    }
    
    return urgency_matrix.get(aqi_category, {}).get(risk_profile, "warning")


def get_aqi_trend_advice(current_aqi: float, forecasted_aqi: List[float]) -> Dict[str, Any]:
    """
    Provide balanced advice based on AQI trends over the forecast period.
    
    Args:
        current_aqi: Current AQI value
        forecasted_aqi: List of forecasted AQI values for the next 24 hours
        
    Returns:
        Dictionary containing trend analysis and advice
    """
    if not forecasted_aqi:
        return {"trend": "unknown", "advice": "No forecast data available."}
    
    avg_forecast = sum(forecasted_aqi) / len(forecasted_aqi)
    max_forecast = max(forecasted_aqi)
    min_forecast = min(forecasted_aqi)
    
    # Determine trend
    if avg_forecast > current_aqi + 30:
        trend = "worsening"
        advice = f"Air quality expected to worsen. Plan indoor activities and prepare protective measures. Peak AQI may reach {max_forecast:.0f}."
    elif avg_forecast < current_aqi - 30:
        trend = "improving"
        advice = f"Air quality expected to improve. Better conditions anticipated. Lowest AQI may be {min_forecast:.0f}."
    else:
        trend = "stable"
        advice = f"Air quality expected to remain similar around {avg_forecast:.0f}. Current protective measures should continue."
    
    return {
        "trend": trend,
        "current_aqi": current_aqi,
        "average_forecast": round(avg_forecast, 1),
        "max_forecast": round(max_forecast, 1),
        "min_forecast": round(min_forecast, 1),
        "advice": advice,
        "best_time_window": _find_best_time_window(forecasted_aqi)
    }


def _find_best_time_window(forecasted_aqi: List[float]) -> str:
    """
    Find the best time window (lowest AQI period) in the forecast.
    
    Args:
        forecasted_aqi: List of hourly AQI forecasts
        
    Returns:
        Description of the best time window
    """
    if not forecasted_aqi:
        return "No forecast available"
    
    min_aqi = min(forecasted_aqi)
    min_index = forecasted_aqi.index(min_aqi)
    
    # Convert index to hours from now
    if min_index <= 3:
        return f"Next {min_index + 1} hours (AQI ~{min_aqi:.0f})"
    elif min_index <= 12:
        return f"Around {min_index} hours from now (AQI ~{min_aqi:.0f})"
    else:
        return f"Later today, around hour {min_index} (AQI ~{min_aqi:.0f})"


def get_delhi_specific_context(aqi_value: float, risk_profile: str) -> Dict[str, Any]:
    """
    Provide Delhi NCR-specific contextual information and resources.
    
    Args:
        aqi_value: Current AQI value
        risk_profile: User's risk profile
        
    Returns:
        Dictionary with Delhi-specific context and resources
    """
    aqi_category = get_aqi_category(aqi_value)
    
    # Delhi NCR medical facilities by category
    medical_facilities = {
        "respiratory": ["AIIMS Delhi", "RML Hospital", "VP Chest Institute", "Max Hospital", "Fortis Hospital"],
        "cardiac": ["Escorts Heart Institute", "Fortis Escorts", "AIIMS Delhi", "Max Hospital"],
        "pediatric": ["Safdarjung Hospital", "Max Hospital", "Fortis Hospital", "AIIMS Delhi"],
        "maternity": ["Sir Ganga Ram Hospital", "Max Hospital", "Safdarjung Hospital", "AIIMS Delhi"]
    }
    
    # GRAP (Graded Response Action Plan) stage mapping
    grap_stage = "Stage 1"
    if aqi_value > 200:
        grap_stage = "Stage 3 - Severe"
    elif aqi_value > 300:
        grap_stage = "Stage 4 - Severe+"
    elif aqi_value > 400:
        grap_stage = "Stage 4 - Emergency"
    
    # Seasonal context
    import datetime
    month = datetime.datetime.now().month
    seasonal_note = ""
    if month in [10, 11, 12, 1, 2]:
        seasonal_note = "Winter pollution season in Delhi NCR. Air quality typically worst Oct-Feb due to stubble burning, low wind, and temperature inversion."
    elif month in [6, 7, 8, 9]:
        seasonal_note = "Monsoon season. Rain helps clear pollution temporarily. Air quality generally better during this period."
    else:
        seasonal_note = "Pre-summer period. Dust storms common. Air quality variable but generally better than winter months."
    
    context = {
        "grap_stage": grap_stage,
        "seasonal_context": seasonal_note,
        "typical_for_delhi": aqi_value >= 150,  # AQI 150+ is common in winter
        "medical_facilities": medical_facilities,
        "emergency_numbers": {
            "ambulance": "102",
            "pollution_helpline": "1800-11-0099",
            "health_emergency": "108"
        },
        "government_measures": _get_government_measures(aqi_category),
        "local_tips": _get_delhi_local_tips(aqi_category, risk_profile)
    }
    
    return context


def _get_government_measures(aqi_category: str) -> List[str]:
    """Get typical government measures for the AQI level"""
    measures = {
        "Good": ["No restrictions", "Normal activities permitted"],
        "Moderate": ["Monitor air quality", "Sensitive groups advised caution"],
        "Unhealthy for Sensitive Groups": [
            "Construction dust control measures",
            "Vehicle pollution checks increased",
            "Public advisories issued"
        ],
        "Unhealthy": [
            "Construction activities restricted",
            "Schools may declare pollution holidays",
            "Vehicle restrictions may be imposed",
            "Public health advisories active"
        ],
        "Very Unhealthy": [
            "GRAP Stage 3 activated",
            "Schools closed or online classes",
            "Construction banned",
            "Vehicle restrictions in place",
            "Emergency health measures"
        ],
        "Hazardous": [
            "GRAP Stage 4 activated",
            "Schools closed",
            "Construction completely banned",
            "Odd-even vehicle scheme possible",
            "Non-essential commercial activities restricted",
            "Emergency health services on alert"
        ],
        "Severe": [
            "Full emergency measures",
            "Possible lockdown considerations",
            "All non-essential activities stopped",
            "Maximum vehicle restrictions",
            "Emergency health protocols"
        ],
        "Severe+": [
            "Maximum emergency response",
            "Complete lockdown possible",
            "Only essential services operating",
            "Emergency evacuation advisories may be issued",
            "Full medical emergency protocols"
        ]
    }
    return measures.get(aqi_category, ["Monitor official announcements"])


def _get_delhi_local_tips(aqi_category: str, risk_profile: str) -> List[str]:
    """Get practical Delhi NCR-specific tips"""
    
    base_tips = [
        "Check AQI before planning outdoor activities",
        "Keep N95 masks ready at all times",
        "Invest in good quality air purifiers for home",
        "Keep emergency medications stocked"
    ]
    
    if aqi_category in ["Unhealthy", "Very Unhealthy", "Hazardous", "Severe", "Severe+"]:
        delhi_tips = [
            "Avoid areas near construction sites and high-traffic roads",
            "Morning hours (before 9 AM) typically have better air quality",
            "Keep windows closed between 6-10 PM when pollution peaks",
            "Use air-conditioned transport when going out",
            "Indoor plants like snake plant and money plant can help marginally",
            "Stay hydrated - drink warm water throughout the day",
            "Consider air quality apps for real-time monitoring"
        ]
        
        if risk_profile in ["pregnant", "children", "elderly", "high_risk", "critical"]:
            delhi_tips.extend([
                "Many Delhi NCR residents temporarily relocate to hill stations during peak pollution",
                "Consult your doctor about whether temporary relocation is advisable",
                "Keep medical records and prescriptions organized for emergencies",
                "Register with nearby hospitals for quick emergency access"
            ])
        
        return base_tips + delhi_tips
    
    return base_tips


# Utility function for API responses
def format_recommendation_for_display(recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the recommendation for user-friendly display.
    Ensures the message is clear, actionable, and not panic-inducing.
    
    Args:
        recommendation: Raw recommendation dictionary
        
    Returns:
        Formatted recommendation suitable for display
    """
    # Add visual indicators based on urgency
    urgency_icons = {
        "info": "ℹ️",
        "caution": "⚠️",
        "warning": "⚠️",
        "serious": "🚨",
        "critical": "🚨",
        "emergency": "🆘"
    }
    
    urgency = recommendation.get("urgency_level", "info")
    icon = urgency_icons.get(urgency, "ℹ️")
    
    # Create a balanced, informative summary
    formatted = {
        "icon": icon,
        "urgency_level": urgency,
        "urgency_label": urgency.upper(),
        "aqi_value": recommendation["aqi_value"],
        "aqi_category": recommendation["aqi_category"],
        "color": recommendation["color"],
        "risk_profile": recommendation["risk_profile"],
        "main_message": f"{icon} {recommendation['summary']}",
        "health_implications": recommendation["health_implications"],
        "what_to_do": {
            "recommended": recommendation["recommended_activities"],
            "precautions": recommendation["precautions"]
        },
        "delhi_context": recommendation.get("delhi_specific", ""),
        "timestamp": recommendation.get("timestamp")
    }
    
    return formatted