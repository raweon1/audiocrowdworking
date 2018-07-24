from django.contrib import admin

from .models import Stimuli, Worker, GoldStandardQuestions, Rating, GoldStandardAnswers, Configuration, RatingSet, \
    Campaign, SubCampaign, SubCampaignTracker, HeadphoneCheckStimulus


class SubCampaignInline(admin.TabularInline):
    model = SubCampaign
    extra = 0


class CampaignAdmin(admin.ModelAdmin):
    inlines = [SubCampaignInline, ]


admin.site.register(Stimuli)
admin.site.register(Worker)
admin.site.register(GoldStandardQuestions)
admin.site.register(Rating)
admin.site.register(GoldStandardAnswers)
admin.site.register(Configuration)
admin.site.register(RatingSet)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(SubCampaign)
admin.site.register(SubCampaignTracker)
admin.site.register(HeadphoneCheckStimulus)
