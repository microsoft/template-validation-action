line_delimiter = "\n"

details_help_link = "https://aka.ms/ai-template-standards"
azd_help_link = "https://aka.ms/ai-template-trouble-shooting"


class Signs:
    CHECK = "- [x]"
    BLOCK = "- [ ] :x:"
    WARNING = "- [ ] :warning:"


how_to_fix = "## <i>How to fix?</i>\n<b>The full Definition of Done of the AI-Gallery template and fix approached can be found [HERE]({detail_link}).</b>".format(
    detail_link=details_help_link
)


class ItemResultFormat:
    PASS = "{sign} <b>{{message}}</b>.".format(sign=Signs.CHECK)
    FAIL = "{{sign}} <b>{{message}}</b>. <a href={detail_link}>[How to fix?]</a>\n\n{{detail_messages}}\n".format(
        detail_link=details_help_link
    )
    AZD_FAIL = "{{sign}} <b>{{message}}</b>. <a href={azd_link}>[How to fix?]</a>\n\n{{detail_messages}}\n".format(
        azd_link=azd_help_link
    )
    DETAILS = "  <details>\n  <summary> Details </summary>\n\n  {message}\n\n</details>"
    SUBITEM = "  {sign} {message}"
