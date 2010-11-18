function roll_die() {

  # capture parameter
  declare -i DIE_SIDES=$1

  # check for die sides
  if [ ! $DIE_SIDES -gt 0 ]; then
    # default to 6
    DIE_SIDES=6
  fi
  
  # echo to screen
  echo $[ ( $RANDOM % $DIE_SIDES )  + 1 ]

}


