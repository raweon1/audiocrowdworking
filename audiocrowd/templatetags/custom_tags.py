from django import template

register = template.Library()


@register.inclusion_tag("audiocrowd/acr_scale.html", takes_context=True)
def acr_scale(context, index=0, stimulus={"name": "noname"}):
    return {"stimuli": stimulus, "index": index, "acr_scale": context["acr_scale"], "language": context["language"]}


@register.inclusion_tag("audiocrowd/display_stimulus.html", takes_context=True)
def display_stimulus(context, stimulus, index=0, volume=0):
    return {"stimulus": stimulus, "index": index, "volume": volume, "display_stimulus": context["display_stimulus"]}


@register.inclusion_tag("audiocrowd/calibrate.html", takes_context=True)
def calibrate_volume(context, audiofile, volume):
    return {"file": audiofile, "pre_msg": context["calibrate"][0], "post_msg": context["calibrate"][1], "volume": volume}
