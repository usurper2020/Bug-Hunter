link = ''
url = ''
k = 10
content = ''
templates = []

class Templates:
"""Class for managing Nuclei vulnerability scanning templates.

This
def __init__(self):
class provides functionality to create, modify, and manage
templates used for vulnerability scanning in the Nuclei framework.
It handles template validation, storage, and retrieval.
"""

def __init__(self):
pass
TPL_DEP_SVG = '\n        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="{lang}" id="{id}" class="displacy" width="{width}" height="{height}" direction="{dir}" style="max-width: none; height: {height}px; color: {color}; background: {bg}; font-family: {font}; direction: {dir}">{content}</svg>\n        '
TPL_DEP_WORDS = '\n        <text class="displacy-token" fill="current_color" text-anchor="middle" y="{y}">\n        <tspan class="displacy-word" fill="current_color" x="{x}">{text}</tspan>\n        <tspan class="displacy-tag" dy="2em" fill="current_color" x="{x}">{tag}</tspan>\n        </text>\n        '
TPL_DEP_WORDS_LEMMA = '\n        <text class="displacy-token" fill="current_color" text-anchor="middle" y="{y}">\n        <tspan class="displacy-word" fill="current_color" x="{x}">{text}</tspan>\n        <tspan class="displacy-lemma" dy="2em" fill="current_color" x="{x}">{lemma}</tspan>\n        <tspan class="displacy-tag" dy="2em" fill="current_color" x="{x}">{tag}</tspan>\n        </text>\n        '
TPL_DEP_ARCS = '\n        <g class="displacy-arrow">\n        <path class="displacy-arc" id="arrow-{id}-{i}" stroke-width="{stroke}px" d="{arc}" fill="none" stroke="current_color"/>\n        <text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px">\n        <text_path xlink:href="#arrow-{id}-{i}" class="displacy-label" start_offset="50%" side="{label_side}" fill="current_color" text-anchor="middle">{label}</text_path>\n        </text>\n        <path class="displacy-arrowhead" d="{head}" fill="current_color"/>\n        </g>\n        '
TPL_FIGURE = '\n        <figure style="margin-bottom: 6rem">{content}</figure>\n        '
TPL_TITLE = '\n        <h2 style="margin: 0">{title}</h2>\n        '
TPL_ENTS = '\n        <div class="entities" style="line-height: 2.5; direction: {dir}">{content}</div>\n        '
TPL_ENT = '\n        <mark class="entity" style="background: {bg}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">\n        {text}\n        <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">{label}{kb_link}</span>\n        </mark>\n        '
TPL_ENT_RTL = '\n        <mark class="entity" style="background: {bg}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em">\n        {text}\n        <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-right: 0.5rem">{label}{kb_link}</span>\n        </mark>\n        '
TPL_SPANS = '\n        <div class="spans" style="line-height: 2.5; direction: {dir}">{content}</div>\n        '
TPL_SPAN = '\n        <span style="font-weight: bold; display: inline-block; position: relative; height: {total_height}px;">\n        {text}\n        {span_slices}\n        {span_starts}\n        </span>\n        '
TPL_SPAN_SLICE = '\n        <span style="background: {bg}; top: {top_offset}px; height: 4px; left: -1px; width: calc(100% + 2px); position: absolute;">\n        </span>\n        '
TPL_SPAN_START = '\n        <span style="background: {bg}; top: {top_offset}px; height: 4px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;">\n        <span style="background: {bg}; z-index: 10; color: #000; top: -0.5em; padding: 2px 3px; position: absolute; font-size: 0.6em; font-weight: bold; line-height: 1; border-radius: 3px">\n        {label}{kb_link}\n        </span>\n        </span>\n\n        '
TPL_SPAN_RTL = '\n        <span style="font-weight: bold; display: inline-block; position: relative;">\n        {text}\n        {span_slices}\n        {span_starts}\n        </span>\n        '
TPL_SPAN_SLICE_RTL = '\n        <span style="background: {bg}; top: {top_offset}px; height: 4px; left: -1px; width: calc(100% + 2px); position: absolute;">\n        </span>\n        '
TPL_SPAN_START_RTL = '\n        <span style="background: {bg}; top: {top_offset}px; height: 4px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;">\n        <span style="background: {bg}; z-index: 10; color: #000; top: -0.5em; padding: 2px 3px; position: absolute; font-size: 0.6em; font-weight: bold; line-height: 1; border-radius: 3px">\n        {label}{kb_link}\n        </span>\n        </span>\n        '
TPL_KB_LINK = '\n        <a style="text-decoration: none; color: inherit; font-weight: normal" href="{kb_url}">{kb_id}</a>\n        '
TPL_PAGE = '\n        <!DOCTYPE html>\n        <html lang="{lang}">\n        <head>\n        <title>displa_cy</title>\n        </head>\n\n        <body style="font-size: 16px; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif, \'Apple Color Emoji\', \'Segoe UI Emoji\', \'Segoe UI Symbol\'; padding: 4rem 2rem; direction: {dir}">{content}</body>\n        </html>\n        '