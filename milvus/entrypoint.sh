# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
        echo "Trapped CTRL-C, exiting ..."
	exit 0
}

if [ ! -d /data/milvus ]; then
  mkdir -p /data/milvus
fi
if [ -d /data/milvus/configs ]; then
  rm -rf /data/milvus/configs
fi

MILVUS_EXEC=$(which milvus-server)
if [ $? -ne 0 ]; then
  echo "milvus-server not found"
  exit 1
fi
if [ -z "$MILVUS_EXEC" ]; then
  echo "milvus-server not found"
  exit 1
fi

$MILVUS_EXEC --system-log debug --log-stdout true --data $DATA_DIR
