# AI Configuration for Chrono Grader
# Adjust these settings to make the AI smarter and more accurate

# OpenAI Model Settings
AI_MODEL = "gpt-4"  # Options: "gpt-3.5-turbo", "gpt-4"
AI_TEMPERATURE = 0.1  # Lower = more consistent, Higher = more creative
AI_MAX_TOKENS = 800  # Maximum response length

# Grading Strictness
GRADING_STRICTNESS = {
    "math_tolerance": 0.01,  # Tolerance for numerical answers
    "require_work_shown": False,  # Whether to require work to be shown
    "partial_credit": True,  # Whether to give partial credit
    "spelling_matters": False,  # Whether spelling affects math grades
}

# Verification Settings
ENABLE_MATH_VERIFICATION = True  # Double-check math problems automatically
ENABLE_CONFIDENCE_THRESHOLD = True  # Only grade if AI is confident
CONFIDENCE_THRESHOLD = 0.8  # Minimum confidence level (0.0 to 1.0)

# Subject-Specific Settings
SUBJECT_CONFIGS = {
    "math": {
        "require_units": False,  # Require units in answers
        "decimal_places": 2,  # Round answers to this many decimal places
        "accept_equivalent_forms": True,  # Accept 1/2 = 0.5 = 50%
    },
    "science": {
        "require_units": True,
        "significant_figures": True,
        "formula_partial_credit": True,
    },
    "english": {
        "grammar_weight": 0.3,  # How much grammar affects score
        "content_weight": 0.7,  # How much content affects score
        "allow_creative_answers": True,
    }
}

# Advanced AI Prompting
SYSTEM_PROMPTS = {
    "math_teacher": """You are an expert mathematics teacher with 20+ years of experience. 
    You grade assignments carefully, focusing on mathematical correctness and student understanding. 
    Always double-check calculations before marking answers wrong. Give partial credit for correct methods.""",
    
    "science_teacher": """You are an experienced science teacher who understands that students 
    may express correct concepts in different ways. Focus on understanding rather than exact wording.""",
    
    "general_teacher": """You are a fair and encouraging teacher who provides constructive feedback. 
    Look for what students did right before focusing on mistakes."""
}

# Error Handling
RETRY_ON_ERROR = True
MAX_RETRIES = 3
FALLBACK_TO_BASIC_GRADING = True  # Use simple keyword matching if AI fails
