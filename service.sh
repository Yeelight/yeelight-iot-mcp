#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PID_FILE="$PROJECT_DIR/uvicorn.pid"
LOG_FILE="$PROJECT_DIR/server.log"

APP_NAME="streamable_http_app"
PORT="${YEELIGHT_IOT_MCP_PORT:-${IOT_MCP_PORT:-${APP_MCP_PORT:-9000}}}"
RUNTIME_ENV="${YEELIGHT_IOT_MCP_RUNTIME_ENV:-${IOT_MCP_RUNTIME_ENV:-${APP_MCP_RUNTIME_ENV:-prod}}}"
if [ -n "$YEELIGHT_IOT_MCP_BIND_HOST" ]; then
    HOST="$YEELIGHT_IOT_MCP_BIND_HOST"
elif [ -n "$IOT_MCP_BIND_HOST" ]; then
    HOST="$IOT_MCP_BIND_HOST"
elif [ -n "$APP_MCP_BIND_HOST" ]; then
    HOST="$APP_MCP_BIND_HOST"
elif [ "$RUNTIME_ENV" = "local" ] || [ "$RUNTIME_ENV" = "test" ]; then
    HOST="127.0.0.1"
else
    HOST="0.0.0.0"
fi
WORKERS="${YEELIGHT_IOT_MCP_WORKERS:-${IOT_MCP_WORKERS:-4}}"

start() {
    UVICORN_CMD="$VENV_DIR/bin/uvicorn main:$APP_NAME --host $HOST --port $PORT --workers $WORKERS"
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Service already running (PID $(cat $PID_FILE))"
        exit 1
    fi
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    $UVICORN_CMD
    # echo $! > "$PID_FILE"
    # echo "Service started (PID $(cat $PID_FILE)) on $APP_NAME at port $PORT"
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            kill TERM "$PID"
            echo "Service stopped"
        else
            echo "No running service found with PID $PID"
        fi
        rm -f "$PID_FILE"
    else
        echo "No PID file found. Service may not be running."
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo "Service is running (PID $PID)"
        else
            echo "PID file exists but process not running"
        fi
    else
        echo "Service is not running"
    fi
}

restart() {
    stop
    sleep 1
    start "$1"
}

case "$1" in
    start)
        start "$2"
        ;;
    stop)
        stop
        ;;
    restart)
        restart "$2"
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status} [streamable_http|sse]"
        exit 1
        ;;
esac
