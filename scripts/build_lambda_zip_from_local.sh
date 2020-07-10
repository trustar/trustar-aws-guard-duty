# Run this from your local laptop.
# It will:
#  -SSH into the EC2 instance.
#  -clone the repo.
#  -pull & fetch all.
#  -jump to the EN-422/update_dependencies branch.
#  -build the .zip
#  -terminate the SSH.
#  -scp the .zip from EC2 to local.