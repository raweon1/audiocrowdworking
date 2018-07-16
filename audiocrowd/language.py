from copy import deepcopy
from .models import Campaign


labels = {
    "en": {
        "base": ["Contact"],
        "qualification_job_introduction": ["Introduction",
                                           "We are looking for workers who are willing to participate in a speech quality "
                                           "assessment experiment. During the test you will be listening to short groups "
                                           "of sentences (7-12 seconds) via your listening device and giving your opinion "
                                           "of the speech you hear on the following scale:",
                                           "In this task you will listen to 11 audio files.",
                                           "To complete this task you will have to do the following steps:",
                                           "First we will collect demographic data from you - Duration: ca 1. minute",
                                           "Then you have to do a short training where you listen to 3 audio files for "
                                           "practice - Duration: ca 2. minutes",
                                           "After completing the training you can rate the audiofiles and finish this "
                                           "task - Duration: ca. 5 minutes",
                                           "Completing the training will allow you to perform other campaigns for up to 60 "
                                           "minutes without redoing steps 1 and 2.",
                                           "It is expected that you perform the task in a quiet environment.",
                                           "Continue"],
        "qualification_job_questions": ["General Questions",
                                        "Please answer the following questions carefully:",
                                        "What is your gender? ",
                                        "In what year were you born? ",
                                        "Do you suffer from hearing loss? ",
                                        "When was the last time you participated in a subjective test? ",
                                        "When was the last time you participated in a speech quality assessment test? ",
                                        "Have you ever been directly involved in work connected with assessment of the "
                                        "performance of telephone circuits, or related work such as speech coding? ",
                                        "What type of listening device do you use for this task?",
                                        "Continue"],
        "qualification_job_questionnaire_meta": ["Questions",
                                                 "not applicable",
                                                 "almost never",
                                                 "occasionally",
                                                 "frequently",
                                                 "almost always",
                                                 "Submit"],
        "qualification_job_questionnaire": ["When you are watching a film in a cinema or a play in a theatre, are you able to understand what is being said (either on the screen or on stage) if people around you are rustling paper or whispering?",
                                            "Can you hear household sounds like those made by a fan, fridge, oven, dish washer, or a running tap?",
                                            "Do you have to concentrate really hard when you are listening to a voice on the radio?",
                                            "Are you able to hear the birds singing outside?",
                                            "Can you distinguish between a trumpet and a saxophone purely based on the sound they make?",
                                            "Can you tell how somebody is feeling from the sound of their voice?",
                                            "When you hear people or cars behind you, can you hear how far away they are?",
                                            "Can you tell from its sound how far away a bus or lorry is?",
                                            "When you hear a voice or footsteps behind you, can you tell in which direction (from left to right or right to left) that person is moving without looking round?",
                                            "Do you immediately turn your head in the correct direction when somebody calls you?",
                                            "Can you follow what somebody is saying when there is much reverberation, such as in a church or railway terminus (echoic) building. Can you follow what the other person is saying?",
                                            "Can you recognise family members by their voices alone?",
                                            "Can you easily have a quiet conversation with somebody you know in a quiet environment?",
                                            "Can you understand what is said without having to ask people to repeat themselves?",
                                            "When you are in a car on the motorway are you able to follow the news on the radio at a normal level?",
                                            "In a busy shop or supermarket, can you understand the checkout assistant when they are talking to you?",
                                            "Think of a time that you and four other people are in a busy restaurant and that you cannot see everybody. Are you able to follow the conversation?",
                                            "When you are travelling in a bus or a car, are you able to have a conversation with the person sitting next to you without difficulty?"],
        "training_job_setup": ["Training",
                               "Next you will get some audio files for review. The audio files may experience various "
                               "types of interference, which may affect the volume or quality of the sound, or cause "
                               "noise and exposure. Please rate for each audio file how you feel about its quality.",
                               "Setup",
                               "Please perform this task in a quiet environment.",
                               "The next 3 audio files are a training session to familiarize you with the user interface.",
                               "Continue"],
        "training_job_rate": ["Complete training"],
        "training_job_welcome_back": ["Welcome back to the evaluation of audio files. Since your last participation "
                                      "is already a long time behind, you have to complete the training again. We "
                                      "thank you for the renewed participation."],
        "acr_job_rate": ["Task",
                         "Done",
                         "Previous",
                         "Next",
                         "Submit"],
        "acr_job_setup": ["Setup - Evaluation of speech quality",
                          "After completing the training, the actual study begins. As in training, the audio "
                          "files may experience a variety of disturbances that can affect volume or voice "
                          "quality, or that can cause noise and exposure. Please rate for each audio file how "
                          "you feel about its quality.",
                          "Please perform this task in a quiet environment.",
                          "Continue"],
        "acr_job_end": ["VCODE",
                        "Thank you for your participation. Please use the following VCODE to complete the task:"],
        "acr_job_welcome_back": ["Audiotests",
                                 "Welcome back to our study on speech quality. Since you have already completed the "
                                 "training or one of our other tasks in the last 60 minutes, you can start directly "
                                 "with a new task. We thank you for your renewed participation.",
                                 "Continue"],
        "acr_scale": ["Quality of the speech",
                      "Score",
                      "Excellent",
                      "Good",
                      "Fair",
                      "Poor",
                      "Bad"],
        "display_stimulus": ["You have to listen to the audio file before rating",
                             "You can now rate the audio file"],
        "calibrate": [
            "Please modify the listening volume of your device to a comfortable level when hearing the following "
            "audio file.",
            "Please do not change the volume on your speakers anymore, since the volume of the audio files "
            "is also part of the test."],
        "campaign_is_full": ["Not available",
                             "All open positions in this campaign are currently being processed, please try one of our "
                             "other campaigns or try again later."]
    },
    "de": {
        "base": ["Kontakt"],
        "qualification_job_introduction": ["Einleitung",
                                           "Bei dieser Aufgabe werden Sie an einer Studie über Sprachqualität teilnehmen."
                                           " Während des Tests werden Sie kurze Sätze (ca. 7-12 Sekunden) mit Ihrem "
                                           "Wiedergabegerät anhören und anschließend diese auf folgender Skala bewerten:",
                                           "Nachdem Sie 11 Sätze bewertet haben können Sie die Aufgabe abschließen",
                                           "Um mit der Bewertung zu beginnen müssen Sie folgende Schritte absolvieren:",
                                           "Zuerst werden wir einige demografische Daten "
                                           "von Ihnen erheben - Dauer: ca. 1 Minute",
                                           "Danach müssen Sie ein kurzes Training durchführen bei dem Sie 3 Audiodateien "
                                           "zur Übung anhören - Dauer: ca. 2 Minuten",
                                           "Nach dem Training können Sie die Audiodateien bewerten und diese Aufgabe "
                                           "abschließen - Dauer: ca. 5 Minuten",
                                           "Der Abschluss des Trainings erlaubt es Ihnen für 60 Minuten andere Kampagnen "
                                           "ohne erneute Ausführung von Schritt 1 und 2 durchzuführen.",
                                           "Bitte bearbeiten Sie diese Aufgabe in einer ruhigen Umgebung.",
                                           "Weiter"],
        "qualification_job_questions": ["Demografische Daten",
                                        "Bitte beantworten Sie die nachfolgenden Fragen:",
                                        "Was ist Ihr Geschlecht?",
                                        "Wann wurden Sie geboren?",
                                        "Haben Sie eine Hörschädigung?",
                                        "Wann haben Sie das letzte mal an einem Subjektiven Test teilgenommen?",
                                        "Wann haben Sie das letzte mal an einem Sprachqualitätstest teilgenommen?",
                                        "Haben Sie jemals im Bereich Sprachkodierung oder Ähnlichem gearbeitet?",
                                        "Welchen Typ von Wiedergabegerät nutzen sie?",
                                        "Weiter",
                                        ["Mann", "Frau", "Andere"],
                                        ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
                                         "September", "Oktober", "November", "Dezember"],
                                        ["Niemals", "Vor 1 Monat", "Vor 3 Monaten", "Vor 6 Monaten",
                                         "Vor 9 Monaten", "Vor 1 Jahr oder länger"],
                                        ["Ja", "Nein"],
                                        ["Lautsprecher", "Kopfhörer", "In-Ear-Kopfhörer"]],
        "qualification_job_questionnaire_meta": ["Questions",
                                                 "not applicable",
                                                 "almost never",
                                                 "occasionally",
                                                 "frequently",
                                                 "almost always",
                                                 "Submit"],
        "qualification_job_questionnaire": ["When you are watching a film in a cinema or a play in a theatre, are you able to understand what is being said (either on the screen or on stage) if people around you are rustling paper or whispering?",
                                            "Can you hear household sounds like those made by a fan, fridge, oven, dish washer, or a running tap?",
                                            "Do you have to concentrate really hard when you are listening to a voice on the radio?",
                                            "Are you able to hear the birds singing outside?",
                                            "Can you distinguish between a trumpet and a saxophone purely based on the sound they make?",
                                            "Can you tell how somebody is feeling from the sound of their voice?",
                                            "When you hear people or cars behind you, can you hear how far away they are?",
                                            "Can you tell from its sound how far away a bus or lorry is?",
                                            "When you hear a voice or footsteps behind you, can you tell in which direction (from left to right or right to left) that person is moving without looking round?",
                                            "Do you immediately turn your head in the correct direction when somebody calls you?",
                                            "Can you follow what somebody is saying when there is much reverberation, such as in a church or railway terminus (echoic) building. Can you follow what the other person is saying?",
                                            "Can you recognise family members by their voices alone?",
                                            "Can you easily have a quiet conversation with somebody you know in a quiet environment?",
                                            "Can you understand what is said without having to ask people to repeat themselves?",
                                            "When you are in a car on the motorway are you able to follow the news on the radio at a normal level?",
                                            "In a busy shop or supermarket, can you understand the checkout assistant when they are talking to you?",
                                            "Think of a time that you and four other people are in a busy restaurant and that you cannot see everybody. Are you able to follow the conversation?",
                                            "When you are travelling in a bus or a car, are you able to have a conversation with the person sitting next to you without difficulty?"],
        "training_job_setup": ["Training",
                               "Im folgenden werden Sie einige Audiodateien zur Bewertung bekommen. Bei den Audiodateien "
                               "können verschiedene Störungen auftreten, die Lautstärke oder Sprachqualität beeinflussen "
                               "können oder zu Störgeräuschen und Aussetzen führen können. Bitte bewerten für jede "
                               "Audiodatei wie Sie deren Qualität empfinden.",
                               "Setup",
                               "Bitte bearbeiten Sie diese Aufgabe in einer ruhigen Umgebung.",
                               "Bei den nächsten 3 Audiodaten handelt es sich zunächst um ein Training, damit Sie sich mit "
                               "der Bedienoberfläche vertraut machen können",
                               "Weiter"],
        "training_job_rate": ["Training abschließen"],
        "training_job_welcome_back": [
            "Willkommen zurück zu unserer Studie über Sprachqualität. Da Ihre letzte Teilnahme "
            "schon länger zurück liegt, müssen Sie das Training noch einmal absolvieren. "
            "Wir danken Ihnen für die erneute Teilnahme."],
        "acr_job_rate": ["Aufgabe",
                         "Bearbeitet",
                         "zurück",
                         "weiter",
                         "Bewertung abgeben"],
        "acr_job_setup": ["Setup - Bewertung von Sprachqualität",
                          "Nachdem Sie das Training absolviert haben, beginnt nun die eigentliche Studie. Wie im Training "
                          "können bei den Audiodateien verschiedene Störungen auftreten, die Lautstärke oder "
                          "Sprachqualität beeinflussen können oder zu Störgeräuschen und Aussetzen führen können. Bitte "
                          "bewerten Sie für jede Audiodatei wie Sie deren Qualität empfinden.",
                          "Bitte bearbeiten Sie diese Aufgabe in einer ruhigen Umgebung.",
                          "Weiter"],
        "acr_job_end": ["VCODE",
                        "Danke für Ihre Mitarbeit. Bitte nutzen Sie folgenden VCODE zum Abschluss der Aufgabe:"],
        "acr_job_welcome_back": ["Audiotests",
                                 "Willkommen zurück zu unserer Studie über Sprachqualität. Da Sie bereits in den letzten "
                                 "60 Minuten das Training oder eine unserer Aufgaben abgeschlossen haben, können Sie "
                                 "direkt mit einer neuen Aufgabe beginnen. Wir danken Ihnen für Ihre erneute Teilnahme.",
                                 "Weiter"],
        "acr_scale": ["Sprachqualität",
                      "Ergebnis",
                      "Ausgezeichnet",
                      "Gut",
                      "Ordentlich",
                      "Dürftig",
                      "Schlecht"],
        "display_stimulus": ["Sie müssen die Audiodatei vor dem Bewerten anhören",
                             "Sie können die Audiodatei nun bewerten"],
        "calibrate": [
            "Bitte stellen Sie die Lautstärke mittels der nachfolgenden Audiodatei auf ein komfortables Level ein.",
            "Bitte ändern Sie die Lautstärke auch an Ihren Lautsprechern nicht mehr, da die Laustärke der "
            "Audiodateien ebenfalls Bestandteil des Tests ist."],
        "campaign_is_full": ["Nicht Verfügbar",
                             "Derzeit sind alle offenen Positionen dieser Kampagne in Bearbeitung, bitte versuchen Sie "
                             "eine unserer anderen Kampagnen oder versuchen Sie es später erneut."]
    },
}


def get_context(campaign, *args):
    context = dict()
    context["language"] = campaign.language
    context["base"] = deepcopy(labels[campaign.language]["base"])
    context["contact"] = campaign.contact_link
    for arg in args:
        context[arg] = deepcopy(labels[campaign.language][arg])
    return context
