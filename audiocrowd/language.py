
language = "en"

label_en = {
    "general_questions_gender": "What is your gender? ",
    "general_questions_birth_year": "In what year were you born? ",
    "general_questions_hearing_loss": "Do you suffer from hearing loss? ",
    "general_questions_subjective_test": "When was the last time you participated in a subjective test? ",
    "general_questions_speech_test": "When was the last time you participated in a speech quality assessment test? ",
    "general_questions_connected": "Have you ever been directly involved in work connected with assessment of the performance of telephone circuits, or related work such as speech coding? ",
}

def get_text(keyword):
    if language == "en":
        return label_en[keyword]