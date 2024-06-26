import axios from 'axios';

interface ThreadResponse {
    thread_id: string;
    run_id: string;
}

export default defineEventHandler(async (event) => {
    // Vérifier si la méthode est POST
  if (event.node.req.method !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed',
    });
  }

    const body = await readBody(event);
    const customer = body.customer;

    if (!customer) {
        throw createError({
            statusCode: 400,
            statusMessage: 'Missing customer in request body',
        });
    }

    try {
        const response = await axios.post('http://localhost:3000/start_thread', {
            customer,
        });

        const { thread_id, run_id } = response.data;

        // Set cookies
        setCookie(event, 'thread-id', thread_id, {
            httpOnly: true,
            path: '/',
            maxAge: 60 * 60 * 24 // 1 day
        });
        setCookie(event, 'run-id', run_id, {
            httpOnly: true,
            path: '/',
            maxAge: 60 * 60 * 24 // 1 day
        });

        return {
            thread: thread_id,
            run: run_id,
        };
    } catch (error) {
        console.error('Error creating thread:', error);
        throw createError({
            statusCode: 500,
            statusMessage: 'Failed to create thread',
        });
    }
});
