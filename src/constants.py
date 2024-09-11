line_delimiter = "\n"

details_help_link = "https://aka.ms/ai-template-standards"
azd_help_link = "https://aka.ms/ai-template-trouble-shooting"


class Signs:
    CHECK = "- [x]"
    BLOCK = "- [ ] :x:"
    WARNING = "- [ ] :warning:"


how_to_fix = "## <i>How to fix?</i>\n<b>The full Definition of Done of the AI-Gallery template and fix approached can be found [HERE]({detail_link}).</b>".format(
    detail_link=details_help_link)

final_result_format = "# AI Gallery Standard Validation: {{result}} \n{{message}}\n\n{end_message}".format(
    link=details_help_link, end_message=how_to_fix)


class ItemResultFormat:
    PASS = "{sign} <b>{{message}}</b>.".format(
        sign=Signs.CHECK)
    FAIL = "{sign} <b>{{message}}</b>. <a href={detail_link}>[How to fix?]</a>\n\n{{detail_messages}}\n".format(
        sign=Signs.BLOCK, detail_link=details_help_link)
    AZD_FAIL = "{sign} <b>{{message}}</b>. <a href={azd_link}>[How to fix?]</a>\n\n{{detail_messages}}\n".format(
        sign=Signs.BLOCK, azd_link=azd_help_link)
    WARNING = "{sign} <b>{{message}}</b>. <a href={detail_link}>[How to fix?]</a>\n\n{{detail_messages}}\n".format(
        sign=Signs.WARNING, detail_link=details_help_link)
    DETAILS = "  <details>\n  <summary> Details </summary>\n\n  {message}\n\n</details>"
    SUBITEM = "  {sign} {message}"