export function renderResult(result: any): string {
  if (!result) return "No result.";
  return JSON.stringify(result, null, 2);
};