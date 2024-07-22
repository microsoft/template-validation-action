line_delimiter = "\n"

details_help_link = "https://aka.ms/ai-template-standards"


class Signs:
    CHECK = ":heavy_check_mark:"
    BLOCK = ":x:"
    WARNING = ":warning:"


how_to_fix = "## <i>How to fix?</i>\n<b>The full Definition of Done of the AI-Gallery template and fix approached can be found [HERE]({detail_link}).</b>".format(
    detail_link=details_help_link)

final_result_format = "# AI Gallery Standard Validation: {{result}} \n{{message}}\n\n{end_message}".format(
    link=details_help_link, end_message=how_to_fix)


class ItemResultFormat:
    PASS = "<details><summary>{sign} <b>{{message}}</b>.</summary></details>".format(
        sign=Signs.CHECK)
    FAIL = "<details><summary>{sign} <b>{{message}}</b>. <a href={detail_link}>[How to fix?]</a></summary>\n\n{{detail_messages}}\n\n</details>".format(
        sign=Signs.BLOCK, detail_link=details_help_link)
    WARNING = "<details><summary>{sign} <b>{{message}}</b>. <a href={detail_link}>[How to fix?]</a></summary>\n\n{{detail_messages}}\n\n</details>".format(
        sign=Signs.WARNING, detail_link=details_help_link)