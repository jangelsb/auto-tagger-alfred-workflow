import sys
import json
import os
import yaml
import urllib.parse
import re
from datetime import datetime

class URLScheme:
    def __init__(self, title, urlScheme, url=None, icon=None):
        self.title = title
        self.urlScheme = urlScheme
        self.url = url
        self.icon = icon


class ResultItem:
    def __init__(self, title, arg, subtitle='', autocomplete=None, location=None, valid=True, mods=None, text=None, uid=None, icon_path=None, type=None, quicklookurl=None, should_skip_smart_sort=None):
        self.uid = uid if uid else title
        self.title = title
        self.arg = arg
        self.subtitle = subtitle
        self.autocomplete = autocomplete 
        self.valid = valid
        self.mods = mods if mods else {}
        self.text = text
        self.icon_path = icon_path
        self.type = type
        self.quicklookurl = quicklookurl
        self.should_skip_smart_sort = should_skip_smart_sort

    def to_dict(self):
        item_dict = {
            "uid": self.uid if self.should_skip_smart_sort is None or self.should_skip_smart_sort is False else None,
            "title": self.title,
            "arg": self.arg,
            "subtitle": self.subtitle,
            "autocomplete": f" {self.autocomplete}",
            "valid": self.valid,
            "type": self.type if self.type else "default",
            "quicklookurl": self.quicklookurl
        }
        if self.mods:
            item_dict["mods"] = {mod.key.value: mod.to_dict()[mod.key.value] for mod in self.mods if mod.key is not None}
        if self.text:
            item_dict["text"] = self.text.to_dict()
        if self.icon_path:
            item_dict["icon"] = {
                "path": self.icon_path
            }
        return {k: v for k, v in item_dict.items() if v is not None}


def generate_list_from_yaml(yaml_string):
    def entry_processor(entry):
        title = entry['title']
        url = entry['url']
        icon = entry.get('icon', None)

        return URLScheme(title=title, urlScheme=url, icon=icon)

    try:
        yaml_data = yaml.safe_load(yaml_string)
        return [entry_processor(entry) for entry in yaml_data]
    except yaml.YAMLError as e:
        # print(f"YAML error: {e}")
        return []
    except Exception as e:
        # print(f"An error occurred: {e}")
        return []





def parse_tags(input_tags):
    """Parses the YAML string into a dictionary."""
    try:
        return yaml.safe_load(input_tags)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return {}

def remove_urls(query):
    """Removes URLs from the query."""
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', query)

def get_matching_tags(query, tags_dict):
    """Finds the tags that match any of the keywords in the query."""
    query_lower = query.lower()
    matched_tags = []

    for tag, keywords in tags_dict.items():
        for keyword in keywords:
            # Match keywords as whole words or followed by punctuation

            # print("----")
            # print(keyword)
            # print(query_lower)
            word_pattern = rf'(^|\s|\b){re.escape(keyword)}(\b|\s|$)'
            if re.search(word_pattern, query_lower):
                matched_tags.append(tag)
                break

    return matched_tags




def process(query, shouldPrintOutput=True):
    input_url_scheme_list = os.getenv('input_url_scheme_list')
    input_tags = os.getenv('input_tags')

    url_items = generate_list_from_yaml(input_url_scheme_list)


    # Remove URLs from the query
    query_without_urls = remove_urls(query)

    # Parse the YAML into a dictionary
    tags_dict = parse_tags(input_tags)

    # Find the matching tags for the query
    matched_tags = get_matching_tags(query_without_urls, tags_dict)

    # Replace placeholders in the URL
    tags_string = ",".join(matched_tags)
    today_date = datetime.now().strftime("%Y-%m-%d")


    for item in url_items:
        item.url = item.urlScheme.replace("[title]", urllib.parse.quote(query)).replace("[tags]", urllib.parse.quote(tags_string)).replace("[today]", today_date)
        

    output = {"items": []}

    output['items'] += [ResultItem(title=item.title, arg=item.url, subtitle=item.url, icon_path=item.icon).to_dict() for item in url_items]

    output['items'] += [ResultItem(title='Tags found', arg="", subtitle="   |   ".join(matched_tags), icon_path="tag.png", valid=False).to_dict()]

    if shouldPrintOutput:
        sys.stdout.write(json.dumps(output))


if __name__ == "__main__":
    process(sys.argv[1])