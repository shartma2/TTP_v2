export function renderResult(result: any): string {
  if (!result) return "No result.";
  if (result.response) {
    if (typeof result.response === "string") return result.response;
    return JSON.stringify(result.response, null, 2);
  }
  return JSON.stringify(result, null, 2);
};