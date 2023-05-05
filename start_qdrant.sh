# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
        echo "Trapped CTRL-C, exiting ..."
	exit 0
}
if [ -z "$QDRANT_DATA" ]; then
  QDRANT_DATA=/data/qrant
fi
if [ ! -d $QDRANT_DATA ]; then
  mkdir -p $QDRANT_DATA
fi

QDRANT_EXEC=/qdrant/qdrant
if [ -z "$QDRANT_EXEC" ]; then
  echo "qdrant not found"
  exit 1
fi

exec $QDRANT_EXEC --config-path /app/qdrant.config.yml --disable-telemetry
