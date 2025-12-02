# SOP: Sales Transcript Processing Workflow

**Goal**: Automate the ingestion, storage, and initial processing of sales call transcripts.

## Workflow Overview

1.  **Trigger**: Webhook receives JSON payload containing call data.
2.  **Storage**: Data is appended to a Google Sheet for raw record keeping.
3.  **Processing**: An AI Agent (LLM) analyzes the transcript to extract key insights.
4.  **Output**: A structured JSON object is prepared for downstream agents.

## Inputs

The Webhook expects a POST request with the following JSON structure:

```json
{
  "call_id": "12345",
  "timestamp": "2023-10-27T10:00:00Z",
  "customer_name": "Acme Corp",
  "transcript": "Speaker 1: Hello... Speaker 2: Hi..."
}
```

## Configuration Steps

1.  **Import Workflow**: Import `execution/n8n_sales_workflow.json` into your n8n instance.
2.  **Google Sheets**:
    *   Create a new Google Sheet.
    *   Add headers: `Timestamp`, `Call ID`, `Customer`, `Transcript`, `AI Summary`.
    *   Connect your Google account in n8n and select this sheet in the "Google Sheets" node.
3.  **AI Agent**:
    *   Configure the "AI Agent" node with your OpenAI (or other provider) API key.
    *   Adjust the system prompt if needed to extract specific information (e.g., budget, pain points).
4.  **Activate**: Toggle the workflow to "Active" in n8n.
5.  **Test**: Send a test payload to the Production Webhook URL.

## Outputs

The workflow outputs a JSON object available for the next step in the pipeline (or returned as a webhook response if configured):

```json
{
  "status": "success",
  "processed_data": {
    "summary": "...",
    "sentiment": "Positive",
    "action_items": ["Send proposal", "Schedule follow-up"]
  }
}
```

## Troubleshooting

-   **Webhook 404**: Ensure the workflow is Active.
-   **Google Sheets Error**: Check column header names match exactly.
-   **AI Error**: Check API quota and key validity.
