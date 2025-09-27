run_backend:
	echo "Running the backend."
	uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

run_frontend:
	echo "Running the frontend."
	streamlit run frontend/app.py
