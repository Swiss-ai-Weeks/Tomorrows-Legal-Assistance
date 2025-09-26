# Swiss Legal Case Analysis Agent

A LangGraph-based ReAct agent for analyzing Swiss legal cases. This agent ingests case descriptions and provides comprehensive analysis including case classification, win likelihood estimation, and time/cost projections.

## Features

- **Case Classification**: Automatically categorizes cases into: Arbeitsrecht, Immobilienrecht, Strafverkehrsrecht, or Andere
- **Win Likelihood Analysis**: Uses RAG retrieval of Swiss law and historic cases to estimate success probability (1-100)
- **Time & Cost Estimation**: Provides realistic time estimates and cost breakdowns
- **ReAct Processing**: Step-by-step reasoning with tool usage for transparent decision making
- **Parallel Analysis**: Simultaneous processing of different analysis branches for efficiency

## Architecture

The agent follows a LangGraph-based workflow:

```
Input → Ingest → Categorize → [Win Likelihood Analysis | Time & Cost Analysis] → Aggregate → Output
```

### Nodes

1. **Ingest**: Normalizes input and initializes working memory
2. **Categorize**: Classifies cases using ML/business logic with user fallback  
3. **Win Likelihood**: ReAct analysis using Swiss law RAG and historic cases
4. **Time & Cost**: Parallel estimation using business logic tools
5. **Aggregate**: Validates and formats final JSON output

### Tools (Plug-and-Play)

- `rag_swiss_law()`: Retrieve relevant Swiss statutes and regulations
- `historic_cases()`: Find similar precedent cases with outcomes  
- `estimate_time()`: Calculate time estimates based on case complexity
- `estimate_cost()`: Generate cost breakdowns including fees and VAT
- `categorize_case()`: ML-powered case classification
- `ask_user()`: UI callback for missing information

## Usage

### Basic Usage

```python
from backend.agent import create_legal_agent, CaseInput

# Create the agent
agent = create_legal_agent(api_key="your-apertus-key")

# Prepare case input
case = CaseInput(
    text="I was terminated from my job without proper notice...",
    metadata={
        "language": "en",
        "court_level": "district", 
        "preferred_units": "months"
    }
)

# Run analysis
result = agent.invoke({"case_input": case})
print(result["result"])
```

### Convenience Function

```python
from backend.agent import run_case_analysis

result = run_case_analysis({
    "text": "Employment dispute case description...",
    "metadata": {"language": "de", "court_level": "cantonal"}
})

# Output format
{
    "likelihood_win": 75,
    "estimated_time": "6 months", 
    "estimated_cost": {
        "total_chf": 15000.0,
        "breakdown": {
            "lawyer_fees": 12000.0,
            "court_fees": 2000.0,
            "vat": 1000.0
        }
    }
}
```

## Installation & Dependencies

### Core Requirements

```bash
pip install langgraph langchain pydantic
```

### Additional Dependencies

The agent integrates with:
- **Apertus LLM**: Swiss AI model for legal reasoning
- **Swiss Law RAG**: Chroma + Gemini embeddings (implemented separately)
- **Historic Cases DB**: Case database with outcomes (implemented separately) 
- **Business Logic Tools**: Time/cost estimation services (implemented separately)

### Environment Setup

```bash
export API_KEY="your-apertus-api-key"
```

## Input Schema

```python
{
    "text": "string",  # Case description (required)
    "metadata": {     # Optional metadata
        "language": "de|fr|it|en",
        "preferred_units": "days|weeks|months",
        "court_level": "string",
        "judges_count": "number"
    }
}
```

## Output Schema

```python
{
    "likelihood_win": "int (1-100)",     # Win probability
    "estimated_time": "string",          # Human-readable duration
    "estimated_cost": "number|object"    # Cost in CHF or breakdown
}
```

## Testing

Run smoke tests:

```bash
python -m backend.agent.test_agent
```

Run with pytest:

```bash
pytest backend/agent/test_agent.py -v
```

## Configuration

### Policies & Prompts

Customize behavior via `backend/agent/policies.py`:

- ReAct system prompts for each node
- Tool call limits and constraints  
- Default values and thresholds
- Swiss legal domain knowledge

### Tool Implementation

Tools are currently stubs in `backend/agent/tools/`. Replace with real implementations:

```python
# backend/agent/tools/rag_swiss_law.py
def rag_swiss_law(query: str, top_k: int = 5):
    # Replace with real Chroma/embedding search
    return search_swiss_law_db(query, top_k)
```

## Development Status

- ✅ Core LangGraph workflow implemented
- ✅ Schema validation and type safety
- ✅ ReAct prompts and policies defined
- ✅ Smoke tests passing
- ⚠️ Tool implementations are stubs
- ⚠️ Requires LangGraph installation
- ⚠️ Needs API key for full testing

## Integration Notes

### RAG Team
- Implement `rag_swiss_law()` with Chroma vector store
- Use Gemini embeddings for Swiss law documents
- Return structured `Doc` objects

### Business Logic Team  
- Implement `estimate_time()` and `estimate_cost()` functions
- Accept structured `CaseFacts` input
- Return typed results per schema

### UI Team
- Implement `ask_user()` callback for missing information
- Handle user interaction flow for clarifications
- Parse and validate user responses

### Backend Integration
- Add agent endpoint to FastAPI routes
- Handle async execution and progress tracking
- Implement proper error handling and logging

## Example Cases

The agent handles various Swiss legal scenarios:

### Employment Law (Arbeitsrecht)
- Wrongful termination disputes
- Wage and overtime claims  
- Workplace discrimination
- Contract violations

### Real Estate Law (Immobilienrecht)
- Property purchase disputes
- Rental agreement conflicts
- Construction defects
- Zoning and planning issues

### Traffic Criminal Law (Strafverkehrsrecht)
- Traffic violations and fines
- License suspension cases
- Criminal traffic offenses
- Insurance disputes

### Other Legal Matters (Andere)
- Contract disputes
- Consumer protection
- Administrative law
- General civil litigation

## Performance Considerations

- **Tool Call Limits**: Max 6 tool calls per case to prevent excessive API usage
- **Parallel Processing**: Win likelihood and time/cost analysis run simultaneously  
- **Caching**: Consider caching RAG results for similar queries
- **Error Handling**: Graceful fallbacks when tools are unavailable

## Contributing

1. Follow existing code structure and patterns
2. Add type hints and docstrings
3. Update tests for new functionality  
4. Document any new tools or configurations
5. Ensure compliance with Swiss legal accuracy requirements