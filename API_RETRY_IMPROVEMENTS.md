# API Retry Logic and Error Handling Improvements

## Overview
This document describes the improvements made to handle transient API errors (like 503 Service Unavailable) in the OCR-LAB application.

## Problem
The application was experiencing failures when external APIs (Google Gemini, OpenAI) returned transient errors such as:
- **503 Service Unavailable**: The service is temporarily overloaded or down for maintenance
- **502 Bad Gateway**: Invalid response from upstream server
- **500 Internal Server Error**: Server-side error
- **429 Too Many Requests**: Rate limiting

These errors were causing immediate failures without any retry attempts, resulting in lost processing time and user frustration.

## Solution

### 1. Automatic Retry with Exponential Backoff
Implemented a robust retry mechanism that automatically retries failed API requests with exponentially increasing wait times:

- **Gemini API**: Up to 5 retries with backoff times of 2s, 4s, 8s, 16s, 32s
- **OpenAI API**: Up to 5 retries with backoff times of 2s, 4s, 8s, 16s, 32s
- **Ollama (Local)**: Up to 3 retries with backoff times of 1s, 2s, 4s (shorter since it's local)

### 2. HTTP Session with Built-in Retry Logic
Created a reusable HTTP session using `urllib3.Retry` and `requests.adapters.HTTPAdapter`:

```python
def _create_retry_session(self, 
                          retries: int = 5,
                          backoff_factor: float = 1.0,
                          status_forcelist: tuple = (500, 502, 503, 504, 429)) -> requests.Session
```

This provides:
- Automatic connection retry on network failures
- Retry on specific HTTP status codes (500, 502, 503, 504, 429)
- Exponential backoff between retries
- Thread-safe session reuse

### 3. Enhanced Error Messages
Improved error reporting to show:
- Which attempt number is being made
- How long the system will wait before retrying
- Clear indication when all retries are exhausted

Example output:
```
⚠️ Gemini API error (attempt 1/5): 503 Server Error: Service Unavailable. Retrying in 2s...
⚠️ Gemini API error (attempt 2/5): 503 Server Error: Service Unavailable. Retrying in 4s...
```

### 4. Timeout Configuration
Added appropriate timeouts for each API:
- **External APIs (Gemini, OpenAI)**: 120 seconds (2 minutes)
- **Local Ollama**: 300 seconds (5 minutes) - longer due to local processing

### 5. Model Fetching Improvements
Enhanced the `get_openai_models()` and `get_gemini_models()` functions with retry logic to handle transient errors when fetching available models.

## Benefits

1. **Increased Reliability**: Transient errors are automatically handled without user intervention
2. **Better User Experience**: Users don't need to manually retry failed operations
3. **Cost Efficiency**: Reduces wasted API calls and processing time
4. **Graceful Degradation**: Clear error messages when all retries are exhausted
5. **Production Ready**: Follows best practices for API integration in production environments

## Technical Details

### Files Modified
- `src/ollama_ocr/ocr_processor.py`: Added retry logic to all API calls
- `src/ollama_ocr/app.py`: Added retry logic to model fetching functions

### New Dependencies
- `urllib3` (already included with `requests`)
- `requests.adapters.HTTPAdapter`
- `urllib3.util.retry.Retry`

### Configuration
All retry parameters are configurable but set to sensible defaults:
- **Max retries**: 5 for external APIs, 3 for local
- **Backoff factor**: 1.0 (doubles wait time each retry)
- **Status codes**: 500, 502, 503, 504, 429

## Usage

No changes are required to existing code. The retry logic is automatically applied to all API calls:

```python
# This will automatically retry on transient errors
processor = OCRProcessor(
    model_name="gemini-2.5-pro",
    api_provider="gemini",
    api_key="your-api-key"
)

result = processor.process_image("image.jpg")
```

## Testing Recommendations

1. **Test with intermittent network issues**: Simulate network failures to verify retry logic
2. **Test with rate limiting**: Send rapid requests to trigger 429 errors
3. **Test with service downtime**: Verify behavior when API is completely unavailable
4. **Monitor retry patterns**: Check logs to ensure exponential backoff is working correctly

## Future Enhancements

Potential improvements for future versions:
1. **Configurable retry parameters**: Allow users to customize retry behavior
2. **Circuit breaker pattern**: Temporarily stop retrying if API is consistently failing
3. **Metrics and monitoring**: Track retry rates and success/failure patterns
4. **Fallback providers**: Automatically switch to alternative API provider on failure
5. **Request queuing**: Queue failed requests for later retry instead of blocking

## Conclusion

These improvements significantly enhance the robustness of the OCR-LAB application when dealing with external API services. The automatic retry mechanism with exponential backoff is an industry-standard approach that balances reliability with responsible API usage.

