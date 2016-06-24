#!/bin/sh

git filter-branch -f --env-filter '
export GIT_COMMITTER_NAME="BKTO"
export GIT_COMMITTER_EMAIL="hello@betterknowtheopposition.com"
export GIT_AUTHOR_NAME="BKTO"
export GIT_AUTHOR_EMAIL="hello@betterknowtheopposition.com"
' master

git push --force --tags origin 'refs/heads/*'
