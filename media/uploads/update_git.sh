#! /bin/bash

for dir in /var/www/*
do
  if [ -d "$dir" ]
  then
    cd "$dir"
    if [ -f .git/project_identifier ]
    then
      project_name=$(cat .git/project_identifier)
    else
      project_name=$(git log 2>/dev/null|grep ^commit|tail -n 2|sha1sum|cut -d' ' -f 1|tee .git/project_identifier)
    fi
    if [ "$project_name" = "$1" ]
    then
      echo "updating " `pwd`
      . ~gavin/.bash/_git_exec_file_move.sh
      . ~gavin/.bash/gull.sh
      gull
      /var/www/correct
      ./fbmvc migrate latest
      exit 0
    fi
  fi
done
exit 1
