from django.db import models
from django.utils.timezone import now


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Stimuli(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=50)
    type = models.CharField(max_length=3,
                            choices=[("img", "Image"), ("aud", "Audio"), ("vid", "Video"), ("txt", "Text")])

    def __str__(self):
        return "stim : " + str(self.name)


class GoldStandardQuestions(models.Model):
    name = models.CharField(max_length=50)
    expected_answer = models.IntegerField(
        choices=[(1, "1 Bad"), (2, "2 Poor"), (3, "3 Fair"), (4, "4 Good"), (5, "5 Excellent")])
    path = models.CharField(max_length=50)
    type = models.CharField(max_length=3,
                            choices=[("img", "Image"), ("aud", "Audio"), ("vid", "Video"), ("txt", "Text")])

    def __str__(self):
        return "gold_standard : " + str(self.name)


class Campaign(models.Model):
    campaign_id = models.CharField(max_length=50)

    platform = models.CharField(max_length=3, choices=[("mw", "Microworkers")])
    vcode_key = models.CharField(max_length=256, default="No key")

    language = models.CharField(max_length=3, choices=[("de", "Deutsch"), ("en", "English")])
    stimuli_per_job = models.IntegerField(default=10)
    gold_standard_per_job = models.IntegerField(default=1)
    stimuli = models.ManyToManyField(Stimuli, related_name="stimuli")
    gold_standard_questions = models.ManyToManyField(GoldStandardQuestions)
    training_stimuli = models.ManyToManyField(Stimuli, related_name="training_stimuli")
    calibrate_stimulus = models.ForeignKey(Stimuli)

    contact_link = models.CharField(max_length=100, default="http://crowd-square.com/viewtopic.php?f=30&t=18835")

    def __str__(self):
        return "Campaign : " + str(self.platform) + "-" + str(self.campaign_id)


class Configuration(SingletonModel):
    access_window = models.IntegerField(default=60)
    default_campaign = models.ForeignKey(Campaign, blank=True, null=True, default=None)

    def __str__(self):
        return "Config"


class Worker(models.Model):
    name = models.CharField(max_length=50)

    gender = models.CharField(max_length=6, choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
                              null=True)
    birth_year = models.DateField(null=True)
    hearing_loss = models.IntegerField(choices=[(1, "Yes"), (0, "No")], null=True)
    subjective_test = models.IntegerField(
        choices=[(0, "Never"), (1, "1 Month"), (2, "3 Months"), (3, "6 Months"), (4, "9 Months"),
                 (5, "1 year or more")], null=True)
    speech_test = models.IntegerField(
        choices=[(0, "Never"), (1, "1 Month"), (2, "3 Months"), (3, "6 Months"), (4, "9 Months"),
                 (5, "1 year or more")], null=True)
    connected = models.IntegerField(choices=[(1, "Yes"), (0, "No")], null=True)

    # hat der Worker die qualification abgeschlossen?
    qualification_done = models.BooleanField(default=False)
    # hat der Worker Zugang bekommen?
    access_training = models.BooleanField(default=False)
    # time until worker can access acr-job
    access_acr = models.DateTimeField(default=now)

    def __str__(self):
        return "Worker: " + str(self.name)


class SubCampaign(models.Model):
    parent_campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    sub_campaign_id = models.CharField(max_length=50)
    tracker_window = models.IntegerField(default=60)
    max_worker_count = models.IntegerField()

    def __str__(self):
        return str(self.sub_campaign_id) + " / " + str(self.parent_campaign)


class SubCampaignTracker(models.Model):
    sub_campaign = models.ForeignKey(SubCampaign, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker)
    time = models.DateTimeField(default=now)


class RatingSet(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    sub_campaign = models.ForeignKey(SubCampaign, on_delete=models.CASCADE)
    set_nr = models.IntegerField()
    finished = models.BooleanField(default=False)
    invalid_set = models.BooleanField(default=False)

    def __str__(self):
        return str(self.worker) + " / set: " + str(self.set_nr)


class Rating(models.Model):
    rating_set = models.ForeignKey(RatingSet, on_delete=models.CASCADE)
    stimulus = models.ForeignKey(Stimuli, on_delete=models.CASCADE)
    rating = models.IntegerField(
        choices=[(1, "1 Bad"), (2, "2 Poor"), (3, "3 Fair"), (4, "4 Good"), (5, "5 Excellent")])

    def __str__(self):
        return str(self.rating_set) + " / " + str(self.stimulus) + " / rating : " + str(self.rating)


class GoldStandardAnswers(models.Model):
    rating_set = models.ForeignKey(RatingSet, on_delete=models.CASCADE)
    question = models.ForeignKey(GoldStandardQuestions, on_delete=models.CASCADE)
    answer = models.IntegerField(
        choices=[(1, "1 Bad"), (2, "2 Poor"), (3, "3 Fair"), (4, "4 Good"), (5, "5 Excellent")])

    def __str__(self):
        return str(self.rating_set) + " / " + str(self.question) + " / answer : " + str(self.answer)
