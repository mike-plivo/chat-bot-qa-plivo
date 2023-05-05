# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
        echo "Trapped CTRL-C, exiting ..."
	exit 0
}

case $1 in
	flymode)
		echo "Starting ingest container in interactive mode ..."
		echo "To stop the container, press CTRL-C."
		echo "In another terminal, start ingestion by typing 'python3 ingest.py' in the /app directory."
		echo ""
		while true; do 
			sleep 60
			echo "Still running ..."
	       	done
	;;
	*)
		echo "Starting ingest container in auto mode ..."
		echo "To stop the container, press CTRL-C."
		echo ""
		cd /app && python3 ./ingest.py
	;;
esac
