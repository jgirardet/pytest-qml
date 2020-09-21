import re
from pathlib import Path

from termcolor import colored

file_line_number = re.compile(r".+\@.+/(?P<module_name>.+\.qml):(?P<line_nb>\d+)")


def get_error_line_in_stack(module_name: str, stack: str):
    for line in file_line_number.finditer(stack):
        group = line.groupdict()
        try:
            if group["module_name"] == module_name:
                return int(group["line_nb"])
        except KeyError:
            continue


def pick_error_context(module: str, test: str, line_no: int, err_type: str, msg: str):
    file = Path(module).read_text()
    res = []
    open_brace_count = 0
    close_brace_count = 0
    line_index = None
    error_line_found = False
    c_index = lambda x: colored(x, "blue")
    c_fn = lambda x: colored(x, "yellow")
    for n, line in enumerate(file.splitlines(keepends=False), start=1):
        if re.match(rf"\s*function {test}\(", line):
            if line_index is None:
                line_index = n
        if line_index is not None:
            open_brace_count += line.count("{")
            close_brace_count += line.count("}")
            if open_brace_count == close_brace_count and open_brace_count > 0:
                res.append(c_index(f"{n}: ") + c_fn(line))
                break
        if line_index is not None:
            if n == line_no:
                res.append(
                    c_index(f"{n}: ")
                    + line
                    + colored(f" {err_type} ===>  {msg}", "red")
                )
                error_line_found = True
            elif n == line_index:
                res.append(c_index(f"{n}: ") + c_fn(line))
            else:
                res.append(c_index(f"{n}: ") + line)
    if not error_line_found:
        res.append(colored(f" {err_type} ===>  {msg}", "red"))
    return res


def format_stack_trace(stack: str, test_name: str, cut=False):
    # print(stack)
    res = []
    for line in stack.splitlines(keepends=False):
        # print(stack)
        fn, path, lineno = re.search(r"(.+)\@(.+\.(?:qml|mjs))?\:(.+)", line).groups()
        # breakpoint()
        string = f"In file {colored(path,'green')} at line {colored(lineno, 'cyan')} in function {colored(fn, 'cyan')}"
        if "utils.mjs" in line and "constructor" in line and cut:
            pass
        else:
            res.append(colored(string, "white"))
        if cut and fn == test_name:
            break
    return res


# def _createReport(self):
#     text_report = []
#     total_columns = shutil.get_terminal_size().columns
#     for module, tests in self.results.items():
#         for test, error in tests.items():
#             self.test_count += 1
#             if error:
#                 text_report.append(
#                     (
#                         f" {module}:{test}".center(total_columns, "-"),
#                         "blue",
#                         ["bold"],
#                     )
#                 )
#                 self.fail_count += 1
#
#                 line = self._getErrorLineInStack(module, error["stack"])
#                 context = self._pick_error_context(module, test, line, error["message"])
#                 # text_report.append(f"{error['message']}")
#                 text_report.extend(context)
#                 text_report.extend(
#                     self._format_stack_trace(error["stack"], test, cut=True)
#                 )
#                 text_report.append(("", "white"))
#     return text_report

#

#
#

#
#
# def _show_report(self, report: List[str]):
#     # print(shutil.get_terminal_size())
#     total_columns = shutil.get_terminal_size().columns
#     report_color = "red" if self.fail_count else "green"
#     cprint(
#         " Tests Report ".center(total_columns, "="),
#         report_color,
#         attrs=["bold"],
#     )
#     print("\n")
#     for line in report:
#         cprint(line[0], line[1])
#
#     failed = f"{self.fail_count} failed," if self.fail_count else ""
#     passed = f"{self.test_count - self.fail_count} passed"
#     cprint(
#         f" QML Tests: {failed}{passed} ".center(total_columns, "="),
#         report_color,
#         attrs=["bold"],
#     )
#
