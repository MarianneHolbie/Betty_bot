import { type IMessage } from "~/interfaces/iMessage";

export const useIsChatting = () => useState("isChatting", () => false);
export const useMessages = () => useState<IMessage[]>("messages", () => []);