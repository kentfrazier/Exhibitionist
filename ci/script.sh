#!/bin/bash

echo "inside $0"

# condition script on envar
# if [ x"$ENVAR" == x"true" ]; then

#     exit
# fi

python setup.py test
