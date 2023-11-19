import json
import pathlib

import jinja2
import termcolor

from importlib.resources import files


TEMPLATES = pathlib.Path(files("style50.renderer").joinpath("templates"))


def to_ansi(files, score, version):
        lines = [termcolor.colored("Results generated by style50 v{}".format(version), "white", attrs=["bold"])]

        # Use same header as more.
        header = termcolor.colored("{0}\n{{}}\n{0}".format(
            ":" * 14), "cyan") if len(files) > 1 else None

        for file in files:
            if header is not None:
                lines.append(header.format(file["name"]))

            try:
                error = file["error"]
            except KeyError:
                pass
            else:
                lines.append(termcolor.colored(error, "yellow"))
                continue

            if file["score"] != 1:
                lines.append("")
                lines.append(file["diff"])
                lines.append("")
                conjunction = "And"
            else:
                lines.append(termcolor.colored("Looks good!", "green"))
                conjunction = "But"

            if file["score"] != 1:
                for type, c in file["warn_chars"]:
                    color, verb = ("on_green", "insert") if type == "+" else ("on_red", "delete")
                    char = termcolor.colored(c, None, color)
                    lines.append(char +
                            termcolor.colored(" means that you should {} a {}."
                                .format(verb, "newline" if c == "\\n" else "tab"), "yellow"))

            if file["comments"]:
                lines.append(termcolor.colored("{} consider adding more comments!".format(conjunction), "yellow"))

            if (file["comments"] or file["warn_chars"]) and file["score"] != 1:
                lines.append("")
        return "\n".join(lines)


def to_ansi_score(files, score, version):
    lines = []
    for file in files:
        if file.get("error"):
            lines.append(termcolor.colored(file["error"], "yellow"))
    lines.append(str(score))
    return "\n".join(lines)


def to_json(files, score, version):
    return json.dumps({"files": files, "score": score, "version": version}, indent=4)


def to_html(files, score, version):
    with open(TEMPLATES / "results.html") as f:
        content = f.read()

    template = jinja2.Template(
        content, autoescape=jinja2.select_autoescape(enabled_extensions=("html",)))
    html = template.render(files=files, version=version)

    return html
