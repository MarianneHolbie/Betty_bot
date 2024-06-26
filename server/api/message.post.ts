import axios from 'axios';

interface MessageResponse {
    answer: string;
}

export default defineEventHandler(async (event) => {
    const threadID = getCookie(event, "thread-id");
    if (!threadID) {
        throw createError({
            statusCode: 400,
            statusMessage: 'Missing thread-id cookie',
        });
    }

    const body = await readBody(event);
    const message = body.message;

    if (!message) {
        throw createError({
            statusCode: 400,
            statusMessage: 'Missing message in request body',
        });
    }

    try {
        const response = await axios.post<MessageResponse>('http://localhost:8000/answer', {
            question: message,
        });

        return response.data;
    } catch (error) {
        console.error('Error posting message:', error);
        throw createError({
            statusCode: 500,
            statusMessage: 'Failed to process message',
        });
    }
});