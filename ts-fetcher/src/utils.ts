export enum Message {
  Hello = "Hello World",
  Bye = "Goodbye World",
}

export const hello = (msg: Message) => console.log(msg);
