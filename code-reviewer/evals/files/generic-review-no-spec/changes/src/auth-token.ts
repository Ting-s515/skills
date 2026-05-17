export function readBearerToken(headers: Record<string, string | undefined>) {
  return headers.authorization!.replace("Bearer ", "");
}
