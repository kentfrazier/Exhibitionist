All contributions, bug reports, bug fixes, documentation improvments,
enhancements and ideas are welcome.

Please try and follow these guidelines, as this makes it easier to accept
your contribution or address the issue you're having. There a lot of points
below, just do the best you can.

- When submitting a bug report:
  - Please include a short, self-contained python snippet.
  - Specify the version used. (you can check `exhibitionist.__version__`).
  - Explain what the expected behavior was, and what you saw instead.

- When submitting a Pull Request
  - **Make sure the test suite passes* on all supported python versions.
    installing [tox](http://tox.testrun.org/) will allow you to do this easily.
    After installation, issuing the "tox" command in the root of your fork
    will automatically run the test suite in a seperate virtualenv for all
    supported versions.
  - [Travis-CI](http://travis-ci.org) is supported. Follow the [instructing](http://about.travis-ci.org/docs/user/getting-started/) to get Travis to automatically run the tests for your PR, and
    have the results shown on the github PR page. It should only take a couple of minutes.
  - **Don't** merge upstream into a branch you're going to submit as a PR.
    This can create all sorts of problems.
    That means "git merge upstream" is bad, use "git merge --rebase upstream"
    instead. When in doubt, just leave your PR branch as it is and don't merge at all.
  - Try and adhere to the style of commmit messages. a single line containing
    a short summary followed by a blank line followd by an optional longer summary.
    Short prefixes are used to denote the type pf change: "ENH: ", "TST:", "BUG:", "DOC:", "BLD"
    , "CLN".
    Check the output of "git log" for examples.
  - For extra brownie points, use "git rebase -i" to squash and reorder
    commits in your PR so that the history makes the most sense. Use your own
    judgment to decide what history needs to be preserved. Back-and-forth commits
    are frowned upon.
  - On the subject of [PEP8](http://www.python.org/dev/peps/pep-0008/): yes.
  - On the subject of massive PEP8 PRs touching everything: NO.

Thanks for caring.