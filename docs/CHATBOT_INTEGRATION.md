# Gemini Chatbot Integration

This document explains how to set up and use the Gemini-powered chatbot integration in the Zyra Vision Shop application.

## Overview

The chatbot integration uses Google's Gemini API to provide an AI-powered shopping assistant that can:
- Help users find products
- Answer questions about shopping
- Provide personalized recommendations
- Suggest relevant categories and products

## Setup Instructions

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key for the next step

### 2. Configure Backend

1. **Add API Key to Environment**:
   ```bash
   # Copy the example environment file
   cp backend/env.example backend/.env
   
   # Edit the .env file and add your Gemini API key
   GEMINI_API_KEY=your-actual-gemini-api-key-here
   ```

2. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the Backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8005
   ```

### 3. Configure Frontend

1. **Start the Frontend**:
   ```bash
   npm run dev
   ```

2. **Verify Environment Variables**:
   Make sure your `.env.development` file contains:
   ```bash
   VITE_API_BASE_URL=http://localhost:8005
   ```

## Testing the Integration

### Automated Testing

Run the test script to verify everything is working:

```bash
python test_chatbot_integration.py
```

This will test:
- Backend connectivity
- Gemini API health check
- Chat functionality

### Manual Testing

1. Open your application in the browser
2. Click the chat button (💬) in the bottom-right corner
3. Send a test message like "Hello, can you help me find a laptop?"
4. Verify you get a response from Gemini

## API Endpoints

### Health Check
```
GET /api/chatbot/health
```
Returns the status of the Gemini API connection.

### Chat
```
POST /api/chatbot/chat
```
Send messages to the chatbot and receive AI responses.

**Request Body**:
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help you?"}
  ],
  "user_id": "optional-user-id"
}
```

**Response**:
```json
{
  "message": "AI response text",
  "suggestions": ["Browse Electronics", "Check New Arrivals"]
}
```

## Features

### Frontend Features
- **Real-time Chat**: Send messages and receive responses instantly
- **Loading States**: Visual feedback while waiting for responses
- **Health Status**: Shows if Gemini API is accessible (🟢/🔴)
- **Error Handling**: Graceful fallback when API is unavailable
- **User Context**: Personalized responses based on user's browsing history
- **Suggestions**: AI-generated product suggestions

### Backend Features
- **Context Awareness**: Uses user's recent interactions for better responses
- **Product Integration**: Can reference actual products from the database
- **Error Handling**: Robust error handling and logging
- **Rate Limiting**: Built-in protection against abuse
- **Health Monitoring**: Endpoint to check API status

## Configuration Options

### Environment Variables

**Backend (.env)**:
```bash
GEMINI_API_KEY=your-gemini-api-key
```

**Frontend (.env.development)**:
```bash
VITE_API_BASE_URL=http://localhost:8005
```

### Customization

You can customize the chatbot behavior by modifying:

1. **System Prompt** (`backend/app/api/chatbot.py`):
   - Change the assistant's personality
   - Modify response length limits
   - Add specific instructions

2. **UI Components** (`src/components/ChatBot.tsx`):
   - Modify the chat interface
   - Change loading messages
   - Update styling

3. **Service Layer** (`src/services/chatbotService.ts`):
   - Add retry logic
   - Implement caching
   - Add analytics

## Troubleshooting

### Common Issues

1. **"Gemini API key not configured"**
   - Make sure `GEMINI_API_KEY` is set in your backend `.env` file
   - Restart the backend server after adding the key

2. **"Failed to get response from chatbot"**
   - Check if your Gemini API key is valid
   - Verify you have API quota remaining
   - Check backend logs for detailed error messages

3. **Frontend can't connect to backend**
   - Ensure backend is running on port 8005
   - Check `VITE_API_BASE_URL` in your frontend environment
   - Verify CORS settings in backend

4. **Health check shows red status (🔴)**
   - Check your internet connection
   - Verify Gemini API key is correct
   - Check if Google AI services are available

### Debug Mode

Enable debug logging by setting `DEBUG=true` in your backend `.env` file. This will show detailed logs including:
- API requests and responses
- Error details
- Performance metrics

## Security Considerations

1. **API Key Protection**:
   - Never commit API keys to version control
   - Use environment variables for all secrets
   - Rotate keys regularly

2. **Input Validation**:
   - All user inputs are validated and sanitized
   - Rate limiting prevents abuse
   - Conversation history is limited

3. **Data Privacy**:
   - User conversations are not stored permanently
   - Only recent interaction context is used
   - No personal data is sent to Gemini

## Performance Optimization

1. **Caching**: Consider implementing response caching for common queries
2. **Rate Limiting**: Implement user-based rate limiting
3. **Async Processing**: Use background tasks for heavy operations
4. **Monitoring**: Add metrics and monitoring for API usage

## Future Enhancements

Potential improvements:
- **Voice Input**: Add speech-to-text capabilities
- **Rich Media**: Support for images and product links
- **Order Tracking**: Integration with order management
- **Multi-language**: Support for multiple languages
- **Analytics**: Track chatbot usage and effectiveness

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend logs for error details
3. Test with the provided test script
4. Verify your Gemini API key and quota

For additional help, refer to:
- [Google AI Studio Documentation](https://ai.google.dev/docs)
- [Gemini API Reference](https://ai.google.dev/api/rest)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
