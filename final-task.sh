#!/usr/bin/env bash

NOTIFY="${bamboo_build_working_directory}/notify-mail"
COMMENT="${bamboo_build_working_directory}/issue-comment"
ISSUE_KEY=${bamboo_planRepository_branchName}

DEVENG_TEXT="Если проблема не в коде - написать коммент с упоминанием @jira-deveng-notify, либо на почту deveng@marathonbet.ru, либо в чат sp_build."

BUILD_FAIL_TEXT="Переоткрыто в связи с неудачной сборкой, необходимо:
1) Посмотреть в логи сборки ${bamboo_resultsUrl}
2) Внести необходимые правки, добившись сборки в ветке
3) Перевести таску в In Review/Resolved

$DEVENG_TEXT"

REBASE_FAIL_TEXT="Переоткрыто в связи с необходимостью ребэйза, необходимо:
1) Посмотреть в логи сборки ${bamboo_resultsUrl}
2) Произвести ребэйз и внести необходимые правки, добившись сборки в ветке
3) Перевести таску в In Review/Resolved

"

BUILD_AND_REBASE_FAIL_TEXT="Переоткрыто в связи с неудачной сборкой после ребэйза, необходимо:
1) Посмотреть в логи сборки ${bamboo_resultsUrl}
2) Произвести ребэйз и внести необходимые правки, добившись сборки в ветке
3) Перевести таску в In Review/Resolved

$DEVENG_TEXT"

if [ "${bamboo_inject_git_rebase}" = "fail" ]; then
    echo "Rebase fail $ISSUE_KEY"
    echo "Sending e-mail notification"
    echo "From: deveng@marathonbet.ru" > $NOTIFY
    echo "Subject: [AUTO-REBASE] Rebase fail $ISSUE_KEY" >> $NOTIFY
    echo "" >> $NOTIFY
    echo "${bamboo_resultsUrl}" >> $NOTIFY
    echo "https://jira.mara.local/browse/$ISSUE_KEY" >> $NOTIFY
    echo "http://manticore.mara.local/workbench/merge_task_to_branch/task/$ISSUE_KEY" >> $NOTIFY
    git diff --name-status --diff-filter=U >> $NOTIFY
    sendmail deveng@marathonbet.ru < $NOTIFY
    echo "Reopenning and commenting task"
    echo "$REBASE_FAIL_TEXT" > $COMMENT
    echo "{noformat}" >> $COMMENT
    git diff --name-status --diff-filter=U >> $COMMENT
    echo "{noformat}" >> $COMMENT
    ${bamboo_build_working_directory}/jira-actions "${bamboo_jira_baseurl}" "${bamboo_jira_user}" "${bamboo_jira_password}" \
        "$ISSUE_KEY" "${bamboo_jira_transitionid}" "file://$COMMENT"

elif [ -z "${bamboo_inject_mvn_build}" ]; then
    echo "Build fail $ISSUE_KEY"
    echo "Sending e-mail notification"
    echo "From: deveng@marathonbet.ru" > $NOTIFY
    echo "Subject: [AUTO-REBASE] Build fail $ISSUE_KEY" >> $NOTIFY
    echo "" >> $NOTIFY
    echo "${bamboo_resultsUrl}" >> $NOTIFY
    echo "https://jira.mara.local/browse/$ISSUE_KEY" >> $NOTIFY
    echo "http://manticore.mara.local/workbench/merge_task_to_branch/task/$ISSUE_KEY" >> $NOTIFY
    sendmail deveng@marathonbet.ru < $NOTIFY
    if [ -z "${bamboo_reopenOnFail}" ]; then
        echo "Fail is permissible. Will not reopen task."
    else
        echo "Reopenning and commenting task"
        if [ "${bamboo_inject_git_rebase}" = "no-need" ]; then
          echo "$BUILD_FAIL_TEXT" > $COMMENT
        else
          echo "$BUILD_AND_REBASE_FAIL_TEXT" > $COMMENT
        fi
        ${bamboo_build_working_directory}/jira-actions "${bamboo_jira_baseurl}" "${bamboo_jira_user}" "${bamboo_jira_password}" \
        "$ISSUE_KEY" "${bamboo_jira_transitionid}" "file://$COMMENT"
    fi
fi