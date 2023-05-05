# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
        echo "Trapped CTRL-C, exiting ..."
	exit 0
}

redis-server --daemonize yes
rqworker --verbose &
gunicorn -c ./gunicorn.conf.py app:app
