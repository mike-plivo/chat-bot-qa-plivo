case "$ENV" in
	"dev" | "development")
		echo "Running Development Mode"
		bash
	;;
	"ingest")
		echo "Running Ingestion Script"
		python3 ./ingest.py
	;;
	"*" | "prod" | "production")
		echo "Running Production Server"
		gunicorn -c ./gunicorn.conf.py app:app
	;;
esac
