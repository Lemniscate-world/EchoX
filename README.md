# Echo - Intelligent Spaced Repetition for Obsidian

Echo is a smart spaced repetition system designed for Obsidian vaults, combining traditional SRS algorithms with graph centrality to prioritize learning based on note importance.

## Features

- **Custom SRS Algorithm**: Enhanced SM-2 with confidence scoring for better retention
- **Graph Centrality**: Uses PageRank to prioritize reviews of high-importance notes (those linked by many others)
- **Obsidian Integration**: Designed for note-based learning with block-level tracking
- **REST API**: FastAPI backend for easy integration
- **SQLite Storage**: Lightweight, local database

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Lemniscate-world/Echo.git  
cd echo
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn
```

### Running the Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Check server status

### Memory Management
- `POST /memory` - Add or update a memory item
  ```json
  {
    "id": "unique-id",
    "source": "note content",
    "note_path": "MyNote.md",
    "block_ref": "block-id"
  }
  ```

### Reviews
- `GET /reviews/today` - Get items due for review today (ordered by centrality)
- `POST /review` - Submit review feedback
  ```json
  {
    "id": "item-id",
    "feedback": "FORGOT" | "FUZZY" | "MASTERED"
  }
  ```

## SRS Algorithm

Echo uses a custom spaced repetition algorithm with:
- **Ease Factor**: Starts at 2.5, adjusts based on performance
- **Confidence**: 0.2-1.0 range for retention confidence
- **Intervals**: Exponential growth for mastered items
- **Graph Priority**: High-centrality notes reviewed first

## Testing

Run the test suite:
```bash
python -c "from tests.test_simulation import test_echo_30_days_simulation; test_echo_30_days_simulation(); print('All tests passed')"
```

## Architecture

- `app.py`: FastAPI application and endpoints
- `engine.py`: SRS algorithm implementation
- `graph.py`: Graph centrality computation (PageRank)
- `models.py`: Data models (MemoryItem, Feedback)
- `db.py`: Database connection and schema
- `tests/`: Unit tests

## Roadmap

- [ ] Obsidian plugin integration
- [ ] Mobile support via webhooks
- [ ] Advanced analytics dashboard
- [ ] Multi-vault support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Portfolio

Visit [Echo Portfolio](https://v0-echoandrecall.vercel.app/) for more information.
