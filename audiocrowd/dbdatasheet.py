from audiocrowd.models import RatingSet, Rating
import csv


def extract_stimulus_name(stimulus):
    name_start = stimulus.rfind("/") + 1
    name_end = stimulus.rfind(".")
    return stimulus[name_start: name_end]


def write_db_csv(path="data.csv"):
    with open(path, "w", encoding="utf-8") as csvfile:
        fieldnames = ["campaign", "platform", "language",
                      "subcampaign",
                      "worker", "gender", "birth_year", "hearing_loss", "subjective_test", "speech_test", "connected",
                      "rating_set_nr", "invalid",
                      "stimulus", "type", "rating"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        rating_sets = RatingSet.objects.all()
        for rating_set in rating_sets:
            sub_campaign = rating_set.sub_campaign
            campaign = sub_campaign.parent_campaign
            worker = rating_set.worker
            csv_dict = {"campaign": campaign.campaign_id,
                        "platform": campaign.platform,
                        "language": campaign.language,
                        "subcampaign": sub_campaign.sub_campaign_id,
                        "worker": worker.name,
                        "gender": worker.gender,
                        "birth_year": str(worker.birth_year),
                        "hearing_loss": worker.hearing_loss,
                        "subjective_test": worker.subjective_test,
                        "speech_test": worker.speech_test,
                        "connected": worker.connected,
                        "questions": worker.questions,
                        "rating_set_nr": rating_set.set_nr,
                        "invalid": rating_set.invalid_set}
            ratings = Rating.objects.filter(rating_set=rating_set)
            for rating in ratings:
                csv_dict["stimulus"] = extract_stimulus_name(rating.stimulus.path)
                csv_dict["type"] = rating.stimulus.type
                csv_dict["rating"] = rating.rating
                writer.writerow(csv_dict)
