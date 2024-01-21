"""Static file generator"""
import jinja2

# load templates folder to environment (security measure)
env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))


def make_page(page_name):
    """Create a main/top-level page."""
    with open(f"../public/{page_name}.html", "w", encoding="utf-8") as chap_page:
        chap_page.write(env.get_template(f"{page_name}.jinja").render())


for template_name in ['index', 'blog', '404']:
    make_page(template_name)
