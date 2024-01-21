from jinja2 import Environment, FileSystemLoader

# load templates folder to environment (security measure)
env = Environment(loader=FileSystemLoader('./'))

# load the `index.jinja` template
#index_template = env.get_template('index.jinja')
#output_from_parsed_template = index_template.render()

# write the parsed template
#with open("../public/index.html", "w") as chap_page:
#    chap_page.write(output_from_parsed_template)

def makePage(pn):
    with open(f"../public/{pn}.html", "w") as chap_page:
        chap_page.write(env.get_template(f"{pn}.jinja").render())

for page_name in ['index','blog','404']:
    makePage(page_name)
