case "$ENV" in
	"dev")
		echo "Running in Dev Mode"
		bash
	;;
	"ingest")
		echo "Running Ingestion Script"
		python3 ./ingest.py
	;;
	"*" | "prod")
		redis-server --daemonize yes
		rqworker &
		gunicorn -c ./gunicorn.conf.py app:app
	;;
esac
