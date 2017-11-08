from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.forms import ModelForm, SelectDateWidget
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from .models import Stimuli, GoldStandardQuestions, Worker, Rating, GoldStandardAnswers, Configuration, RatingSet, Campaign
from .language import get_context_language

from datetime import timedelta
from random import randint

job_list = dict(register="register", qualification="qualification_job", training="training_job", acr="acr_job")

qualification_job_tasks = dict(introduction="introduction", questions="general_questions")
training_job_tasks = dict(setup="setup", samples="samples")
acr_job_tasks = dict(setup="setup", rate="rate", next="next", done="done")

task_list = {
    job_list['qualification']: qualification_job_tasks,
    job_list['training']: training_job_tasks,
    job_list['acr']: acr_job_tasks,
}

link_list = {
    job_list['register']: "/audio/register",
    job_list['qualification']: "/audio/qualification/",
    job_list['training']: "/audio/training/",
    job_list['acr']: "/audio/acr/",
}


# TODO allgemein was mir gerade einfällt
# qualification general questions evaluation
# payment auf acr_next


def index(request):
    return HttpResponse("Hello world")


class NotRegisteredException(Exception):
    pass


class WrongJobException(Exception):
    pass


def get_task(request):
    try:
        return request.session["task"]
    except KeyError:
        raise NotRegisteredException


def get_job(request):
    try:
        return request.session["job"]
    except KeyError:
        raise NotRegisteredException


def is_registered(request):
    try:
        campaign = Campaign.objects.get(campaign_id=request.session["campaign"])
        worker = Worker.objects.get(name=request.session["worker"])
    except KeyError:
        raise NotRegisteredException()
    except ObjectDoesNotExist:
        raise NotRegisteredException()
    return worker, campaign


def correct_job(request, job):
    job_todo = get_job(request)
    if job != job_todo:
        raise WrongJobException


def stuff(request, called_job):
    try:
        worker, campaign = is_registered(request)
        correct_job(request, called_job)
        task = get_task(request)
    except NotRegisteredException:
        return True, HttpResponseBadRequest("You are not registered"), None, None, None
    except WrongJobException:
        return True, HttpResponseRedirect(link_list[get_job(request)]), None, None, None
    return False, None, worker, campaign, task


def redirect_to(request, job, task):
    request.session["job"] = job
    request.session["task"] = task
    return HttpResponseRedirect(link_list[job])


# localhost:8000/audio/register?workerid=1337&campaignid=hallo
def register(request):
    campaign_id = request.GET.get("campaignid")
    worker_id = request.GET.get("workerid")
    if not (campaign_id and worker_id):
        error = '<div align="center">BadRequest 400<br>'
        if not campaign_id:
            error = error + 'Expected argument "campaignid"<br>'
        if not worker_id:
            error = error + 'Expected argument "workerid"<br>'
        error = error + "</div>"
        return HttpResponseBadRequest(error)
    request.session["campaign"] = campaign_id
    request.session["worker"] = worker_id
    try:
        Campaign.objects.get(campaign_id=campaign_id)
    except ObjectDoesNotExist:
        request.session.flush()
        return HttpResponseBadRequest("Campaign " + campaign_id + " does not exist")
    # session wird beendet wenn der browser geschlossen wird
    request.session.set_expiry(0)
    worker, created = Worker.objects.get_or_create(name=worker_id)
    if created:
        return redirect_to(request, job_list['qualification'], task_list[job_list['qualification']]['introduction'])
    else:
        if not worker.qualification_done:
            return redirect_to(request, job_list['qualification'], task_list[job_list['qualification']]['introduction'])
        elif not worker.access_training:
            return HttpResponse("You are not qualified to participate")
        return redirect_to(request, job_list['training'], task_list[job_list['training']]['setup'])


class GeneralQuestionsForm(ModelForm):
    class Meta:
        model = Worker
        fields = ("gender", "birth_year", "hearing_loss", "subjective_test", "speech_test", "connected")
        widgets = {
            "birth_year": SelectDateWidget(years=[y for y in range(1930, 2050)])
        }

    def __init__(self, labels, *args, **kwargs):
        super(GeneralQuestionsForm, self).__init__(*args, **kwargs)
        self.fields["gender"].label = labels[2]
        self.fields["birth_year"].label = labels[3]
        self.fields["hearing_loss"].label = labels[4]
        self.fields["subjective_test"].label = labels[5]
        self.fields["speech_test"].label = labels[6]
        self.fields["connected"].label = labels[7]


def qualification_job_view(request):
    error, http, worker, campaign, task = stuff(request, job_list['qualification'])
    if error:
        return http

    if task == task_list[job_list['qualification']]['introduction']:
        if request.method == "POST":
            return redirect_to(request, job_list['qualification'], task_list[job_list['qualification']]['questions'])
        else:
            context = dict(list(get_context_language(campaign.language, "base").items()) +
                           list(get_context_language(campaign.language, "qualification_job_introduction").items()) +
                           list(get_context_language(campaign.language, "acr_scale").items()))
            return render(request, "audiocrowd/qualification_job_introduction.html", context)
    elif task == task_list[job_list['qualification']]['questions']:
        if request.method == "POST":
            labels = get_context_language(campaign.language, "qualification_job_questions")["qualification_job_questions"]
            form = GeneralQuestionsForm(labels, data=request.POST, instance=worker)
            if form.is_valid():
                form.save()
                worker.qualification_done = True
                worker.save()
                # TODO evaluation! wenn Zugang gewährt wird muss worker.access_training auf True gesetzt werden
                worker.access_training = True
                worker.save()
                return redirect_to(request, job_list['training'], task_list[job_list['training']]["setup"])
            else:
                # Die Form ist immer valid!
                return HttpResponse("Form is invalid")
        else:
            context = dict(list(get_context_language(campaign.language, "base").items()) +
                           list(get_context_language(campaign.language, "qualification_job_questions").items()))
            form = GeneralQuestionsForm(context["qualification_job_questions"], instance=worker)
            context["form"] = form
            return render(request, "audiocrowd/qualification_job_questions.html", context)


def require_training(worker):
    return now() > worker.access_acr


def get_training_stimuli_to_rate_context(campaign):
    available_stimuli = campaign.training_stimuli.all()
    count = available_stimuli.__len__() + 1
    stimuli_to_rate = []
    for i in range(1, count):
        if available_stimuli.__len__() == 0:
            break
        rnd = randint(0, available_stimuli.__len__() - 1)
        stimuli_to_rate.append((i, available_stimuli[rnd]))
        available_stimuli = available_stimuli.exclude(name=available_stimuli[rnd].name)
    print(stimuli_to_rate)
    return stimuli_to_rate


def training_job_view(request):
    error, http, worker, campaign, task = stuff(request, job_list['training'])
    if error:
        return http

    if require_training(worker):
        if task == task_list[job_list['training']]["setup"]:
            if request.method == "POST":
                request.session["calibrate"] = request.POST.dict()["calibrate"]
                return redirect_to(request, job_list["training"], task_list[job_list['training']]["samples"])
            else:
                context = dict(list(get_context_language(campaign.language, "base").items()) +
                               list(get_context_language(campaign.language, "training_job_setup").items()) +
                               list(get_context_language(campaign.language, "calibrate").items()))
                context["calibrate_stimulus"] = campaign.calibrate_stimulus
                return render(request, "audiocrowd/training_setup.html", context)
        elif task == task_list[job_list['training']]["samples"]:
            if request.method == "POST":
                worker.access_acr = now() + timedelta(minutes=Configuration.load().access_window)
                worker.save()
                return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['setup'])
            else:
                context = dict(list(get_context_language(campaign.language, "base").items()) +
                               list(get_context_language(campaign.language, "acr_job_rate").items()) +
                               list(get_context_language(campaign.language, "acr_scale").items()))
                context["to_rate"] = get_training_stimuli_to_rate_context(campaign)
                context["volume"] = request.session["calibrate"]
                return render(request, "audiocrowd/acr_job_rate.html", context)
    return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['setup'])


# @param: count = max. Anzahl von zu bearbeitenden Stimuli
# @param: worker = Der aktuelle Arbeiter
# @param: campaign = Die Campaign über die der Arbeiter kommt
# @return: gibt eine Liste von Stimuli zurück, die von <worker> bisher nicht bearbeitet wurden. Die Reihenfolge ist zufällig. Stimuli stehen in Verbindung mit campaign.
# @return: Liste kann leer sein, wenn keine Stimuli mehr zu bewerten sind.
def get_stimuli_to_rate(count, worker, campaign):
    available_stimuli = campaign.stimuli.all().exclude(rating__rating_set__worker=worker)
    stimuli_to_rate = []
    for i in range(0, count):
        if available_stimuli.__len__() == 0:
            break
        rnd = randint(0, available_stimuli.__len__() - 1)
        stimuli_to_rate.append(available_stimuli[rnd])
        available_stimuli = available_stimuli.exclude(name=available_stimuli[rnd].name)
    return stimuli_to_rate


# @param: siehe get_stimuli_to_rate
# @return: gibt eine Liste von Stimuli UND einer GoldStandardQuestion zurück, die von <worker> bisher nicht bearbeitet wurden. Die Reihenfolge ist zufällig.
# @return: Liste kann leer sein, wenn keine Stimuli ODER GoldStandardQuestions mehr zur Verfügung stehen.
def get_set_to_rate(count, worker, campaign):
    set_to_rate = get_stimuli_to_rate(count, worker, campaign)
    if set_to_rate.__len__() == 0:
        return set_to_rate
    available_gold_standard_questions = campaign.gold_standard_questions.all()
    if available_gold_standard_questions.__len__() == 0:
        return []
    for i in range(0, campaign.gold_standard_per_job):
        rnd = randint(0, available_gold_standard_questions.__len__() - 1)
        set_to_rate.insert(randint(0, set_to_rate.__len__() - 1), available_gold_standard_questions[rnd])
        available_gold_standard_questions = available_gold_standard_questions.exclude(
            name=available_gold_standard_questions[rnd].name)
    return set_to_rate


def get_or_create_session_set_to_rate(request, worker, campaign):
    try:
        serialized_set_to_rate = request.session["set_to_rate"]
        set_to_rate = []
        for obj in serializers.deserialize("xml", serialized_set_to_rate):
            set_to_rate.append(obj.object)
        # nach del request.session["set_to_rate"] ist set_to_rate leer, jedoch wird kein KeyError erzeugt
        if set_to_rate.__len__() == 0:
            set_to_rate = get_set_to_rate(campaign.stimuli_per_job, worker, campaign)
            request.session["set_to_rate"] = serializers.serialize("xml", set_to_rate)
    except KeyError:
        set_to_rate = get_set_to_rate(campaign.stimuli_per_job, worker, campaign)
        request.session["set_to_rate"] = serializers.serialize("xml", set_to_rate)
    return set_to_rate


# @param: eine Liste von Stimuli und GoldStandardQuestions
# @return: eine Liste mit einem Tupel (Index, Object) für jeden Eintrag in der @param-Liste
def get_set_to_rate_context(set_to_rate):
    context_set = []
    for i in range(1, set_to_rate.__len__() + 1):
        context_set.append((i, set_to_rate[i - 1]))
    return context_set


# Funktion soll den Namen eines Stimulus von einem Key key aus dem Dict von acr_job_rate.html geben. Falls key != stimulus.name ist, muss diese Funktion
# für parse_name_from_key(key) == stimulus.name sorgen
def parse_name_from_key(key):
    return key


def parse_rating_form(form_dict):
    stimuli = {}
    gold_standard = {}
    for key in list(form_dict.keys()):
        try:
            stimulus = Stimuli.objects.get(name=parse_name_from_key(key))
            stimuli[key] = {
                    "object": stimulus,
                    "rating": form_dict[key]
                }
            del form_dict[key]
        except ObjectDoesNotExist:
            try:
                gold_standard_question = GoldStandardQuestions.objects.get(name=parse_name_from_key(key))
                gold_standard[key] = {
                    "object": gold_standard_question,
                    "rating": form_dict[key]
                }
                del form_dict[key]
            except ObjectDoesNotExist:
                pass
    # find more values like "{{stimuli.name}}_volume"
    for stimulus in stimuli:
        for key in list(form_dict.keys()):
            if stimulus in key:
                stimuli[stimulus][key.replace(stimulus + "_", "")] = form_dict[key]
                del form_dict[key]
    for gold_standard_question in gold_standard:
        for key in list(form_dict.keys()):
            if gold_standard_question in key:
                gold_standard[gold_standard_question][key.replace(gold_standard_question + "_", "")] = form_dict[key]
                del form_dict[key]
    return form_dict, stimuli, gold_standard


def acr_job_view(request):
    error, http, worker, campaign, task = stuff(request, job_list['acr'])
    if error:
        return http

    if task == task_list[job_list['acr']]['setup']:
        if request.method == "POST":
            # nach dem Setup wird ein RatingSet erstellt, in dem die Kalibrierung abgespeichert wird
            try:
                rating_set = RatingSet.objects.get(worker=worker, finished=False)
                rating_set.calibrated_volume = request.POST.dict()["calibrate"]
                rating_set.campaign = campaign
            except ObjectDoesNotExist:
                set_nr = RatingSet.objects.filter(worker=worker, finished=True).__len__() + 1
                calibrated_volume = request.POST.dict()["calibrate"]
                rating_set = RatingSet(worker=worker, campaign=campaign,
                                       set_nr=set_nr, calibrated_volume=calibrated_volume)
            rating_set.save()
            return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['rate'])
        context = dict(list(get_context_language(campaign.language, "base").items()) +
                       list(get_context_language(campaign.language, "acr_job_setup").items()) +
                       list(get_context_language(campaign.language, "calibrate").items()))
        context["calibrate_stimulus"] = campaign.calibrate_stimulus
        return render(request, "audiocrowd/acr_job_setup.html", context)

    elif task == task_list[job_list['acr']]['rate']:
        if request.method == "POST":
            other, stimuli, gold_standard = parse_rating_form(request.POST.dict())
            rating_set = RatingSet.objects.get(worker=worker, finished=False)
            for stimulus in stimuli:
                stim_dict = stimuli[stimulus]
                rating = Rating(rating_set=rating_set, stimulus=stim_dict["object"], rating=stim_dict["rating"])
                try:
                    rating.volume = stim_dict["volume"]
                except KeyError:
                    pass
                rating.save()
            for gold_standard_question in gold_standard:
                gold_dict = gold_standard[gold_standard_question]
                answer = GoldStandardAnswers(rating_set=rating_set, question=gold_dict["object"], answer=gold_dict["rating"])
                if answer.answer != answer.question.expected_answer:
                    rating_set.invalid_set = True
                try:
                    answer.volume = gold_dict["volume"]
                except KeyError:
                    pass
                answer.save()
            rating_set.finished = True
            if other["volume_changed"] == "True":
                rating_set.invalid_set = True
            rating_set.save()
            del request.session["set_to_rate"]
            return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['next'])
        else:
            set_to_rate = get_or_create_session_set_to_rate(request, worker, campaign)
            if set_to_rate.__len__() == 0:
                return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['done'])
            context = dict(list(get_context_language(campaign.language, "base").items()) +
                           list(get_context_language(campaign.language, "acr_job_rate").items()) +
                           list(get_context_language(campaign.language, "acr_scale").items()))
            context["to_rate"] = get_set_to_rate_context(set_to_rate)
            context["volume"] = RatingSet.objects.get(worker=worker, finished=False).calibrated_volume
            return render(request, "audiocrowd/acr_job_rate.html", context)

    elif task == task_list[job_list['acr']]['next']:
        if request.method == "POST":
            if request.POST.dict()['continue'] == "true":
                if require_training(worker):
                    return redirect_to(request, job_list['training'], "tmp")
                return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['setup'])
            else:
                return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['done'])
        else:
            set_to_rate = get_or_create_session_set_to_rate(request, worker, campaign)
            if set_to_rate.__len__() == 0:
                return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['done'])
            return render(request, "audiocrowd/acr_job_next_job.html", {})

    elif task == task_list[job_list['acr']]['done']:
        request.session.flush()
        return render(request, "audiocrowd/acr_job_done.html", {})
    return Http404()
