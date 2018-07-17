from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.forms import ModelForm
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.contrib.staticfiles.templatetags.staticfiles import static

from .models import Stimuli, GoldStandardQuestions, Worker, Rating, GoldStandardAnswers, Configuration, RatingSet, \
    Campaign, SubCampaign, SubCampaignTracker
from .language import get_context
from .my_widgets import MySelectDateWidget, YearOnlySelectDateWidget
from .dbdatasheet import write_db_csv

from audiocrowdworking.settings import STATIC_ROOT

from datetime import timedelta
from random import randint
from hashlib import sha256
from collections import defaultdict
from operator import itemgetter

job_list = dict(register="register", qualification="qualification_job", training="training_job", acr="acr_job")

qualification_job_tasks = dict(introduction="introduction", questions="general_questions",
                               questionnaire="questionnaire")
training_job_tasks = dict(setup="setup", samples="samples", welcome_back="welcome_back")
acr_job_tasks = dict(setup="setup", rate="rate", next="next", done="done", end="end", welcome_back="welcome_back")

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


#http://localhost:8000/audio/register/de_img_test/campaignid=de_img_test&workerid=Andre


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
        sub_campaing = SubCampaign.objects.get(sub_campaign_id=request.session["sub_campaign"],
                                               parent_campaign=campaign)
    except KeyError:
        raise NotRegisteredException()
    except ObjectDoesNotExist:
        raise NotRegisteredException()
    return worker, campaign, sub_campaing


def correct_job(request, job):
    job_todo = get_job(request)
    if job != job_todo:
        raise WrongJobException


def get_environment(request, called_job):
    try:
        worker, campaign, sub_campaign = is_registered(request)
        correct_job(request, called_job)
        task = get_task(request)
    except NotRegisteredException:
        return True, HttpResponseBadRequest("You are not registered"), None, None, None, None
    except WrongJobException:
        return True, HttpResponseRedirect(link_list[get_job(request)]), None, None, None, None
    return False, None, worker, campaign, sub_campaign, task


def redirect_to(request, job, task):
    request.session["job"] = job
    request.session["task"] = task
    return HttpResponseRedirect(link_list[job])


def register(request, campaign_id):
    sub_campaign_id = request.GET.get("campaignid")
    worker_id = request.GET.get("workerid")
    if not (sub_campaign_id and worker_id):
        error = '<div align="center">BadRequest 400<br>'
        if not sub_campaign_id:
            error = error + 'Expected argument "campaignid"<br>'
        if not worker_id:
            error = error + 'Expected argument "workerid"<br>'
        error = error + "</div>"
        return HttpResponseBadRequest(error)
    try:
        sub_campaign = SubCampaign.objects.get(sub_campaign_id=sub_campaign_id,
                                               parent_campaign__campaign_id=campaign_id)
    except ObjectDoesNotExist:
        try:
            campaign = Campaign.objects.get(campaign_id=campaign_id)
            sub_campaign = SubCampaign(parent_campaign=campaign, sub_campaign_id=sub_campaign_id,
                                       max_worker_count=30, tracker_window=60)
            sub_campaign.save()
        except ObjectDoesNotExist:
            request.session.flush()
            return HttpResponseBadRequest("Campaign " + campaign_id + " does not exist")
    # session wird beendet wenn der browser geschlossen wird
    request.session.set_expiry(0)

    # falls bereits eine session läuft darf keine neue Session gestartet werden.
    try:
        if not request.session["finished"]:
            return HttpResponseBadRequest(
                "Another unfinished session is already running. Please finish that session before starting a new one")
    except KeyError:
        request.session["finished"] = False

    request.session["sub_campaign"] = sub_campaign_id
    request.session["campaign"] = sub_campaign.parent_campaign.campaign_id
    request.session["worker"] = worker_id
    request.session["calibrate"] = 0.5
    worker, created = Worker.objects.get_or_create(name=worker_id)

    try:
        # sollte er schon ein token haben -> ok
        SubCampaignTracker.objects.get(sub_campaign=sub_campaign, worker=worker)
    except ObjectDoesNotExist:
        # braucht ein token
        tmp = SubCampaignTracker.objects.filter(sub_campaign=sub_campaign)
        for entry in tmp:
            if entry.time + timedelta(minutes=sub_campaign.tracker_window) < now():
                entry.delete()
        tmp = SubCampaignTracker.objects.filter(sub_campaign=sub_campaign)
        if tmp.__len__() < sub_campaign.max_worker_count - RatingSet.objects.filter(sub_campaign=sub_campaign,
                                                                                    finished=True).__len__():
            track = SubCampaignTracker(sub_campaign=sub_campaign, worker=worker)
            track.save()
        else:
            context = get_context(sub_campaign.parent_campaign, "campaign_is_full")
            request.session.flush()
            return render(request, "audiocrowd/campaign_is_full.html", context)
    if not worker.qualification_done:
        return redirect_to(request, job_list['qualification'], task_list[job_list['qualification']]['introduction'])
    elif not worker.access_training:
        return HttpResponse("You are not qualified to participate")
    return redirect_to(request, job_list['training'], task_list[job_list['training']]['welcome_back'])


class GeneralQuestionsForm(ModelForm):
    class Meta:
        model = Worker
        fields = ("gender", "birth_year", "hearing", "background_noise", "subjective_test", "speech_test", "connected",
                  "listening_device")
        widgets = {
            "birth_year": YearOnlySelectDateWidget(empty_label=("---------", "---------", "---------"),
                                                   years=[y for y in range(1950, 2007)])
        }

    def __init__(self, campaign, *args, **kwargs):
        super(GeneralQuestionsForm, self).__init__(*args, **kwargs)
        tmp = get_context(campaign, "qualification_job_questions")["qualification_job_questions"]
        self.fields["gender"].label = tmp[2]
        self.fields["birth_year"].label = tmp[3]
        self.fields["hearing"].label = tmp[4]
        self.fields["background_noise"].label = tmp[5]
        self.fields["subjective_test"].label = tmp[6]
        self.fields["speech_test"].label = tmp[7]
        self.fields["connected"].label = tmp[8]
        self.fields["listening_device"].label = tmp[9]
        if campaign.language != "en":
            # todo add choices for de for hearing & background_noise
            self.fields["gender"].choices = [("", "---------"),
                                             ("male", tmp[10][0]), ("female", tmp[10][1]), ("other", tmp[10][2])]
            #self.fields["birth_year"].widget.months = {1: tmp[11][0], 2: tmp[11][1], 3: tmp[11][2], 4: tmp[11][3],
            #                                           5: tmp[11][4], 6: tmp[11][5], 7: tmp[11][6], 8: tmp[11][7],
            #                                           9: tmp[11][8], 10: tmp[11][9], 11: tmp[11][10], 12: tmp[11][11]}
            self.fields["subjective_test"].choices = [("", "---------"),
                                                      (0, tmp[12][0]), (1, tmp[12][1]), (2, tmp[12][2]),
                                                      (3, tmp[12][3]), (4, tmp[12][4]), (5, tmp[12][5])]
            self.fields["speech_test"].choices = [("", "---------"),
                                                  (0, tmp[12][0]), (1, tmp[12][1]), (2, tmp[12][2]),
                                                  (3, tmp[12][3]), (4, tmp[12][4]), (5, tmp[12][5])]
            #self.fields["hearing_loss"].choices = [("", "---------"), (1, tmp[13][0]), (0, tmp[13][1])]
            self.fields["connected"].choices = [("", "---------"), (1, tmp[13][0]), (0, tmp[13][1])]
            self.fields["listening_device"].choices = [("", "---------"),
                                                       (0, tmp[14][0]), (1, tmp[14][1]), (2, tmp[14][2])]


def qualification_job_view(request):
    error, http, worker, campaign, sub_campaign, task = get_environment(request, job_list['qualification'])
    if error:
        return http

    if task == task_list[job_list['qualification']]['introduction']:
        if request.method == "POST":
            return redirect_to(request, job_list['qualification'], task_list[job_list['qualification']]['questions'])
        else:
            context = get_context(campaign, "qualification_job_introduction", "acr_scale")
            return render(request, "audiocrowd/qualification_job_introduction.html", context)
    elif task == task_list[job_list['qualification']]['questions']:
        if request.method == "POST":
            form = GeneralQuestionsForm(campaign, data=request.POST, instance=worker)
            if form.is_valid():
                form.save()
                worker.save()
                return redirect_to(request, job_list['qualification'],
                                   task_list[job_list['qualification']]['questionnaire'])
            else:
                # Die Form ist sollte immer valid sein
                return HttpResponse("Form is invalid")
        else:
            context = get_context(campaign, "qualification_job_questions")
            form = GeneralQuestionsForm(campaign, instance=worker)
            context["form"] = form
            return render(request, "audiocrowd/qualification_job_questions.html", context)
    elif task == task_list[job_list['qualification']]['questionnaire']:
        if request.method == "POST":
            tmp = request.POST.dict()
            answer = "".join([tmp[str(i)] for i in range(1, tmp.__len__())])
            worker.questions = answer
            # TODO evaluation! wenn Zugang gewährt wird muss worker.access_training auf True gesetzt werden
            worker.qualification_done = True
            worker.access_training = True
            worker.save()
            return redirect_to(request, job_list['training'], task_list[job_list['training']]["setup"])
        else:
            context = get_context(campaign, "qualification_job_questionnaire", "qualification_job_questionnaire_meta")
            tmp_list = []
            for i in range(1, context["qualification_job_questionnaire"].__len__() + 1):
                tmp_list.append((i, context["qualification_job_questionnaire"][i - 1]))
            context["qualification_job_questionnaire"] = tmp_list
            return render(request, "audiocrowd/qualification_job_questionaire.html", context)


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
    return stimuli_to_rate


def training_job_view(request):
    error, http, worker, campaign, sub_campaign, task = get_environment(request, job_list['training'])
    if error:
        return http

    if require_training(worker):
        if task == task_list[job_list['training']]["setup"]:
            if request.method == "POST":
                request.session["calibrate"] = request.POST.dict()["calibrate"]
                return redirect_to(request, job_list["training"], task_list[job_list['training']]["samples"])
            else:
                context = get_context(campaign, "training_job_setup", "calibrate")
                context["calibrate_stimulus"] = campaign.calibrate_stimulus
                context["volume"] = 0.5
                return render(request, "audiocrowd/training_setup.html", context)
        elif task == task_list[job_list['training']]["samples"]:
            if request.method == "POST":
                worker.access_acr = now() + timedelta(minutes=Configuration.load().access_window)
                worker.save()
                return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['setup'])
            else:
                context = get_context(campaign, "acr_job_rate", "acr_scale", "display_stimulus")
                context["acr_job_rate"][4] = get_context(campaign, "training_job_rate")["training_job_rate"][0]
                context["to_rate"] = get_training_stimuli_to_rate_context(campaign)
                context["volume"] = request.session["calibrate"]
                return render(request, "audiocrowd/acr_job_rate.html", context)
        elif task == task_list[job_list['training']]["welcome_back"]:
            if request.method == "POST":
                return redirect_to(request, job_list['training'], task_list[job_list['training']]['setup'])
            else:
                context = get_context(campaign, "acr_job_welcome_back")
                context["acr_job_welcome_back"][1] = get_context(
                    campaign, "training_job_welcome_back")["training_job_welcome_back"][0]
                return render(request, "audiocrowd/acr_welcome_back.html", context)
    return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['welcome_back'])


# @param: count = max. Anzahl von zu bearbeitenden Stimuli
# @param: worker = Der aktuelle Arbeiter
# @param: campaign = Die Campaign über die der Arbeiter kommt
# @return: gibt eine Liste von Stimuli zurück, die von <worker> bisher nicht bearbeitet wurden. Die Reihenfolge ist
# zufällig. Stimuli stehen in Verbindung mit campaign.
# @return: Liste kann leer sein, wenn keine Stimuli mehr zu bewerten sind.
def get_stimuli_to_rate(count, worker, campaign):
    available_stimuli = campaign.stimuli.all().exclude(rating__rating_set__worker=worker,
                                                       rating__rating_set__sub_campaign__parent_campaign=campaign)
    tmp = defaultdict(list)
    for stimulus in available_stimuli:
        rating_count = Rating.objects.filter(rating_set__sub_campaign__parent_campaign=campaign,
                                             stimulus=stimulus).__len__()
        tmp[rating_count].append(stimulus)

    pflicht_stim = []
    filler_stim = []
    for rating_count, stim_list in sorted(tmp.items(), key=itemgetter(0)):
        pflicht_stim.extend(filler_stim)
        filler_stim = stim_list
        if pflicht_stim.__len__() + filler_stim.__len__() >= count:
            break

    stimuli_to_rate = []
    for i in range(0, count):
        if pflicht_stim.__len__() > 0:
            rnd = randint(0, pflicht_stim.__len__() - 1)
            stimuli_to_rate.append(pflicht_stim[rnd])
            del pflicht_stim[rnd]
        elif filler_stim.__len__() > 0:
            rnd = randint(0, filler_stim.__len__() - 1)
            stimuli_to_rate.append(filler_stim[rnd])
            del filler_stim[rnd]
        if pflicht_stim.__len__() + filler_stim.__len__() == 0:
            break
    return stimuli_to_rate


# @param: siehe get_stimuli_to_rate
# @return: gibt eine Liste von Stimuli UND einer GoldStandardQuestion zurück, die von <worker> bisher nicht bearbeitet
# wurden. Die Reihenfolge ist zufällig.
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


# Funktion soll den Namen eines Stimulus von einem Key key aus dem Dict von acr_job_rate.html geben.
# Falls key != stimulus.name ist, muss diese Funktion
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


def get_mw_vcode(sub_campaign_id, worker_id, vcode_key):
    tmp = sub_campaign_id + worker_id + vcode_key
    return "mw-" + sha256(tmp.encode("utf-8")).hexdigest()


def acr_job_view(request):
    error, http, worker, campaign, sub_campaign, task = get_environment(request, job_list['acr'])
    if error:
        return http

    if task == task_list[job_list['acr']]['setup']:
        if request.method == "POST":
            # nach dem Setup wird ein RatingSet erstellt, in dem die Kalibrierung abgespeichert wird
            request.session["calibrate"] = request.POST.dict()["calibrate"]
            try:
                rating_set = RatingSet.objects.get(worker=worker, finished=False)
                rating_set.sub_campaign = sub_campaign
            except ObjectDoesNotExist:
                set_nr = RatingSet.objects.filter(worker=worker, finished=True).__len__() + 1
                rating_set = RatingSet(worker=worker, sub_campaign=sub_campaign,
                                       set_nr=set_nr)
            rating_set.save()
            return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['rate'])
        context = get_context(campaign, "acr_job_setup", "calibrate")
        context["calibrate_stimulus"] = campaign.calibrate_stimulus
        context["volume"] = request.session["calibrate"]
        return render(request, "audiocrowd/acr_job_setup.html", context)

    elif task == task_list[job_list['acr']]['rate']:
        if request.method == "POST":
            other, stimuli, gold_standard = parse_rating_form(request.POST.dict())
            rating_set = RatingSet.objects.get(worker=worker, finished=False)
            for stimulus in stimuli:
                stim_dict = stimuli[stimulus]
                rating = Rating(rating_set=rating_set, stimulus=stim_dict["object"], rating=stim_dict["rating"])
                rating.save()
            for gold_standard_question in gold_standard:
                gold_dict = gold_standard[gold_standard_question]
                answer = GoldStandardAnswers(rating_set=rating_set,
                                             question=gold_dict["object"], answer=gold_dict["rating"])
                answer.save()
                if str(answer.answer) != str(answer.question.expected_answer):
                    rating_set.invalid_set = True
            rating_set.finished = True
            rating_set.save()
            del request.session["set_to_rate"]
            # session is finished, another one can be startet
            request.session["finished"] = True
            return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['end'])
        else:
            set_to_rate = get_or_create_session_set_to_rate(request, worker, campaign)
            if set_to_rate.__len__() == 0:
                return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['done'])
            context = get_context(campaign, "acr_job_rate", "acr_scale", "display_stimulus")
            context["to_rate"] = get_set_to_rate_context(set_to_rate)
            context["volume"] = request.session["calibrate"]
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

    elif task == task_list[job_list['acr']]['welcome_back']:
        if request.method == "POST":
            return redirect_to(request, job_list['acr'], task_list[job_list['acr']]['setup'])
        else:
            context = get_context(campaign, "acr_job_welcome_back")
            return render(request, "audiocrowd/acr_welcome_back.html", context)

    elif task == task_list[job_list['acr']]['end']:
        # damit man nach x Kampagnen nicht wieder Training machen muss
        worker.access_acr = now() + timedelta(minutes=Configuration.load().access_window)
        worker.save()
        # trackereintrag löschen
        try:
            track = SubCampaignTracker.objects.get(worker=worker, sub_campaign=sub_campaign)
            track.delete()
        except ObjectDoesNotExist:
            pass
        context = get_context(campaign, "acr_job_end")
        context["vcode"] = get_mw_vcode(sub_campaign.sub_campaign_id, worker.name, campaign.vcode_key)
        return render(request, "audiocrowd/acr_job_end.html", context)
    raise Http404()


def result_view(request):
    write_db_csv(STATIC_ROOT + "data.csv")
    return HttpResponseRedirect(static("data.csv"))
