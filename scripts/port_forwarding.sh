#!/usr/bin/env bash
# Helper for forwarding test DB connection
# on $LOCAL_PG_ADDR:$LOCAL_PG_PORT (localhost:15501 by default)
# to
# REMOTE_FWD_ADDR ("138.68.76.50" - test db by default)
# (open key should be added for user pjfwd on $REMOTE_FWD_ADDR host)
#
# based on https://unix.stackexchange.com/questions/100859/ssh-tunnel-without-shell-on-ssh-server
#set -x

# Example usage:
# ./port_forwarding.sh \
#   --name=dl1-docker-forwarding \
#   --local-addr=localhost \
#   --local-port=8991 \
#   --remote-addr=localhost \
#   --remote-port=9991 \
#   --remote-ssh=dl1 \
#   --ssh-user=n01z3 \
#   --command=start
#
# ./port_forwarding.sh \
#   --n=dl2-docker-forwarding \
#   -la=localhost \
#   -lp=8992 \
#   -ra=localhost \
#   -rp=9992 \
#   -rs=dl2 \
#   -su=n01z3 \
#   -c=stop


set -e

# Args parsing
for i in "$@"; do
    case "$1" in
        -n=*|--name=*)
            FWD_NAME="${i#*=}"
            shift
        ;;
        -la=*|--local-addr=*)
            FWD_LOCAL_ADDR="${i#*=}"
            shift
        ;;
        -lp=*|--local-port=*)
            FWD_LOCAL_PORT="${i#*=}"
            shift
        ;;
        -ra=*|--remote-addr=*)
            FWD_REMOTE_ADDR="${i#*=}"
            shift
        ;;
        -rp=*|--remote-port=*)
            FWD_REMOTE_PORT="${i#*=}"
            shift
        ;;
        -rs=*|--remote-ssh=*)
            FWD_REMOTE_SSH="${i#*=}"
            shift
        ;;
        -su=*|--ssh-user=*)
            FWD_SSH_USER="${i#*=}"
            shift
        ;;
        -c=*|--command=*)
            CMD="${i#*=}"
            shift
        ;;
        *)
            echo "Invalid option $i"
            exit 1
    esac
done

FWD_SOCK_FILE=${FWD_SOCK_FILE:-"/tmp/pj-ssh-$FWD_NAME-fwd"}
FWD_LOCAL=$FWD_LOCAL_ADDR:$FWD_LOCAL_PORT
FWD_REMOTE=$FWD_REMOTE_ADDR:$FWD_REMOTE_PORT
echo "Tunneled $FWD_LOCAL <= $FWD_REMOTE (on $FWD_SSH_USER@$FWD_REMOTE_SSH)"


case $CMD in
    start)
        echo "Start forwarding ${FWD_NAME}: $FWD_REMOTE on $FWD_LOCAL"
        ssh -f -N -M -S "${FWD_SOCK_FILE}" -L "$FWD_LOCAL:$FWD_REMOTE" "${FWD_SSH_USER}@${FWD_REMOTE_SSH}"
        ;;
    stop)
        echo "Stop forwarding ($FWD_NAME) on :$FWD_LOCAL"
        ssh -S "${FWD_SOCK_FILE}" -O exit "${FWD_SSH_USER}@${FWD_REMOTE_SSH}"
        ;;
    *)
        echo "Error: unknown command $CMD"
        echo "Usage: ./bin/fwd.sh [start|stop]"
        exit 1
        ;;
esac

# TIPS ON ERRORS:
#
# Error: «channel_setup_fwd_listener_tcpip: cannot listen to port: »
# Sulution:
# lsof -i :$LOCAL_PORT
# kill $PID