import { getLatestMessages } from "../utils/get_message";

export default defineEventHandler(async (event) => {
    const threadID = getCookie(event, "thread-id");
    const runID = getCookie(event, "run-id");

    console.log('thread-id:', threadID);
    console.log('run-id:', runID);

    if (!threadID || !runID) {
        throw createError({
            statusCode: 400,
            statusMessage: 'Missing thread-id or run-id cookie',
        });
    }

    try {
        return await getLatestMessages(threadID, runID);
    } catch (error) {
        console.error('Error fetching messages:', error);
        throw createError({
            statusCode: 500,
            statusMessage: 'Failed to fetch messages',
        });
    }
});