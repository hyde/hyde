**tl;dr**  Good (code + tests + commit message) = Great Pull Request.

*********************************************************************

How do the pull requests get merged?
------------------------------------

The following points are considered as part of merging pull requests
after it is deemed necessary.

1.  Is there an issue tagged in the commit?
2.  Do the existing tests pass?
3.  Are there new tests added to verify any new functionality / issue?
4.  Is the authors list up to date?
5.  Is the changelog updated?
6.  Is the version updated?
7.  Does this require any changes to the documentation?

Guidelines
----------

If the following guidelines are observed as much as possible, it will
immensely help in verifying and merging the pull requests.

1.  One pull request = One feature or One bug.
2.  Always tag an issue in the commit. If an issue does not exist for
    a feature or a bug, please add one.
3.  Use topic / feature branches.
4.  Make sure a test exists to verify the committed code. A good way
    to think about it is: if these commits were reversed and only the
    test were added back in, it ought to fail.
5.  Make the `commit message`_ as verbose as possible.
6.  Add yourself to `Authors`_ list and update your contribution.
7.  Cross update `Changelog`_ list as well.
8.  If the change was complicated and resulted in a lot of commits,
    consider ``rebase -i`` to squash and/or rearrange them to make it
    easier to review.
9. Update the `Readme`_.


.. _commit message: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
.. _Changelog: CHANGELOG.rst
.. _Authors: AUTHORS.rst
.. _Readme: README.rst

