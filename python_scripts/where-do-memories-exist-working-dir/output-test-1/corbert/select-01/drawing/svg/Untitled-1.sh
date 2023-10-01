#!/bin/bash

# use sed on mac to replace all
# width="{width}" height="{height}"
# with
# width="420mm" height="297mm"

sed -i '' 's/width="{width}" height="{height}"/width="420mm" height="297mm"/g' *.svg

# use sed on mac to replace version="1.1">
# with
# version="1.1"> <g transform="scale(1.75)">
sed -i '' 's/version="1.1">/version="1.1"> <g transform="scale(1.75)">/g' *.svg

# and replace
# </svg>
# with
# </g> </svg>
sed -i '' 's/<\/svg>/<\/g> <\/svg>/g' *.svg

# pull dry_run from env or set to 0
dry_run=${dry_run:-0}

for svg in $(ls $PWD/*svg); do
  # echo "trace $svg"
  if [ $dry_run -eq 1 ]; then
    echo "axicli $svg --config /home/hcwiley/axidraw_conf.py"
  else
    axicli $svg --config /home/hcwiley/axidraw_conf.py
  fi

  espeak "ok, next drawing ya heard" -v "romanian"

  # wait for the keyboard to have the enter key pressed
  read -p "Press enter to continue"    
done
