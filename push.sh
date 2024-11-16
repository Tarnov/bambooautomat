#!/usr/bin/env bash

git remote set-url origin ${bamboo_repository_git_repositoryUrl}
if [ "${bamboo_inject_git_rebase}" = "success" ]; then
    echo "Push rebased branch"
    git push origin ${bamboo_repository_git_branch} -f
else
    echo "Nothing to push."
    exit 0
fi