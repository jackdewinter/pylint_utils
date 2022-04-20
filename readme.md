# PyLint Utilities (pylint_utils)

|   |   |
|---|---|
|Project|[![Version](https://img.shields.io/pypi/v/pylint_utils.svg)](https://pypi.org/project/pylint_utils)  [![Python Versions](https://img.shields.io/pypi/pyversions/pylint_utils.svg)](https://pypi.org/project/pylint_utils)  ![platforms](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)  [![License](https://img.shields.io/github/license/jackdewinter/pylint_utils.svg)](https://github.com/jackdewinter/pylint_utils/blob/master/LICENSE.txt)  [![GitHub top language](https://img.shields.io/github/languages/top/jackdewinter/pylint_utils)](https://github.com/jackdewinter/pylint_utils)|
|Quality|[![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/jackdewinter/pylint_utils/Main)](https://github.com/jackdewinter/pylint_utils/actions/workflows/main.yml)  [![Issues](https://img.shields.io/github/issues/jackdewinter/pylint_utils.svg)](https://github.com/jackdewinter/pylint_utils/issues)  [![codecov](https://codecov.io/gh/jackdewinter/pymarkdown/branch/main/graph/badge.svg?token=PD5TKS8NQQ)](https://codecov.io/gh/jackdewinter/pylint_utils)  [![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)  ![snyk](https://img.shields.io/snyk/vulnerabilities/github/jackdewinter/pylint_utils) |
|  |![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pylint_utils/black/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pylint_utils/flake8/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pylint_utils/pylint/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pylint_utils/mypy/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pylint_utils/pyroma/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pylint_utils/pre-commit/master)|
|Community|[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/jackdewinter/pylint_utils/graphs/commit-activity) [![Stars](https://img.shields.io/github/stars/jackdewinter/pylint_utils.svg)](https://github.com/jackdewinter/pylint_utils/stargazers)  [![Forks](https://img.shields.io/github/forks/jackdewinter/pylint_utils.svg)](https://github.com/jackdewinter/pylint_utils/network/members)  [![Contributors](https://img.shields.io/github/contributors/jackdewinter/pylint_utils.svg)](https://github.com/jackdewinter/pylint_utils/graphs/contributors)  [![Downloads](https://img.shields.io/pypi/dm/pylint_utils.svg)](https://pypistats.org/packages/pylint_utils)|
|Maintainers|[![LinkedIn](https://img.shields.io/badge/-LinkedIn-black.svg?logo=linkedin&colorB=555)](https://www.linkedin.com/in/jackdewinter/)|

## TL;DR

From my point of view, quality is not an absolute 0% or 100%.  For me, quality
is a series of qualitative measurements that occur in the range between those two
absolutes.  Given that viewpoint, I believe it logically follows that any qualitative
measurements that "quality percentage" have (for the most part) similar ranges for
their values. Part of those quality measurements for Python projects are the number
of suppressions used to suppress PyLint warnings.  Therefore, it follows that it
is important to curate, track, and measure PyLint suppressions to contribute to
that qualitative measurement.

Therefore, this package provides a few utilities that:

- verify that PyLint suppression enables and disables are balanced, existing
  in pairs
- create a report on the suppressions used in a given set of files
- looks for PyLint suppression that are no longer used

The intent of these utilities is to properly manage any PyLint suppressions used
within a project, enabling other applications to use the summary information to
create a useful quality measurement from that report.

## Getting Started

In basic mode, this package serves to check whether any PyLint suppressions present
in the scanned code follow good suppression practices.  Specifically, those good
practices are:

- with few exceptions*, any warning that is suppressed using `disabled` is turned
  back on again using `enabled`
- a warning that is already disabled cannot be disabled again
- a warning that is already enabled cannot be enabled again

As the asterisk notes, there are exceptions.  The only current exception is
a file scoped  `disable=too-many-lines` suppression.  This suppression is typically
added at the start of a Python file, and must not be matched with an `enabled`
suppression to have the desired effect.  Therefore, there is special handling in
place to not check for a matching `enabled` suppression in that one case.

Checking whether a set of Python files adheres to these practices is simple.
For example, to check this project's `pylint_utils` module from the root of the
project, invoke:

```sh
pylint_utils --verbose pylint_utils
```

While the `--verbose` flag is not required, it will help to show the files that
are being scanned as the scanner is working through files.  If the files are following
best practices, the utility will output a set of lines like this:

```text
Scanning file: pylint_utils/main.py
  File contains 0 scan errors.
```

for each file that is scanned.  While the `pylint_utils/main.py` module itself is
kept clean, if there were any violations of the best practices, a line similar to
one of the following lines would be output:

```text
pylint_utils/main.py(13): Pylint error 'too-many-arguments' was disabled, but not re-enabled.
pylint_utils/main.py(12): Pylint error 'too-many-arguments' was already disabled.
pylint_utils/main.py(10): Pylint error 'too-many-arguments' was not disabled, so enable is ignored.
```

## Advanced Features

Before describing these other features, it is important to note that the check to
ensure that suppression are following good practices always happen.  However, once
those checks have completed, either one of the actions in the following sections
may performed after those checks.

### Reporting

To aid in coming up with a quality metric based on the number of PyLint suppressions
in a given set of files, a report can be generated of the used supressions.  This
reporting is initiated using the `--report` or `-r` command line argument, followed
by the name of the file to write the report to.  An example of such a command line
would be:

```sh
pylint_utils --report report-dir project-dir
```

The resultant report is in the JSON format, and looks something like this mocked
up report file:

```json
{
    "disables-by-file": {
        "pymarkdown/__init__.py": {},
        "pymarkdown/__main__.py": {},
        "pymarkdown/main.py": {
            "broad-except": 2
        },
        "pymarkdown/version.py": {}
    },
    "disables-by-name": {
        "broad-except": 2,
    }
}
```

In the report file, there are two sections: the `disables-by-name` section and the
`disables-by-file` section.  As its name suggests, the `disables-by-name` section
provides an accounting of the suppressed warnings based on the name of the warning.
To provide more indepth information, the `disables-by-file` section provides an
accouting of those same warnings, but breaking down those warnings by the files
in which they were found in.

### Finding Unused Suppressions

As software project usually evolve, there is a need to check to see if a suppression
that was once needed still requires suppression.  This often happens when one or
more modules or functions are refactored, breaking them up into small pieces.
What may have been one function with `too-many-branches` can now become two functions,
each with a healthy number of branches.

To scan for unused suppressions, either of the `--scan` argument or the `-s` argument
is used as a flag to turn the scanning on.
In cases where a configuration file is used with PyLint to modify the behavior of
PyLint, that configuration file needs to be passed to PyLint_Utils to ensure that
the scanner and PyLint will use the same configuration.  To do that, simply
add `--config {file}` to the command line, where `{file}` is the name of the
configuration file.  As an example, in the PyLint_Utils package itself, the
configuration for PyLint is in the `setup.cfg` file.  Therefore, `--config setup.cfg`
is added to the command line.

That is where the fun begins.
To properly determine if suppressions in each file are still
required, each file must properly scan with PyLint before the unused suppression
check can continue.  That "feature" is part of the design of this package, used
to keep the complexity at manageable levels.  To that end, if any unsuppressed
warnings are found, then text similar to the following will appear:

```text
Verifying {file} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: missing-function-docstring, missing-module-docstring, too-many-arguments, trailing-newlines
  Fix all errors before scanning again.
```

where `{file}` is the name of the file.

When the files have been fixed to include no unsuppressed warnings, the pacakge
will then proceed to look at each file to determine if any warnings are no longer
needed.  To achieve parity with PyLint's handling of warnings, PyLint itself is
used as the final arbiter of whether any warnings is still required.  The tradeoff
is that it takes time to spin up PyLint, ask it to scan a file, and to then wait
for it to close properly.

However, when that process finishes for each file, one of two outcomes is possible.
In the positive case, if no unused suppressions are found the following test will
appear:

```text
No unused PyLint suppressions found.
```

Otherwise, some form of the following text will appear:

```text
1 unused PyLint suppressions found.
{file}:6: Unused suppression: too-many-branches
```

with the number of unused suppression listed, followed by the file and line number
for each unused suppression, and which suppression is no longer needed.

## Future Goals

The 0.5.0 releases are to get this project on the board.
Once that is done, going to give this project time to mature and get battle tested.

## When Did Things Change?

The changelog for this project is maintained [at this location](/changelog.md).

## Still Have Questions?

If you still have questions, please consult our [Frequently Asked Questions](/docs/faq.md) document.

## Contact Information

If you would like to report an issue with the tool or the documentation, please file an issue [using GitHub](https://github.com/jackdewinter/pylint_utils/issues).

If you would like to us to implement a feature that you believe is important, please file an issue [using GitHub](https://github.com/jackdewinter/pylint_utils/issues) that includes what you want to add, why you want to add it, and why it is important.
Please note that the issue will usually be the start of a conversation and be ready for more questions.

If you would like to contribute to the project in a more substantial manner, please contact me at `jack.de.winter` at `outlook.com`.
