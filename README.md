# AutoTagger for Alfred

This Alfred 5 workflow let's you quickly add items to any app using a custom URL scheme while automatically generating tags based on your query. 

It features an inline YAML configuration for specifying tags and related terms, along with a customizable URL scheme using dynamic placeholders `[title]`, `[tags]`, and `[today]`, and is optimized for Sorted³ out of the box.

Tags are derived from the words in the query, with URLs being excluded. For usage examples, please refer to the unit tests in [tests.py](tests.py).