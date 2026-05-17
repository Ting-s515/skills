export function readBearerToken(headers: Record<string, string | undefined>) {
  const authorization = headers.authorization ?? headers.Authorization;
  if (!authorization?.startsWith("Bearer ")) {
    return null;
  }

  const token = authorization.slice("Bearer ".length).trim();
  return token.length > 0 ? token : null;
}
