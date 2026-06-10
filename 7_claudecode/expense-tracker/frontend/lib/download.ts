/** Trigger a client-side file download from a string payload. */
export function downloadFile(
  filename: string,
  content: string,
  mime = "text/csv;charset=utf-8"
): void {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
