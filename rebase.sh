#!/usr/bin/env bash

# Bamboo variable allowed.sources must contain all allowed sources
if ! [[ "${bamboo_allowed_sources}" == *"${bamboo_build_source}"* ]]; then
    echo "Build source ${bamboo_build_source} is not allowed."
    exit 0
fi
echo "Fetch origin from ${bamboo_repository_git_repositoryUrl}"
git remote set-url origin ${bamboo_repository_git_repositoryUrl}
git fetch
git show-ref origin/master

if ! git merge-base --is-ancestor origin/master origin/${bamboo_repository_git_branch}
then
    echo "REBASE NEEDED"
    if ! git rebase origin/master
    then
        echo "REBASE FAILED"
        echo "git_rebase=fail" >> ${bamboo_build_working_directory}/build-result.txt
        git diff --name-status --diff-filter=U
        exit 1
    else
        echo "REBASE SUCCESS"
        echo "git_rebase=success" >> ${bamboo_build_working_directory}/build-result.txt
    fi
else
    echo "REBASE NO NEEDED"
    echo "git_rebase=no-need" >> ${bamboo_build_working_directory}/build-result.txt
fi