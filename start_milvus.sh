# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
        echo "Trapped CTRL-C, exiting ..."
	exit 0
}
if [ -z "$MILVUS_DATA" ]; then
  MILVUS_DATA=/data/milvus
fi
if [ ! -d $MILVUS_DATA ]; then
  mkdir -p $MILVUS_DATA
fi
if [ -d $MILVUS_DATA/configs ]; then
  rm -rf $MILVUS_DATA/configs
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

exec $MILVUS_EXEC --system-log debug --log-stdout true --data $MILVUS_DATA
