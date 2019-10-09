docker images | grep -v REPOSITORY | awk '{printf $1; printf ":"; print $2}' | xargs -L1 docker pull
