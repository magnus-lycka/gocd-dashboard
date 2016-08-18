from bs4 import BeautifulSoup

from gocddash.analysis.go_client import go_request_comparison_html
from gocddash.util.html_utils import *


def open_html(pipeline_name, current, comparison):
    html = go_request_comparison_html(pipeline_name, current, comparison)
    # html = remove_wbr_tags(html)
    # html = remove_new_line(html)
    # html = remove_excessive_whitespace(html)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def fetch_pipeline_from_url(url):
    return url.rsplit("/", 1)[1] if "/" in url else url


def extract_list_of_lists_from_html_table(git_sections):
    """ Rather convoluted way of extracting the git blame list from GO. """
    final_list = []

    for table in git_sections:
        revisions = []
        modified_by = []
        comments = []
        git_url = (table.split("<strong>")[1]).split(",")[0]
        pipeline_name = fetch_pipeline_from_url(git_url)

        list_of_words = table.split()

        print(list_of_words)
        indices = [i for i, x in enumerate(list_of_words) if  """class="revision">""" in x and """class="revision">Revision""" not in x]

        for index in indices:
            revisions.append(clean_html(list_of_words[index]).replace("""class="revision">""", "").replace("<td", ""))

        start_indices = [i for i, x in enumerate(list_of_words) if """class="modified_by">""" in x and """class="modified_by">Modified""" not in x]
        end_indices = [i for i, x in enumerate(list_of_words) if """class="comment"><p>""" in x]

        for i, index in enumerate(indices):
            modified_by.append(clean_html(' '.join(list_of_words[start_indices[i]:end_indices[i]])).replace("""class="modified_by">""", "").replace("<td", ""))

        start_indices = [i for i, x in enumerate(list_of_words) if
                         """class="comment"><p>""" in x]  # Every comment starts with this
        end_indices = [i + 1 for i, x in enumerate(list_of_words) if "</td></tr>" in x]  # Every comments ends with this

        modified_by = [mod.replace(">", "> ") for mod in modified_by]

        for i, index in enumerate(start_indices):
            comments.append(((clean_html(' '.join(list_of_words[index:end_indices[i]]))).split(">")[1]).replace("<tr", ""))

        for i, revision in enumerate(revisions):
            final_list.append([pipeline_name, git_url, revision, modified_by[i], comments[i]])

    return final_list


def get_git_comparison(pipeline_name, current, comparison, preferred_upstream):
    soup = open_html(pipeline_name, current, comparison)

    # Material revision diff test
    if "pipeline instance that was triggered with a non-sequential material revision." in str(soup):
        return None
    material_titles = soup.findAll('div', {"class": "material_title"})
    git_sections = list(map(lambda z: z.rpartition("/")[2], filter(lambda y: not y.startswith(" Pipeline"),  map(lambda x: x.findAll('strong')[0].get_text(), material_titles))))
    tables = soup.findAll('table', {'class': "list_table material_modifications"})
    # print(tables)
    assert len(tables) == len(git_sections)
    changes = []
    for table_index, table in enumerate(tables):
        revisions = table.findAll('td', {'class': 'revision'})
        modified_by = table.findAll('td', {'class': 'modified_by'})
        comments = table.findAll('td', {'class': 'comment'})

        these_changes = []
        for index, revision in enumerate(revisions):
            revision_text = revision.get_text().strip()
            modified_by_text = remove_new_line(modified_by[index].get_text().strip())
            comments_text = comments[index].get_text().strip()
            these_changes.append((revision_text, modified_by_text, comments_text))
        these_changes = only_real_people(these_changes)
        changes.append((git_sections[table_index], these_changes))

    return changes


def sort_by_current_then_preferred(git_blame_list, pipeline_name, preferred_upstream):
    # Not all pipeline names are the same as their git repo names. Possible fix is to do NLP similarity comparisons.
    git_blame_list.sort(
        key=lambda x: (pipeline_name not in x[0], preferred_upstream not in x[0]))  # x[0] is the pipeline column
    return git_blame_list


def only_real_people(git_blame_list):
    return list(filter(lambda x: "go-agent" not in x[1], git_blame_list))
