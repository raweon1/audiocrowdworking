label_en = {
    "base:": ["Evaluation of audio-samples"],
    "qualification_job_introduction": ["Introduction",
                                       "We are looking for workers who are willing to participate in a speech quality "
                                       "assessment experiment. During the test you will be listening to short groups "
                                       "of sentences (4-6) seconds via your listening device and giving your opinion "
                                       "of the speech you hear. In each task you will listen to X audio files and give "
                                       "your opinion for each on the following scale:",
                                       "Each task can be completed in Y minutes. There will be a total of Z tasks "
                                       "available for each worker",
                                       "Procedure",
                                       "The procedure is as following:",
                                       "To get access to the quality assessment job, you should first complete this "
                                       "qualification job.",
                                       "Selected group of workers will be invited to perform the training job "
                                       "(B minutes) in which you will listen to C sample audio files",
                                       "Then, they get access to the quality assessment job and can perform up "
                                       "to D tasks",
                                       "It is expected that you perform the task in a quiet environment!",
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
                                    "Submit"],
    "acr_job_rate": ["Sample",
                     "previous",
                     "next",
                     "Submit"],
    "acr_job_setup": ["Welcome",
                      "Placeholder",
                      "Payment",
                      "Placeholder",
                      "Setup",
                      "Please perform this task in a quiet environment!",
                      "Ready"],
    "acr_scale": ["Quality of the speech",
                  "Score",
                  "Excellent",
                  "Good",
                  "Fair",
                  "Poor",
                  "Bad"],
    "calibrate": ["Please modify the listening volume of your device to a comfortable level when hearing the following "
                  "audio file.",
                  "IMPORTANT: After that, you are not allowed to change the volume anymore. If you do, your "
                  "response will be discarded!"],
}

label_de = {
    "base": ["Bewertung von Audiodateien"],
    "qualification_job_introduction": ["Einleitung",
                                       "Wir suchen Arbeiter die bei einer Studie über die Qualität von Sprache "
                                       "mitmachen. Während des Tests werden Sie kurze Sätze (5-10 Sekunden) mit ihrem "
                                       "Lautsprecher anhören und anschließend diese bewerten. Sie werden ca. 10 Sätze "
                                       "auf der folgenden Skala bewerten:",
                                       "Diese Aufgabe können sie in ca. 2-3 Minuten beenden.",
                                       "Prozedur",
                                       "Der Ablauf ist wie folgt:",
                                       "Sie müssen die nachfolgende Qualifikation absolvieren.",
                                       "Danach müssen sie ein kleines Training durchführen bei dem sie 4 Audiodateien "
                                       "zur Übung anhören",
                                       "Nach dem Training haben sie 60 Minuten Zeit um Audiodateien zu bewerten. "
                                       "Sie können diese Campaign öfters aufrufen um neue Sätze zu bewerten.",
                                       "Wir erwarten das sie diese Aufgabe in einer ruhigen Umgebung ausführen!",
                                       "Weiter"],
    "qualification_job_questions": ["Allgemeine Fragen",
                                    "Bitte beantworten Sie die nachfolgenden Fragen:",
                                    "Was ist dein Geschlecht?",
                                    "Wann wurden sie geboren?",
                                    "Haben sie ein geschwächtes Gehör?",
                                    "Wann haben sie das letzte mal an einem Subjektiven Test teilgenommen?",
                                    "Wann haben sie das letzte mal an einem Sprachqualitätstest teilgenommen?",
                                    "Haben sie jemals im Bereich speech coding oder Ähnlichem gearbeitet?",
                                    "Abgeben"],
    "acr_job_rate": ["Aufgabe",
                     "vorher",
                     "nächstes",
                     "Abgeben"],
    "acr_job_setup": ["Willkommen",
                      "Nachdem sie dieses Setup beendet haben können Sie die Audiodateien bewerten. "
                      "Sie müssen jede Audiodatei vollständig und am Stück abgespielt haben um diese bewerten zu können. "
                      "Nachdem sie jede Audiodatei bewertet haben können Sie mittels des Abgabe-Buttons ihr Bewertungen "
                      "abgeben und die Aufgabe abschließen.",
                      "Bezahlung",
                      "Sie erhalten x€",
                      "Setup",
                      "Bitte bearbeiten Sie diese Aufgabe in einer ruhigen Umgebung!",
                      "Bereit"],
    "acr_scale": ["Sprachqualität",
                  "Ergebnis",
                  "Ausgezeichnet",
                  "Gut",
                  "Fair",
                  "Schlecht",
                  "Mies"],
    "calibrate": ["Bitte stellen sie die Lautstärke mittels der nachfolgenden Audiodatei auf ein komfortables Level ein.",
                  "WICHTIG: Ändern sie die Lautstärke NICHT mehr, sonst werden ihre Antworten verworfen!"]
}


def get_context_language(lang, site):
    if lang == "de":
        label = label_de
    elif lang == "en":
        label = label_en
    return {site: label[site]}
