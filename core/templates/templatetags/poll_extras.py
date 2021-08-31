from django import template
from django.conf import settings
from re import IGNORECASE, compile, escape as rescape

import numpy as np
import re

from django.utils.html import strip_tags
from django.utils.safestring import mark_safe



register = template.Library()

SETTINGS_PREFIX = 'SEARCH_'
SETTINGS_DEFAULTS = {
    'CONTEXT_WORDS': 10,
    'IGNORE_CASE': True,
    'WORD_BOUNDARY': False,
    'HIGHLIGHT_CLASS': "highlight"
}


@register.filter
def highlight(text, s, autoescape=True):

    search  = s.split()
    text = strip_tags(text)

    search = [' ' + x + ' ' for x in search]
   

    for x in search:
        if x != 'mark' and x != '<' and x != '>' and x != '/':
           # text = text.replace(x, "<mark>%s</mark>" %x)
            text = re.sub(x, f' <mark>{x}</mark> ', text, flags=re.IGNORECASE)


    return mark_safe(text)



@register.filter
def highlightR(text, s, autoescape=True):

    text = strip_tags(text)

    text = text.replace(s, " <span style='background-color:#FFA4A4;color=#FFFFFF;border-radius:3px;'>%s</span> " %s)

            

    return mark_safe(text)

@register.filter
def highlightG(text, s, autoescape=True):

    s = ' '+s+' '
    text = strip_tags(text)
    text = text.replace(s, " <span style='background-color:#ABEBC6;color=#FFFFFF;border-radius:3px;'>%s</span> " %s)

    return mark_safe(text)

@register.filter
def highlightBG(text, s, autoescape=True):

    s = ''+s+''
    text = strip_tags(text)
    text = text.replace(s, " <span style='border-bottom:3px solid #ABEBC6;color=#FFFFFF'>%s</span> " %s)

    return mark_safe(text)

@register.filter
def highlightBR(text, s, autoescape=True):

    s = ''+s+''
    text = strip_tags(text)
    text = text.replace(s, " <span style='border-bottom:3px solid #FFA4A4;color=#FFFFFF'>%s</span> " %s)

    return mark_safe(text)


 
@register.filter
def highlight_search(text, search):
    highlighted = text.replace(search.lower(), '<mark>{}</mark>'.format(search.lower()))

    return highlighted

@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    # you would need to do any localization of the result here
    return qty * unit_price

# @register.filter
# def highlight(text, word):
#     return text.replace(word, "<mark style='background-color: #F3C366;'>%s</mark>" % word)

