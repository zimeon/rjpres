"""Simple function to show Markdown help and exit
"""

import os.path

def show_help_md():
    template_dir = os.path.join(os.path.dirname(__file__),'templates')
    template_file = os.path.join(template_dir,"help_md.tpl")
    template = open(template_file).read()
    # Populate arguments for template
    args = { }
    # Fill template and return
    print template.format(**args)
