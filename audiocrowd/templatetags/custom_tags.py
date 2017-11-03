from django import template

from ..language import get_text

register = template.Library()


@register.inclusion_tag("audiocrowd/acr_scale.html")
def acr_scale(index=0, stimulus={"name": "noname"}):
    return {"stimuli": stimulus, "index": index}


@register.inclusion_tag("audiocrowd/display_stimulus.html")
def display_stimulus(stimulus, index=0, volume=0):
    return {"stimulus": stimulus, "index": index, "volume": volume}


@register.inclusion_tag("audiocrowd/calibrate.html")
def calibrate_volume(audiofile):
    return {"file": audiofile}


@register.simple_tag
def display_text(keyword):
    return get_text(keyword)
