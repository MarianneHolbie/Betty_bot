import { client } from "./openai";

export const getLatestMessages = async (threadID: string, runID: string) => {
    let run = client.beta.threads.runs.retrieve(threadID, runID);

    while (run.status != "completed") {
        new Promise((resolve) => setTimeout(resolve, 500));

        run = client.beta.threads.runs.retrieve(threadID, runID);
    }

    return await client.beta.threads.messages.list(threadID);
};