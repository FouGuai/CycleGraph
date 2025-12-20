#!/bin/bash

trap 'kill 0' SIGINT SIGTERM EXIT

python -m server.main & cd frontend && npm run dev & wait
